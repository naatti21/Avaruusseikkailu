"""Original C-07 concept interpretation. Blender 4.3.2, metre units.
Run: blender --background --python native-prototype/art/c07/build_c07.py
No legacy courier geometry, downloaded models, or concept-image projections.
"""
from pathlib import Path
import bpy, math, json, hashlib
import numpy as np
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'native-prototype/production/models/c07_courier.glb'
SOURCE = Path(__file__).parent / 'source/c07_courier.blend'
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1
# Forward -Y in Blender becomes +Z in Godot. Z-up becomes Y-up.
parts = []
# One 1024 atlas, eight 256x512 tiles, physically authored surface variation.
W = 1024
colors = [(0.67,.70,.69),(.105,.135,.15),(.64,.26,.052),(.035,.105,.14),
          (.32,.37,.39),(.8,.88,.94),(.95,.40,.07),(.025,.033,.041)]
rough = [.54,.58,.61,.22,.38,.32,.4,.72]
metal = [.28,.72,.25,.58,.82,.15,.25,.65]
yy, xx = np.mgrid[:W,:W]
tile = xx//256 + (yy//512)*4
u,v=xx%256,yy%512
# Directional milling and restrained scratches; no noise-derived geometry.
rng=np.random.default_rng(1207)
noise=rng.uniform(-.012,.012,(W,W))
seam=((u<3)|(u>252)|(v<3)|(v>508))
scratch=((xx*7+yy*19)%487<2)&((yy%101)<39)
base=np.array(colors,dtype=np.float32)[tile]+noise[:,:,None]
base[seam]*=.55
base[scratch]*=.85
orm=np.ones((W,W,3),dtype=np.float32)
orm[:,:,1]=np.clip(np.array(rough)[tile]+noise*3,0,1)
orm[:,:,2]=np.array(metal)[tile]
normal=np.zeros((W,W,3),dtype=np.float32); normal[:]=(.5,.5,1)
normal[:,:,0]+=np.sin(xx*.7)*.012
normal[:,:,1]+=np.sin(yy*.3)*.008
normal[seam,0]=.55
em=np.zeros((W,W,3),dtype=np.float32)
em[tile==5]=(.28,.62,1.0); em[tile==6]=(1,.22,.025)
images={}
for name,pixels,data in [('basecolor',base,False),('metalrough',orm,True),('normal',normal,True),('emissive',em,False)]:
 im=bpy.data.images.new('C07_'+name,W,W)
 if data: im.colorspace_settings.name='Non-Color'
 rgba=np.ones((W,W,4),dtype=np.float32); rgba[:,:,:3]=pixels
 im.pixels.foreach_set(rgba.ravel()); im.pack(); images[name]=im
mat=bpy.data.materials.new('C07_shared_1k_PBR_atlas'); mat.use_nodes=True
n=mat.node_tree.nodes; links=mat.node_tree.links; bs=n.get('Principled BSDF')
for key in images:
 tex=n.new('ShaderNodeTexImage'); tex.image=images[key]; tex.label=key
 if key=='basecolor': links.new(tex.outputs['Color'],bs.inputs['Base Color'])
 if key=='metalrough':
  sep=n.new('ShaderNodeSeparateColor'); links.new(tex.outputs['Color'],sep.inputs['Color'])
  links.new(sep.outputs['Green'],bs.inputs['Roughness']); links.new(sep.outputs['Blue'],bs.inputs['Metallic'])
 if key=='normal':
  norm=n.new('ShaderNodeNormalMap'); norm.inputs['Strength'].default_value=.35
  links.new(tex.outputs['Color'],norm.inputs['Color']); links.new(norm.outputs['Normal'],bs.inputs['Normal'])
 if key=='emissive':
  links.new(tex.outputs['Color'],bs.inputs['Emission Color']); bs.inputs['Emission Strength'].default_value=1.5

