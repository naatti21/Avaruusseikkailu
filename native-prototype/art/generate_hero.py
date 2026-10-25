#!/usr/bin/env python3
"""Self-authored modular hard-surface station and courier. World units: metres.
Run with Blender: --background --python generate_hero.py -- --output ./assets
"""
import bpy
import math
import sys
import json
import numpy as np
from pathlib import Path
from mathutils import Vector, Matrix

argv = sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
if len(argv)!=2 or argv[0]!="--output":
    raise SystemExit("Expected -- --output DIR")
dest=Path(argv[1]).resolve()
dest.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)

def mat(name,rgb,metal=.65,rough=.39,emission=0):
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*rgb,1)
    m.use_nodes=True
    p=m.node_tree.nodes.get("Principled BSDF")
    p.inputs["Base Color"].default_value=(*rgb,1)
    p.inputs["Metallic"].default_value=metal
    p.inputs["Roughness"].default_value=rough
    if emission:
        if "Emission Color" in p.inputs:
            p.inputs["Emission Color"].default_value=(*rgb,1)
            p.inputs["Emission Strength"].default_value=emission
        elif "Emission" in p.inputs:
            p.inputs["Emission"].default_value=(*rgb,1)
    return m

hull=mat("01 titanium steel",(.19,.26,.32),.85,.33)
armor=mat("02 bluegrey ceramic armor",(.40,.49,.53),.62,.42)
shadow=mat("03 graphite recess",(.042,.065,.085),.56,.54)
copper=mat("04 bronze machinery",(.42,.28,.17),.70,.35)
cyan=mat("05 cyan nav emission",(.025,.78,.88),.1,.28,2)
amber=mat("06 amber utility emission",(1,.36,.07),.1,.25,1.5)
glass=mat("07 cockpit glass",(.04,.17,.24),.33,.11)
materials=[hull,armor,shadow,copper,cyan,amber,glass]
# Shared original 512² trim atlas: albedo + packed rough/metal + tangent normal.
N=512
y,x=np.mgrid[0:N,0:N];tile=(x//256)+2*(y//256)
colors=np.array([[.24,.31,.37],[.57,.61,.57],[.075,.105,.13],[.46,.28,.12]])
seam=((x%64)<2)|((y%96)<2)
rng=np.random.default_rng(2082)
noise=rng.uniform(-.025,.025,(N,N))
base=np.clip(colors[tile]*(1-.5*seam[...,None])+noise[...,None],0,1)
# Paint hazard strips into one atlas trim without external imagery.
hazard=(tile==3)&((y%128)<20)
base[hazard]=np.where((((x+y)//12)%2)[hazard,None],np.array([.9,.52,.06]),np.array([.045,.055,.065]))
height=(~seam).astype(float)*.08
hy,hx=np.gradient(height)
normal=np.stack([-hx*3,-hy*3,np.ones_like(hx)],axis=2)
normal/=np.linalg.norm(normal,axis=2)[...,None]
packed=np.stack([np.ones_like(x),np.clip(.36+.18*seam+noise,0,1),np.where(tile==1,.25,.8)],axis=2)
def image(name,rgb,data=False):
    im=bpy.data.images.new(name,width=N,height=N,alpha=True)
    if data: im.colorspace_settings.name='Non-Color'
    pixels=np.concatenate([rgb,np.ones((N,N,1))],axis=2).astype(np.float32)
    im.pixels.foreach_set(pixels.ravel())
    im.filepath_raw=str(dest/(name+'.png'));im.file_format='PNG';im.save()
    return im
albedo=image('colony_albedo',base)
orm=image('colony_rough_metal',packed,True)
norm=image('colony_normal',normal*.5+.5,True)
for m in [hull,armor,shadow,copper]:
    nodes=m.node_tree.nodes;links=m.node_tree.links;p=nodes.get('Principled BSDF')
    a=nodes.new('ShaderNodeTexImage');a.image=albedo;links.new(a.outputs['Color'],p.inputs['Base Color'])
    r=nodes.new('ShaderNodeTexImage');r.image=orm
    sep=nodes.new('ShaderNodeSeparateColor');links.new(r.outputs['Color'],sep.inputs['Color'])
    links.new(sep.outputs['Green'],p.inputs['Roughness']);links.new(sep.outputs['Blue'],p.inputs['Metallic'])
    n=nodes.new('ShaderNodeTexImage');n.image=norm
    nm=nodes.new('ShaderNodeNormalMap');links.new(n.outputs['Color'],nm.inputs['Color']);links.new(nm.outputs['Normal'],p.inputs['Normal'])
objects=[]
manifest={'units':'metres','author':'Original repository procedural art; no third-party assets','blender':bpy.app.version_string,'assets':{},'windows':[]}


def track(obj,material):
    obj.data.materials.clear()
    obj.data.materials.append(material)
    if material in [hull,armor,shadow,copper] and obj.data.uv_layers.active:
        idx=[hull,armor,shadow,copper].index(material)
        for loop in obj.data.uv_layers.active.data:
            loop.uv=(loop.uv.x*.48+(idx%2)*.5+.01,loop.uv.y*.48+(idx//2)*.5+.01)
    objects.append(obj)
    return obj

def box(name,pos,size,material,edge=0,angle=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=pos)
    o=bpy.context.object
    o.name=name
    o.dimensions=size
    o.rotation_euler.z=angle
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if edge:
        modifier=o.modifiers.new("machined chamfer","BEVEL")
        modifier.width=edge
        modifier.segments=2
        bpy.ops.object.modifier_apply(modifier=modifier.name)
    return track(o,material)

def rod(name,start,end,radius,material,vertices=12):
    a,b=Vector(start),Vector(end)
    d=b-a
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,
         depth=d.length,location=(a+b)*.5)
    o=bpy.context.object
    o.name=name
    o.rotation_euler=d.to_track_quat("Z","Y").to_euler()
    return track(o,material)

def torus(name,radius,width,z,material,segments=128):
    bpy.ops.mesh.primitive_torus_add(major_segments=segments,
         minor_segments=12,major_radius=radius,minor_radius=width,
         location=(0,0,z))
    o=bpy.context.object
    o.name=name
    return track(o,material)

def export_glb(file_name):
    # Merge modules sharing materials: seven batched meshes instead of hundreds
    # of draw objects. Rotate Blender Z-up construction into Godot orientation.
    coords=[o.matrix_world @ v.co for o in objects for v in o.data.vertices]
    lo=[min(v[i] for v in coords) for i in range(3)]
    hi=[max(v[i] for v in coords) for i in range(3)]
    manifest['assets'][file_name]={'bounds_min':lo,'bounds_max':hi,'triangles':sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in objects),'modules':len(objects)}
    export=[]
    # Collect groups before joins remove Blender objects from the scene.
    groups={}
    for o in objects:
        key=(o.data.materials[0],int((o.location.x+3000)//750) if 'station' in file_name else 0)
        groups.setdefault(key,[]).append(o)
    for (material,chunk),selected in groups.items():
        if not selected:
            continue
        bpy.ops.object.select_all(action="DESELECT")
        for o in selected:
            o.select_set(True)
        bpy.context.view_layer.objects.active=selected[0]
        if len(selected)>1:
            bpy.ops.object.join()
        joined=bpy.context.object
        joined.name=material.name+"_sector_"+str(chunk)
        joined.matrix_world=Matrix.Rotation(math.pi/2,4,"X") @ joined.matrix_world
        export.append(joined)
    bpy.ops.object.select_all(action="DESELECT")
    for o in export:
        o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(dest/file_name),
        export_format="GLB",use_selection=True,export_apply=True)
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    objects.clear()
    print("Export:",file_name,"material groups:",len(export))

# A six-kilometre axial colony, not a scaled wheel. Repeated pressure districts
# flank a cargo/utility spine; habitats and heavy industry occupy distinct zones.
def loft(name,sections,material):
    vertices=[]
    ring=[(-.7,-1),(.7,-1),(1,-.5),(1,.5),(.65,1),(-.65,1),(-1,.5),(-1,-.5)]
    for z,w,h,cy in sections:
        vertices.extend([(x*w,y*h+cy,z) for x,y in ring])
    faces=[tuple(reversed(range(8)))]
    for k in range(len(sections)-1):
        for j in range(8):faces.append((k*8+j,k*8+(j+1)%8,(k+1)*8+(j+1)%8,(k+1)*8+j))
    faces.append(tuple(range((len(sections)-1)*8,len(sections)*8)))
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(vertices,[],faces);mesh.update()
    o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o)
    bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
    bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project();bpy.ops.object.mode_set(mode='OBJECT')
    return track(o,material)

def colony(far=False):
    edge=0 if far else 5
    box('6000m backbone',(0,-120,-160),(6000,64,110),hull,edge)
    for y in [-170,-65]:
        box('transit guideway',(0,y,60),(5960,12,24),shadow)
    for i in range(15):
        x=-2800+i*400
        box('structural bulkhead',(x,-110,-80),(28,200,340),armor,edge)
        for side in [-1,1]:
            rod('diagonal tension strut',(x-180,-165,-130),(x+180,side*220,-250),12,hull,6)
    # Habitation: staggered pressure blocks, shaded courtyards, terrace decks.
    for district,x0 in enumerate([-2050,-1050,450,1400]):
        for tier in range(3):
            x=x0+(-65 if tier%2 else 35)
            y=110+tier*200
            z=-120-tier*55
            length=610-tier*65
            pod=loft('faceted habitation pressure vessel',[(-length/2,72,34,0),(-length/2+35,112,55,0),(length/2-35,112,55,0),(length/2,72,34,0)],armor)
            pod.rotation_euler.y=math.pi/2;pod.location=(x,y,z)
            if not far:
                for k in range(7):
                    px=x-length*.4+k*length*.8/6
                    for side in [-1,1]:
                        rod('pressure vessel external rib',(px,y-25,z+side*116),(px,y+25,z+side*116),3,hull,6)
                    rod('habitat rooftop conduit',(px,y+57,z-65),(px,y+57,z+65),3,copper,6)
            box('terrace sunshade',(x,y+70,z+50),(650-tier*65,10,285),hull,edge)
            box('recessed greenhouse',(x,y+61,z+85),(470-tier*65,14,100),glass)
            rod('district transit lift',(x0+330,-140,30),(x0+330,570,30),22,shadow,8)
            if not far:
                for row in range(2):
                    for col in range(22-tier*3):
                        manifest['windows'].append([x-260+col*24,y-12+row*24,z+116])
                for j in range(5):
                    box('hab airlock/service bay',(x-220+j*100,y-15,z+121),(20,38,10),shadow,2)
        box('district transport terminal',(x0,-15,100),(150,65,130),copper,edge)
    # Asymmetric refinery/thermal zone; no city blocks masquerading as engines.
    for x in [2200,2480,2760]:
        rod('refinery tank',(x,-70,-280),(x,420,-280),92,hull,16 if not far else 8)
        for y in [0,170,340]:
            box('tank servicing gantry',(x,y,-280),(225,14,225),copper,edge)
        box('radiator root',(x,-220,-150),(80,120,100),hull)
        for side in [-1,1]:
            box('thermal radiator',(x, -440, side*260-160),(180,410,12),shadow)
            if not far:
                for k in range(8):
                    box('radiator coolant rib',(x-75+k*21,-440,side*260-150),(3,390,4),copper)
    # Cargo districts, independent external berths and access viaducts.
    for x in [-2700,-500,900,1850]:
        box('cargo viaduct',(x,-170,260),(80,45,430),hull,edge)
        box('secondary docking terminal',(x,-130,480),(190,140,160),armor,edge)
        box('secondary berth recess',(x,-125,562),(95,70,8),shadow)
        box('secondary berth guide',(x,-170,570),(110,5,4),cyan)
        if not far:
            for j in range(5):
                box('standard freight pod',(x-70+j*32,-40,470),(26,28,54),copper,2)
    loft('central logistics pressure hull',[(-140,140,80,-80),(20,170,110,-80),(440,150,90,-80),(518,90,70,-70)],hull)
    if far:
        box('distant berth frame left',(-48,0,625),(12,72,200),armor)
        box('distant berth frame right',(48,0,625),(12,72,200),armor)
        box('distant berth roof',(0,32,625),(108,12,200),armor)
        box('distant berth floor',(0,-32,625),(108,12,200),armor)

colony(True)
export_glb('hero_station_far.glb')
colony(False)
# Real open 76 x 48m throat, 200m depth. No front cap/black disk.
box('hangar floor',(0,-29,620),(108,10,200),shadow,1)
box('hangar ceiling',(0,29,620),(108,10,200),hull,1)
for side in [-1,1]:
    box('hangar wall',(side*49,0,620),(10,68,200),hull,2)
    for z in [530,570,615,660,710]:
        box('mechanical portal jamb',(side*42,0,z),(8,58,9),armor,1.5)
        box('portal lintel',(0,28,z),(92,8,9),armor,1)
        box('floor guidance',(side*30,-23,z),(2,.6,18),cyan)
        box('maintenance access',(side*42,0,z-14),(2,16,13),copper,.4)
        rod('hydraulic door ram',(side*50,-28,z),(side*50,28,z),2,copper)
    box('retracted pressure shutter',(side*58,0,718),(18,58,8),shadow,1)
    box('mouth hazard rail',(side*43,0,724),(4,60,4),copper,.5)
box('rear pressure wall',(0,0,518),(108,68,4),shadow)
box('rear observation gallery',(0,13,522),(50,8,2),glass)
for x in [-26,-10,10,26]:
    box('cargo cradle',(x,-17,560),(10,12,24),copper,1)
for z in [545,590,635,680]:
    box('ceiling service bridge',(0,20,z),(74,3,4),shadow)
# Painted berth designation is geometry only near the entrance.
box('berth sign backplate',(0,40,721),(90,12,3),shadow,1)
curve=bpy.data.curves.new('berth designation','FONT');curve.body='C 07 / COURIER';curve.size=5;curve.extrude=.04
text=bpy.data.objects.new('berth signage',curve);bpy.context.collection.objects.link(text)
text.location=(-23,37,724);text.rotation_euler=(0,0,0)
bpy.context.view_layer.objects.active=text;text.select_set(True)
bpy.ops.object.convert(target='MESH');track(bpy.context.object,amber)
export_glb('hero_station.glb')

# Faceted, lofted pressure hull: actual tapered cross-sections, not a textured box.
loft('courier pressure hull',[(-15,.6,.65,0),(-11,2,1.5,.2),(-5,3,2.6,0),(5,3.8,2.5,0),(12,3,2,0)],hull)
loft('armoured dorsal shell',[(-11,1.8,.3,1.5),(-6,2.7,.4,2.3),(6,3.5,.35,2.3),(10,2.8,.3,2)],armor)
loft('angular cockpit canopy',[(-11,1.3,.12,1.6),(-8,2, .65,2.1),(-5,2,.65,2.1)],glass)
for side in [-1,1]:
    rod('canopy spine',(side*1.4,1.9,-10.8),(side*2.1,2.9,-5),.1,armor,6)
    box('external cargo container',(side*4.5,-.2,3),(2.4,4,14),armor,.35)
    for z in [-3,0,3,6,9]:
        box('container structural rib',(side*5.75,-.2,z),(.15,4.1,.16),hull,.04)
        box('recessed service hatch',(side*5.72,.3,z+1),(.07,1.8,1.6),shadow,.04)
    rod('engine mount',(side*2.7,0,9),(side*2.7,0,12),1.55,hull,16)
    # Open annular exhaust shells, with recessed emissive chamber.
    for j in range(16):
        a=j*math.tau/16;b=(j+1)*math.tau/16
        rod('nozzle longitudinal petal',(side*2.7+1.4*math.cos(a),1.4*math.sin(a),12),(side*2.7+1.7*math.cos(a),1.7*math.sin(a),15),.2,shadow,6)
        rod('exhaust rim',(side*2.7+1.7*math.cos(a),1.7*math.sin(a),15),(side*2.7+1.7*math.cos(b),1.7*math.sin(b),15),.12,copper,6)
    rod('recessed engine emission',(side*2.7,0,12.2),(side*2.7,0,12.3),1.25,cyan,16)
    box('navigation lamp',(side*5.8,1.5,-3),(.2,.3,.8),amber if side<0 else cyan,.05)
    for z in [-7,8]:
        rod('RCS housing',(side*2.9,1.2,z),(side*3.5,1.2,z),.35,shadow,8)
    box('folded landing skid',(side*2,-2.5,2),(.4,.4,8),shadow,.1)
for z in [-2,1,4,7]:
    box('dorsal maintenance panel',(0,2.72,z),(3,.08,1.6),shadow,.03)
    for x in [-1.3,1.3]:box('panel fastening rail',(x,2.8,z),(.1,.1,1.7),copper,.02)
export_glb('courier_30m.glb')
box('window instance',(0,0,0),(12,4,.6),amber)
export_glb('window_module.glb')
manifest['dock']={'clear_width':76,'clear_height':48,'front_z':720,'rear_z':520,'depth':200}
(dest/'hero_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
assert 5990<=manifest['assets']['hero_station.glb']['bounds_max'][0]-manifest['assets']['hero_station.glb']['bounds_min'][0]<=6010
assert 29.9<=manifest['assets']['courier_30m.glb']['bounds_max'][2]-manifest['assets']['courier_30m.glb']['bounds_min'][2]<=30.5
print('Hero v0.2 assets exported; visual and Android approval still required')
