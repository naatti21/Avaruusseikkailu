"""C-07 v3 silhouette studies. Blender 4.3.2. Read-only source -> two new .blend/GLB files.
blender --background --python native-prototype/art/c07-v3/build_options.py -- /tmp/c07-v3-base.blend
No production asset replacement. No new production texture work.
"""
import bpy,bmesh,ast,math,hashlib,json,sys
from pathlib import Path
from mathutils import Vector,Matrix
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
BASE=Path(sys.argv[sys.argv.index('--')+1]);BASE_SHA='68086c196a1ec918f854e9e9522fba0b0b5da806c14536785c13c69cecd33808'
assert hashlib.sha256(BASE.read_bytes()).hexdigest()==BASE_SHA
SOURCE=HERE/'source';OUT=ROOT/'native-prototype/design-review/c07-v3'
SOURCE.mkdir(exist_ok=True,parents=True);OUT.mkdir(exist_ok=True,parents=True)
tree=ast.parse((HERE.parent/'c07/build_c07.py').read_text())
helpers=compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'original_model_helpers','exec')
records=[]

def world_points(ob):return [ob.matrix_world@v.co for v in ob.data.vertices]
def bounds(points):return [min(p[k] for p in points) for k in range(3)],[max(p[k] for p in points) for k in range(3)]
def map_points(ob,fn):
 inv=ob.matrix_world.inverted()
 for v in ob.data.vertices:v.co=inv@Vector(fn(ob.matrix_world@v.co))
 ob.data.normals_split_custom_set([(0,0,0)]*len(ob.data.loops));ob.data.update()

def retain_crop_front(ob):
 bm=bmesh.new();bm.from_mesh(ob.data)
 bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=.0001,plane_co=(0,-7.3,0),plane_no=(0,1,0),clear_outer=True)
 bmesh.ops.holes_fill(bm,edges=[e for e in bm.edges if e.is_boundary],sides=0)
 bm.to_mesh(ob.data);bm.free()

def cargo_remap(ob,center,half_size):
 lo,hi=bounds(world_points(ob));mid=[(a+b)/2 for a,b in zip(lo,hi)]
 def transform(p):
  q=[(p[k]-mid[k])/((hi[k]-lo[k])/2) for k in range(3)]
  # Preserve the inherited chamfered cassette topology; taper its fore/aft ends.
  taper=1-.25*abs(q[1])**3
  return (center[0]+q[0]*half_size[0]*taper,center[1]+q[1]*half_size[1],center[2]+q[2]*half_size[2]*taper)
 map_points(ob,transform)