def finish(obj,name,tile=0,group='hull',bevel=.045):
 obj.name=name; obj['assembly']=group; obj['atlas_tile']=tile
 bpy.context.view_layer.objects.active=obj
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if bevel:
  mod=obj.modifiers.new('Machined edge radius','BEVEL'); mod.width=bevel; mod.segments=2
  bpy.ops.object.modifier_apply(modifier=mod.name)
 # Face-local metric projection; all faces own their atlas island, padded from tiles.
 uv=obj.data.uv_layers.new(name='AtlasUV') if not obj.data.uv_layers else obj.data.uv_layers.active
 for poly in obj.data.polygons:
  axis=max(range(3),key=lambda k:abs(poly.normal[k])); axes=[k for k in range(3) if k!=axis]
  pts=[obj.data.vertices[obj.data.loops[i].vertex_index].co for i in poly.loop_indices]
  lo=[min(p[k] for p in pts) for k in axes]; hi=[max(p[k] for p in pts) for k in axes]
  for i,p in zip(poly.loop_indices,pts):
   q=[(p[k]-lo[j])/max(.001,hi[j]-lo[j]) for j,k in enumerate(axes)]
   uv.data[i].uv=((tile%4+.04+q[0]*.92)/4,(tile//4+.025+q[1]*.95)/2)
 obj.data.materials.clear(); obj.data.materials.append(mat)
 if name.startswith('Engine bell'):
  for poly in obj.data.polygons: poly.use_smooth=True
 # Flat major panels, bevels get weighted vertex normals (no melted hard surfaces).
 mod=obj.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL'); mod.keep_sharp=True; mod.weight=50
 bpy.ops.object.modifier_apply(modifier=mod.name)
 parts.append(obj); return obj

def mesh(name,verts,faces,tile=0,group='hull',bevel=.04):
 m=bpy.data.meshes.new(name); m.from_pydata(verts,[],faces); m.update()
 ob=bpy.data.objects.new(name,m); scene.collection.objects.link(ob)
 # Recalculate outward winding before bevel and glTF export.
 bpy.context.view_layer.objects.active=ob; ob.select_set(True)
 bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT'); bpy.ops.mesh.normals_make_consistent(inside=False); bpy.ops.object.mode_set(mode='OBJECT')
 ob.select_set(False)
 return finish(ob,name,tile,group,bevel)

def box(name,loc,size,tile=0,group='hull',bevel=.04):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc); ob=bpy.context.object; ob.scale=size
 return finish(ob,name,tile,group,bevel)

def bar(name,a,b,r=.05,tile=4,group='service'):
 a,b=Vector(a),Vector(b)
 bpy.ops.mesh.primitive_cylinder_add(vertices=8,radius=r,depth=(b-a).length,location=(a+b)/2)
 ob=bpy.context.object; ob.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler()
 return finish(ob,name,tile,group,.01)

# Clockwise cross section around Y, chamfered rectangular pressure vessel.
def cross(w,h,c=.24):
 return [(-w*(1-c),h),(w*(1-c),h),(w,h*(1-c)),(w,-h*(1-c)),
         (w*(1-c),-h),(-w*(1-c),-h),(-w,-h*(1-c)),(-w,h*(1-c))]

def loft(name,sections,tile=1,group='hull',bevel=.06):
 verts=[(x,y,z) for y,w,h in sections for x,z in cross(w,h)]
 faces=[tuple(reversed(range(8))),tuple(range((len(sections)-1)*8,len(sections)*8))]
 for j in range(len(sections)-1):
  for i in range(8): faces.append((j*8+i,j*8+(i+1)%8,(j+1)*8+(i+1)%8,(j+1)*8+i))
 return mesh(name,verts,faces,tile,group,bevel)

def shell_panel(name,y0,y1,w,h,edge,tile=0,group='armor',thick=.17):
 # Individual wrap-around plates, real thickness and gaps between facets.
 a,b=Vector(cross(w,h)[edge]),Vector(cross(w,h)[(edge+1)%8])
 d=(b-a).normalized(); a+=d*.065; b-=d*.065
 normal=Vector(((a.x+b.x)*.5,(a.y+b.y)*.5)).normalized()
 ai,bi=a-normal*thick,b-normal*thick
 verts=[(p.x,y,p.y) for y in [y0,y1] for p in [a,b,bi,ai]]
 ob=mesh(name,verts,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],tile,group,.035)
 return ob

loft('Continuous pressure hull',[(-14.65,2.65,1.70),(-11.6,3.75,2.45),(-7.6,4.85,3.05),(10.8,4.85,3.05),(12.8,4.05,2.60)],1)
# Keel is a connected load path under removable cargo and armor.
loft('Ventral load bearing keel',[(-11,1.7,.42),(10,1.7,.42),(12,1.2,.35)],7,'keel').location.z=-3.2
# Cockpit visor: independent trapezoid panes inside raised structural mullions.
for side in [-1,1]:
 verts=[(side*2.70,-14.72,.15),(side*3.72,-11.7,.20),(side*3.5,-11.7,1.78),(side*2.56,-14.72,1.35)]
 ob=mesh('Cockpit side glazing',verts,[(0,1,2,3)],3,'cockpit',0)
 for i in range(4): bar('Visor armored mullion',verts[i],verts[(i+1)%4],.10,4,'cockpit')
 for y,w in [(-13.4,3.12),(-12.15,3.55)]:
  bar('Visor cross mullion',(side*w,y,.19),(side*(w-.12),y,1.63),.055,0,'cockpit')
 # Sloping upper windshield on faceted prow.
 verts=[(side*.15,-14.5,1.74),(side*2.15,-14.5,1.74),(side*2.85,-10.7,2.65),(side*.15,-10.7,2.65)]
 mesh('Upper cockpit glazing',verts,[(0,1,2,3)],3,'cockpit',0)
 for i in range(4): bar('Upper windshield frame',verts[i],verts[(i+1)%4],.095,4,'cockpit')
 # recessed forward lights within real armored housings
 box('Forward light recess',(side*2.2,-14.78,-.55),(.75,.28,.72),7,'cockpit')
 for z in [-.73,-.39]: box('Forward guide lamp',(side*2.2,-14.94,z),(.48,.04,.15),5,'lights',.015)
