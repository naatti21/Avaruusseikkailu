#!/usr/bin/env python3
"""Self-authored modular hard-surface station and courier. World units: metres.
Run with Blender: --background --python generate_hero.py -- --output ./assets
"""
import bpy
import math
import sys
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
cyan=mat("05 cyan nav emission",(.025,.78,.88),.1,.28,4)
amber=mat("06 amber utility emission",(1,.36,.07),.1,.25,3)
glass=mat("07 cockpit glass",(.04,.17,.24),.33,.11)
materials=[hull,armor,shadow,copper,cyan,amber,glass]
objects=[]

def track(obj,material):
    obj.data.materials.clear()
    obj.data.materials.append(material)
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
    export=[]
    for material in materials:
        selected=[o for o in objects if o.data.materials[0]==material]
        if not selected:
            continue
        bpy.ops.object.select_all(action="DESELECT")
        for o in selected:
            o.select_set(True)
        bpy.context.view_layer.objects.active=selected[0]
        if len(selected)>1:
            bpy.ops.object.join()
        joined=bpy.context.object
        joined.name=material.name
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

# The same non-scaling station in all three camera beats.
# Main pressure ring diameter: 2*(839+49)=1776m. Navigation/armor extend
# slightly beyond it, intended overall silhouette ~1.8km.
torus("pressure ring",839,49,-110,hull)
torus("external ridge",852,15,-75,armor)
torus("inner guide",796,12,-45,shadow)
torus("navigation rail",826,4,-28,cyan)
torus("service girder",742,8,-132,copper)
for i in range(72):
    theta=i*math.tau/72
    c,s=math.cos(theta),math.sin(theta)
    x,y=839*c,839*s
    box("armored segment %02d"%i,(x,y,-101),(62,92,82),
        armor if i%4 else hull,7,theta)
    if i%2==0:
        box("recessed shield %02d"%i,(x*1.057,y*1.057,-66),
            (12,39,10),shadow,2,theta)
    if i%3==0:
        box("nav inset %02d"%i,(x*.948,y*.948,-36),
            (7,29,5),cyan,1,theta)
    if i%9==0:
        rod("antenna %02d"%i,(x,y,-96),
            (x*1.12,y*1.12,-185),2.5,shadow,8)
        box("beacon %02d"%i,(x*1.12,y*1.12,-185),
            (13,13,13),amber,2)
for i in range(12):
    theta=i*math.tau/12
    c,s=math.cos(theta),math.sin(theta)
    rod("radial truss %02d"%i,(c*110,s*110,-125),
        (c*760,s*760,-125),15,hull)
    rod("tension member %02d"%i,(c*130,s*130,-167),
        (c*690,s*690,-167),4,copper)
    box("spoke collar %02d"%i,(c*690,s*690,-125),
        (54,54,42),shadow,5,theta)
rod("longitudinal spine",(0,0,-580),(0,0,190),70,hull,32)
rod("rear machinery ring",(0,0,-400),(0,0,-338),95,armor,32)
rod("command drum",(0,0,100),(0,0,212),115,armor,40)
rod("dark docking throat",(0,0,212),(0,0,297),60,shadow,32)
rod("docking mouth armour",(0,0,250),(0,0,278),91,hull,32)
torus("berth navigation ring",71,4,282,cyan,64)
torus("inner docking lock",56,9,297,copper,64)
box("deep shadow inside berth",(0,0,304),(65,52,9),shadow,3)
for i in range(4):
    theta=i*math.tau/4
    x,y=73*math.cos(theta),73*math.sin(theta)
    rod("docking clamp %d"%i,(x,y,278),(x,y,313),8,copper)
    box("docking lamps %d"%i,(x,y,315),(10,10,5),cyan,2)
for i in range(24):
    z=-535+i*30
    box("spinal armour rib %02d"%i,(0,0,z),
        (158,29,14),armor,3)
    if i%2==0:
        box("service light %02d"%i,(75,0,z),
            (9,22,5),amber,1)
for i in range(24):
    theta=math.tau*i/24
    x,y=105*math.cos(theta),105*math.sin(theta)
    box("control windows %02d"%i,(x,y,165),
        (13,13,8),glass,2,theta)
export_glb("hero_station.glb")

# 30 m courier. Nose points toward station on Godot negative-Z axis.
box("central hull",(0,0,1),(5.5,3.6,22),hull,1.1)
box("freight keel",(0,-1.2,3),(4.4,3.4,15),armor,.9)
rod("nose wedge",(0,0,-15),(0,0,-8),1.8,hull,20)
box("cockpit visor",(0,2,-6),(3.6,1.2,6.8),glass,.55)
for side in (-1,1):
    box("cargo wing %d"%side,(side*5,-.35,3),
        (8.5,.75,10),hull,.8,side*.18)
    box("wing trim %d"%side,(side*8,-.1,3),
        (2,.32,8),copper,.2)
    rod("engine shroud %d"%side,(side*2.25,-.55,10),
        (side*2.25,-.55,14),1.5,shadow)
    rod("engine light %d"%side,(side*2.25,-.55,14),
        (side*2.25,-.55,15),1.1,cyan)
    box("wing running lamp %d"%side,(side*8,0,-.8),
        (1.2,.9,2),amber if side<0 else cyan,.3)
for i in range(5):
    box("cargo rib %d"%i,(0,2.05,-1+i*2.1),
        (5.9,.35,.65),armor,.14)
export_glb("courier_30m.glb")

for filename in ("hero_station.glb","courier_30m.glb"):
    p=dest/filename
    assert p.exists() and p.stat().st_size>1500,filename
print("SUCCESS: deterministic geometry/GLB exports; actual visual QA pending")