for option in ['A','B']:
 bpy.ops.wm.open_mainfile(filepath=str(BASE));scene=bpy.context.scene;parts=[]
 # Reuse the reviewed model's shape/UV construction helpers, not its scene-building code.
 palette={0:((.48,.52,.51),.55,.12),1:((.32,.38,.42),.6,.18),2:((.62,.39,.15),.63,.08),3:((.035,.095,.13),.20,.2),4:((.42,.47,.50),.48,.25),5:((.35,.63,.75),.35,.05),6:((.65,.32,.09),.5,.1),7:((.065,.09,.10),.65,.12)}
 mats={}
 for tile,(color,rough,metal) in palette.items():
  m=bpy.data.materials.new('Study_'+str(tile));m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*(c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4 for c in color),1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
  if tile in [5,6]:p.inputs['Emission Color'].default_value=(*color,1);p.inputs['Emission Strength'].default_value=.4
  mats[tile]=m
 mat=mats[1];exec(helpers)
 inherited=[];cargo=[]
 for ob in list(scene.objects):
  if ob.type!='MESH':bpy.data.objects.remove(ob,do_unlink=True);continue
  g=ob.get('assembly');pts=world_points(ob);mean=sum(pts,Vector())/len(pts)
  keep=g in ['cockpit','engines'] or ob.name=='Continuous pressure hull' or ob.name.startswith('Cargo cassette 0') or (g=='lights' and (mean.y<-11 or ob.name.startswith('Recessed cold engine core')))
  if ob.name.startswith(('Propellant manifold','Engine service manifold','Manifold cooling vane')): keep=False
  if not keep:bpy.data.objects.remove(ob,do_unlink=True);continue
  ob['study_parent_object']=ob.name;inherited.append(ob.name)
  if ob.name.startswith('Cargo cassette 0'):cargo.append(ob);continue
  if ob.name=='Continuous pressure hull':retain_crop_front(ob);ob['assembly']='cockpit'
  is_engine=g=='engines' or ob.name.startswith('Recessed cold engine core')
  if is_engine:
   sign=1 if mean.x>0 else -1
   if option=='A':map_points(ob,lambda p,s=sign:(p.x+s*.95,p.y,p.z+.05))
   elif sign>0:map_points(ob,lambda p:(p.x+1.0,p.y,p.z+.05))
   else:map_points(ob,lambda p:((p.x+2.55)*.68-3.55,(p.y-12)*.68+9.4,p.z*.68+.35))
   ob['assembly']='propulsion'
  else:
   if ob.name.startswith(('Upper cockpit glazing','Upper windshield frame')):
    map_points(ob,lambda p:(p.x,p.y,p.z+.12))
   if option=='A':map_points(ob,lambda p:(p.x*.85,p.y,p.z*.94+.65))
   else:map_points(ob,lambda p:(p.x*.68-2.25,p.y,p.z*.85+1.05))
   ob['assembly']='cockpit'
 # The same two inherited cassette meshes are rescaled into removable primary modules.
 cargo.sort(key=lambda o:sum(v.x for v in world_points(o)))
 if option=='A':
  for ob,x in zip(cargo,[-3.95,3.95]):cargo_remap(ob,(x,1,-.85),(2.0,6.0,2.15));ob['assembly']='cargo'
  loft('A structural keel',[(-10,1.1,.75),(-6,1.55,1.1),(5,1.55,1.1),(11.8,1.2,.85)],1,'structure',.12).location.z=-1.75
  loft('A raised crew shoulder',[(-8.1,2.8,2.25),(-6.0,2.6,2.5),(-4.8,1.6,1.2)],0,'cockpit',.13).location.z=.75
  loft('A dorsal access spine',[(-5.7,.9,.55),(4.7,.9,.55),(7.8,1.25,.75)],4,'structure',.1).location.z=.65
  loft('A aft transmission case',[(7.8,1.5,1.0),(10.4,3.25,1.65),(12.3,3.7,1.4)],1,'structure',.15).location.z=-.05
  # Main propulsion yoke is swept from the keel to both engine axes; no continuous box body.
  for sign in [-1,1]:
   verts=[(sign*x,y,z) for z in [-1.0,.4] for x,y in [(1.2,5.4),(2.0,5.4),(4.0,11.8),(2.8,11.8)]]
   mesh('A swept thrust yoke',verts,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],1,'structure',.12)
   for y in [-2.7,4.5]:bar('A cargo trunnion',(sign*1.2,y,-1.5),(sign*3.8,y,-1.5),.3,4,'structure')
   for y in [-2.7,4.5]:bar('A landing leg',(sign*2.3,y,-1.5),(sign*2.3,y,-3.65),.18,4,'structure')
   loft('A landing runner',[( -5, .28,.20),(6.7,.28,.20)],7,'structure',.07).location=(sign*2.3,0,-3.75)
  box('A dorsal crew hatch',(0,-6.4,3.55),(1.6,1.75,.75),4,'cockpit',.15)
 else:
  cargo_remap(cargo[0],(-2.9,.25,-1.1),(3.05,5.6,2.3));cargo[0]['assembly']='cargo'
  cargo_remap(cargo[1],(-2.65,7.1,-.9),(2.0,1.65,1.65));cargo[1]['assembly']='cargo'
  loft('B offset utility spine',[(-11,1.05,.8),(-6.1,1.6,1.35),(6.2,1.65,1.5),(12.5,1.15,1.0)],1,'structure',.14).location=(2.4,0,-.15)
  loft('B command shoulder',[(-8.5,2.15,1.8),(-6.2,2.1,1.95),(-4.8,1.1,1.0)],0,'cockpit',.12).location=(-2.25,0,1.15)
  box('B crew roof hatch',(-2.25,-6.55,3.55),(1.3,1.5,.75),4,'cockpit',.12)
  loft('B main drive nacelle',[(8.1,1.35,1.2),(10.4,1.75,1.5),(12.4,1.6,1.4)],1,'structure',.14).location=(3.55,0,0)
  bar('B crew connection bridge',(-2.25,-6.5,-.45),(2.0,-6.0,-.45),.65,1,'structure')
  # Two diagonal load paths tie the offset crew/cargo to the starboard drive keel.
  for y in [-5.6,5.4]:
   verts=[(x,yy,z) for z in [-2.6,-1.3] for x,yy in [(-4.6,y),(-3.8,y-1),(3.4,y+1.3),(3.4,y+2.1)]]
   mesh('B asymmetric load crossbeam',verts,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],4,'structure',.12)
  # Retracted service gantry is a primary silhouette element, not fine greeble.
  box('B gantry pedestal',(3.4,-1.5,1.3),(.8,1.0,.8),4,'structure',.08)
  bar('B utility gantry root',(3.4,-1.5,1.0),(5.75,1.2,2.9),.30,4,'structure')
  bar('B folded utility gantry',(5.75,1.2,2.9),(4.4,5.5,2.6),.30,4,'structure')
  bar('B auxiliary drive support',(-1.1,6.8,-.3),(-3.55,9.0,.1),.5,1,'structure')
  for x in [-3.5,2.7]:
   loft('B landing runner',[(-6.0,.3,.2),(7.5,.3,.2)],7,'structure',.06).location=(x,0,-3.75)
   for y in ([-5.8,5.0] if x<0 else [-4.2,6.8]):bar('B landing leg',(x,y,-2.0),(x,y,-3.65),.18,4,'structure')
 # Flat, explicitly provisional materials reveal form. Retain UVs but add no texture work.
 meshes=[o for o in scene.objects if o.type=='MESH']
 for ob in meshes:
  ob.data.materials.clear();ob.data.materials.append(mats[int(ob.get('atlas_tile',1))])
  # The structural/bulkhead pressure hull is crew-colored, not a dark cargo container.
  if ob.name=='Continuous pressure hull':ob.data.materials[0]=mats[0]
 used_materials={m for ob in meshes for m in ob.data.materials}
 for material in list(bpy.data.materials):
  if material not in used_materials:bpy.data.materials.remove(material)
 for image in list(bpy.data.images):
  if image.users==0:bpy.data.images.remove(image)
 scene['study_option']=option;scene['base_source_sha256']=BASE_SHA;scene['visual_approval']='unselected';scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
 # Editable source review camera; no render used as evidence is generated by Blender.
 bpy.ops.object.camera_add(location=(36,-42,27));cam=bpy.context.object;cam.rotation_euler=(-cam.location).to_track_quat('-Z','Y').to_euler();scene.camera=cam
 bpy.context.preferences.filepaths.save_version=0
 source=SOURCE/f'c07_option_{option.lower()}.blend';bpy.ops.wm.save_as_mainfile(filepath=str(source))
 # Batch per assembly/material, retaining functional names with limited draw calls.
 groups={}
 for ob in meshes:groups.setdefault((ob['assembly'],ob.data.materials[0].name),[]).append(ob)
 for (group,material),objects in groups.items():
  bpy.ops.object.select_all(action='DESELECT')
  for ob in objects:ob.select_set(True)
  bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();bpy.context.object.name=option+'_'+group+'_'+material
 bpy.ops.object.select_all(action='DESELECT');runtime=[o for o in scene.objects if o.type=='MESH']
 for ob in runtime:ob.select_set(True)
 out=OUT/f'c07_option_{option.lower()}.glb'
 bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_texcoords=True,export_normals=True,export_materials='EXPORT',export_cameras=False,export_lights=False)
 lo,hi=bounds([v for o in runtime for v in world_points(o)])
 rec={'option':option,'base_commit':'764452a583c9c61a38ef8b229925247ad61aa2e6','base_source_sha256':BASE_SHA,'inherited_objects':inherited,'source':str(source.relative_to(ROOT)),'path':str(out.relative_to(ROOT)),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'dimensions_blender_xyz':[b-a for a,b in zip(lo,hi)],'triangles':sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in runtime),'surfaces':len(runtime),'materials':len({o.data.materials[0].name for o in runtime}),'texture_maps':0,'review_status':'unselected','can_integrate':False}
 records.append(rec);print('STUDY',json.dumps(rec),flush=True)
(OUT/'manifest.json').write_text(json.dumps({'schema_version':1,'baseline_commit':'764452a583c9c61a38ef8b229925247ad61aa2e6','release_approved':False,'selected_option':None,'options':records},indent=2)+'\n')