# Front-facing paired panes and a stout central divider.
for side in [-1,1]:
 mesh('Forward cockpit pane',[(side*.20,-14.69,.10),(side*1.95,-14.69,.10),(side*1.95,-14.69,1.15),(side*.20,-14.69,1.15)],[(0,1,2,3)],3,'cockpit',0)
 for z in [.04,1.21]: bar('Forward visor frame',(side*.16,-14.73,z),(side*2.02,-14.73,z),.07,4,'cockpit')
bar('Central armored prow',(0,-14.8,-1.2),(0,-14.8,1.67),.15,4,'cockpit')
# Three broad discontinuous armor belts; chamfered transitions preserve a long ship silhouette.
for num,(y0,y1,w,h) in enumerate([(-9.5,-7.4,5.35,3.55),(-5.5,-2.3,5.95,3.92),(4.3,7.2,5.95,3.92),(10.3,11.8,5.35,3.55)]):
 for edge in range(8):
  panel=shell_panel('Armor belt %d facet %d'%(num,edge),y0,y1,w,h,edge,0,'armor_%d'%num)
  if edge in [2,6]:
   side=1 if edge==2 else -1
   for y in [y0+.45,y1-.45]:
    bpy.ops.mesh.primitive_cube_add(size=1,location=(side*w,y,2.35))
    cut=bpy.context.object; cut.scale=(1,.42,.32)
    bpy.context.view_layer.objects.active=cut; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    bev=cut.modifiers.new('Rounded access opening','BEVEL'); bev.width=.055; bev.segments=3
    bpy.ops.object.modifier_apply(modifier=bev.name)
    bpy.context.view_layer.objects.active=panel
    mod=panel.modifiers.new('Through inspection port','BOOLEAN'); mod.operation='DIFFERENCE'; mod.object=cut
    bpy.ops.object.modifier_apply(modifier=mod.name); bpy.data.objects.remove(cut,do_unlink=True)
   for y in [y0+.22,y1-.22]:
    for z in [-1.7,1.7]:
     bpy.ops.mesh.primitive_cylinder_add(vertices=12,radius=.075,depth=.035,location=(side*(w+.025),y,z),rotation=(0,math.pi/2,0))
     finish(bpy.context.object,'Captive hex fastener',4,'armor_%d'%num,.007)
  if edge==0:
   box('Dorsal access gasket',(0,(y0+y1)/2,h+.022),(2.9,(y1-y0)*.65,.035),7,'armor_%d'%num,.07)
   box('Dorsal access cover',(0,(y0+y1)/2,h+.055),(2.73,(y1-y0)*.59,.04),0,'armor_%d'%num,.07)
   for x in [-1.12,1.12]:
    box('Flush lifting handle',(x,(y0+y1)/2,h+.092),(.10,.55,.04),4,'armor_%d'%num,.018)
  if edge in [1,7]:
   side=1 if edge==1 else -1
   for y in [y0+.32,y1-.32]:
    bar('Chamfer retaining spine',(side*w*.79,y,h*.97),(side*w*.97,y,h*.79),.06,4,'armor_%d'%num)
 # Actual radial attachment struts connect the stand-off armor to the pressure hull.
 inner_w=4.5 if num==0 else 4.85
 inner_h=2.85 if num==0 else 3.05
 for y in [y0+.18,y1-.18]:
  for (ix,iz),(ox,oz) in zip(cross(inner_w,inner_h),cross(w-.17,h-.15)):
   bar('Armor radial attachment',(ix,y,iz),(ox,y,oz),.14,4,'service')
 # Paired end ribs and fine dark separation line rather than floating decoration.
 for y in [y0-.09,y1+.09]:
  for e in range(8): shell_panel('Belt edge retainer',y-.055,y+.055,w-.1,h-.06,e,4,'armor_%d'%num,.12)
 for side in [-1,1]:
  for y in [y0+.3,y1-.3]:
   for z in [-2.4,2.4]:
    box('Recessed access latch',(side*(w+.015),y,z),(.045,.35,.20),7,'armor_%d'%num,.015)
    box('Latch handle',(side*(w+.045),y,z),(.03,.20,.045),4,'armor_%d'%num,.008)
  # Raised service doors on armor sidewall; no painting detail on a cuboid substitute.
  box('Service panel gasket',(side*(w+.015),(y0+y1)/2,-.65),(.035,(y1-y0)*.64,1.05),7,'armor_%d'%num,.015)
  box('Service panel',(side*(w+.045),(y0+y1)/2,-.65),(.035,(y1-y0)*.59,.94),0,'armor_%d'%num,.015)
# Orange removable cargo cassettes exposed between white belts.
for bay,(y0,y1) in enumerate([(-2.1,1.0),(1.2,4.1),(7.5,10.1)]):
 for side in [-1,1]:
  ob=loft('Cargo cassette %d'%bay,[(y0,.44,2.45),(y0+.18,.55,2.675),(y1-.18,.55,2.675),(y1,.44,2.45)],2 if bay<2 else 1,'cargo',.045); ob.location.x=side*4.75
  for y in [y0+.12,y1-.12]:
   box('Cargo restraint',(side*5.36,y,0),(.12,.14,5.05),4,'cargo',.02)
  for z in [-2.35,2.35]: box('Cargo edge rail',(side*5.36,(y0+y1)/2,z),(.13,y1-y0,.13),1,'cargo',.02)
  for z in [-1.45,-.7,.05,.8,1.55]:
   box('Cargo formed stiffener',(side*5.35,(y0+y1)/2,z),(.055,y1-y0-.55,.07),4,'cargo',.015)
  box('Cargo ID plate',(side*5.40,(y0+y1)/2,1.8),(.035,.68,.34),0,'cargo',.015)
# Exposed mechanical interspaces and longitudinal coolant plumbing.
for side in [-1,1]:
 for z in [-2.2,2.2]:
  bar('Longitudinal coolant pipe',(side*4.9,-7.25,z),(side*4.9,10.2,z),.11,4)
 for y in [-6.8,-6.2,1.07,7.35]:
  box('Truss cross-member',(side*4.95,y,0),(.28,.15,5.2),7,'service',.03)
 for y in [-6.8,1.07,8.8]:
  for z in [-2.75,2.75]:
   box('Amber clearance lamp housing',(side*5.12,y,z),(.27,.33,.25),7,'lights')
   box('Amber clearance lamp',(side*5.28,y,z),(.035,.23,.15),6,'lights',.01)
# Dorsal roof equipment, radiators and mechanically legible docking socket.
for x in [-2.8,2.8]:
 box('Dorsal heat exchanger',(x,1.1,3.13),(2.0,5.7,.26),7,'dorsal',.08)
 for y in np.linspace(-1.35,3.55,16): box('Heat exchanger fin',(x,float(y),3.36),(1.82,.09,.22),4,'dorsal',.012)
box('Docking socket base',(0,-3.8,3.74),(2.2,1.65,.40),1,'dorsal',.1)
box('Docking socket recess',(0,-3.8,3.97),(1.48,1.05,.055),7,'dorsal',.04)
for x in [-.85,.85]: box('Docking jaw',(x,-3.8,3.97),(.24,1.25,.14),4,'dorsal',.025)
# Retracted landing / berth saddles and real braced attachment members.
for x in [-3.4,3.4]:
 for y in [-5.8,8.2]:
  box('Retracted landing saddle',(x,y,-3.65),(1.8,1.5,.4),1,'keel',.1)
  bar('Landing brace',(x,y-.5,-3.35),(x*.8,y+.4,-2.85),.17,4,'keel')
# Two deep bell nozzles: concentric wall mesh, interior visible from aft.
def nozzle(x):
 n=48; rings=[(11.65,1.55),(12.5,1.82),(14.9,1.82),(14.9,1.60),(13.4,1.12),(12.9,.72)]
 verts=[(x+r*math.cos(i*2*math.pi/n),y,r*math.sin(i*2*math.pi/n)) for y,r in rings for i in range(n)]
 faces=[]
 for j in range(len(rings)-1):
  for i in range(n): faces.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
 mesh('Engine bell with recessed throat',verts,faces,4,'engines',.025)
 for y,r in [(12.1,1.72),(12.7,1.89),(14.65,1.88)]:
  bpy.ops.mesh.primitive_torus_add(major_segments=48,minor_segments=6,location=(x,y,0),major_radius=r,minor_radius=.09,rotation=(math.pi/2,0,0))
  finish(bpy.context.object,'Engine retaining ring',1,'engines',0)
 bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=.7,depth=.08,location=(x,12.88,0),rotation=(math.pi/2,0,0))
 finish(bpy.context.object,'Recessed cold engine core',5,'lights',.02)
 for i in range(12):
  a=i*math.tau/12
  bar('Engine external cooling tube',(x+1.86*math.cos(a),12.5,1.86*math.sin(a)),(x+1.86*math.cos(a),14.55,1.86*math.sin(a)),.055,1,'engines')
for x in [-2.55,2.55]: nozzle(x)
# Four attitude thruster blocks with inset nozzle mouths.
for side in [-1,1]:
 for y in [-10.0,11.4]:
  box('RCS armored block',(side*4.6,y,-1.3),(.65,.8,.8),1,'service',.1)
  for z in [-1.48,-1.1]:
   bpy.ops.mesh.primitive_torus_add(major_segments=16,minor_segments=5,location=(side*4.96,y,z),major_radius=.12,minor_radius=.035,rotation=(0,math.pi/2,0))
   finish(bpy.context.object,'RCS inset nozzle rim',4,'service',0)
   box('RCS dark throat',(side*4.94,y,z),(.02,.18,.18),7,'service',.03)
# Geometry markings use Blender's bundled Bfont. Legible from both sides.
for side in [-1,1]:
 bpy.ops.object.text_add(location=(side*6.015,-4.85,.30))
 ob=bpy.context.object; ob.data.body='C-07'; ob.data.size=.80; ob.data.extrude=.003
 # text local X runs along the hull, local Y is up, normal points outward
 from mathutils import Matrix
 ob.rotation_euler=Matrix(((0,0,side),(side,0,0),(0,1,0))).to_euler()
 bpy.ops.object.convert(target='MESH'); finish(bpy.context.object,'C-07 registration',7,'markings',0)
# Metre reference camera and editable named assemblies in .blend.
for obj in parts: obj.select_set(False)
for name,loc in [('Review three quarter',(38,-42,26)),('Review aft',(-30,42,20))]:
 bpy.ops.object.camera_add(location=loc); cam=bpy.context.object; cam.name=name
 cam.rotation_euler=(-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.lens=48
 scene.camera=cam
bpy.ops.object.light_add(type='AREA',location=(10,-15,25)); bpy.context.object.data.energy=2500; bpy.context.object.data.shape='DISK'; bpy.context.object.data.size=15
scene['asset_id']='c07_courier'; scene['visual_approval']='candidate_only'
scene['reference']='User supplied 03_c07_aluksen_referenssi.jpg; original modeled interpretation'
SOURCE.parent.mkdir(parents=True,exist_ok=True)
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
# Batch by functional assembly for efficient runtime; retain editable source objects above.
groups={}
for ob in parts: groups.setdefault(ob['assembly'],[]).append(ob)
for group,objects in groups.items():
 bpy.ops.object.select_all(action='DESELECT')
 for ob in objects: ob.select_set(True)
 bpy.context.view_layer.objects.active=objects[0]; bpy.ops.object.join()
 bpy.context.object.name='C07_'+group
bpy.ops.object.select_all(action='DESELECT')
meshes=[o for o in scene.objects if o.type=='MESH']
for ob in meshes: ob.select_set(True)
OUT.parent.mkdir(parents=True,exist_ok=True)
bpy.ops.export_scene.gltf(filepath=str(OUT),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_texcoords=True,export_normals=True,export_materials='EXPORT',export_cameras=False,export_lights=False)
verts=[ob.matrix_world@v.co for ob in meshes for v in ob.data.vertices]
bounds=[max(v[k] for v in verts)-min(v[k] for v in verts) for k in range(3)]
triangles=sum(sum(len(p.vertices)-2 for p in ob.data.polygons) for ob in meshes)
stats={'blender':bpy.app.version_string,'source_objects':len(parts),'runtime_meshes':len(meshes),'triangles':triangles,'dimensions_blender_xyz_m':bounds,'texture_size':1024,'texture_maps':4,'glb_bytes':OUT.stat().st_size,'glb_sha256':hashlib.sha256(OUT.read_bytes()).hexdigest(),'blend_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest()}
(Path(__file__).parent/'build_metrics.json').write_text(json.dumps(stats,indent=2)+'\n')
print('C07_BUILD',json.dumps(stats))
