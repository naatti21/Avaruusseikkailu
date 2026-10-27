"""Issue 15: editable A v3 continuation. Blender 4.3.2; no existing asset writes."""
import bpy,ast,math,json,hashlib
import numpy as np
from pathlib import Path
from mathutils import Vector
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[2]
BASE=HERE.parent/'c07-v3/source/c07_option_a.blend'
OLD=json.loads((ROOT/'native-prototype/design-review/c07-v3/manifest.json').read_text())['options'][0]
assert hashlib.sha256(BASE.read_bytes()).hexdigest()==OLD['source_sha256']
bpy.ops.wm.open_mainfile(filepath=str(BASE));scene=bpy.context.scene;parts=[]
OUT=ROOT/'native-prototype/design-review/c07-v4';OUT.mkdir(exist_ok=True)
# Retain selected A's structural keel, drive bells, aft case and landing gear.
# Its front and cargo body meshes are replaced within this source continuation.
retained=[];removed=[]
for ob in list(scene.objects):
 keep=ob.type=='MESH' and (ob.get('assembly')=='propulsion' or ob.name.startswith(('A structural keel','A swept thrust yoke','A landing')))
 if keep:ob['a_v3_source_object']=ob.name;retained.append(ob.name)
 else:removed.append(ob.name);bpy.data.objects.remove(ob,do_unlink=True)
# Eight purpose-specific atlas tiles. Restrained brushed/painted material variation.
W=1024;y,x=np.mgrid[:W,:W];tile=x//256+(y//512)*4;u=x%256;v=y%512
colors=np.array([(.62,.65,.63),(.19,.24,.26),(.57,.32,.105),(.035,.09,.115),(.38,.43,.44),(.38,.68,.76),(.79,.30,.08),(.075,.09,.10)])
rng=np.random.default_rng(1504);noise=rng.uniform(-.008,.008,(W,W));seam=(u<5)|(u>250)|(v<5)|(v>506)
base=np.clip(colors[tile]+noise[:,:,None],0,1);base[seam]*=.7
orm=np.ones((W,W,3));orm[:,:,0]=np.where(seam,.84,1);orm[:,:,1]=np.clip(np.array([.55,.57,.64,.19,.39,.34,.5,.72])[tile]+noise*3,0,1);orm[:,:,2]=np.array([.2,.62,.15,.38,.8,.1,.15,.55])[tile]
normal=np.zeros((W,W,3));normal[:]=(.5,.5,1);normal[:,:,0]+=np.sin(x*.6)*.008;normal[:,:,1]+=np.sin(y*.31)*.006
em=np.zeros((W,W,3));em[tile==5]=(.16,.40,.47);em[tile==6]=(.45,.10,.02)
mat=bpy.data.materials.new('C07_A_v4_shared_1k_PBR');mat.use_nodes=True;n=mat.node_tree.nodes;links=mat.node_tree.links;bs=n.get('Principled BSDF');images={}
for key,pix in [('basecolor',base),('orm',orm),('normal',normal),('emissive',em)]:
 im=bpy.data.images.new('A4_'+key,W,W);im.colorspace_settings.name='sRGB' if key in ['basecolor','emissive'] else 'Non-Color'
 rgba=np.ones((W,W,4),dtype=np.float32);rgba[:,:,:3]=np.where(pix<=.04045,pix/12.92,((pix+.055)/1.055)**2.4) if key in ['basecolor','emissive'] else pix;im.pixels.foreach_set(rgba.ravel());im.pack();images[key]=im
 tex=n.new('ShaderNodeTexImage');tex.image=im
 if key=='basecolor':links.new(tex.outputs['Color'],bs.inputs['Base Color'])
 if key=='orm':
  sep=n.new('ShaderNodeSeparateColor');links.new(tex.outputs['Color'],sep.inputs[0]);links.new(sep.outputs['Green'],bs.inputs['Roughness']);links.new(sep.outputs['Blue'],bs.inputs['Metallic'])
  # glTF exporter recognises this group as occlusion, using the same ORM image.
  group=bpy.data.node_groups.new('glTF Material Output','ShaderNodeTree');group.interface.new_socket(name='Occlusion',in_out='INPUT',socket_type='NodeSocketFloat')
  gn=n.new('ShaderNodeGroup');gn.node_tree=group;links.new(sep.outputs['Red'],gn.inputs['Occlusion'])
 if key=='normal':
  nm=n.new('ShaderNodeNormalMap');nm.inputs['Strength'].default_value=.3;links.new(tex.outputs[0],nm.inputs['Color']);links.new(nm.outputs[0],bs.inputs['Normal'])
 if key=='emissive':links.new(tex.outputs[0],bs.inputs['Emission Color']);bs.inputs['Emission Strength'].default_value=1.0
# Reuse only pure geometry helpers, never execute the old asset builder.
tree=ast.parse((HERE.parent/'c07/build_c07.py').read_text());exec(compile(ast.Module(body=[v for v in tree.body if isinstance(v,ast.FunctionDef)],type_ignores=[]),'geometry_helpers','exec'))
for ob in scene.objects:
 if ob.type=='MESH':ob.data.materials.clear();ob.data.materials.append(mat)
# Low pointed prow flows into a dorsal pressure cabin: no vertical truck windscreen.
loft('A4 forward pressure shell',[(-14.65,.60,.35),(-13.1,1.65,.85),(-10.3,2.25,1.6),(-7.0,2.35,1.75),(-5.4,1.25,1.25)],0,'crew',.12).location.z=.65
# Cockpit canopy lies on an inclined roof, distinct from the impact/sensor prow.
for s in [-1,1]:
 # Roof-following six-vertex glazing avoids a flat pane cutting through the roof break.
 pts=[(s*x,y,z) for y,w,z in [(-12.85,1.20,1.59),(-10.3,1.58,2.29),(-9.0,1.69,2.35)] for x in [.13,w]]
 mesh('A4 inclined canopy',pts,[(0,1,3,2),(2,3,5,4)],3,'crew',0)
 for i,j in [(0,1),(1,3),(3,5),(5,4),(4,2),(2,0)]:bar('A4 pressure canopy frame',pts[i],pts[j],.055,4,'crew')
 # Side cheek viewport is small, high, forward-looking; not a vehicle door window.
 pts=[(s*2.27,-10.1,1.50),(s*2.34,-7.8,1.55),(s*2.25,-7.8,2.03),(s*2.17,-10.1,1.96)]
 mesh('A4 cheek viewport',pts,[(0,1,2,3)],3,'crew',0)
 for i in range(4):bar('A4 cheek viewport frame',pts[i],pts[(i+1)%4],.045,4,'crew')
 box('A4 sensor blister',(s*.82,-13.1,.0),(.60,1.0,.36),1,'crew',.14)
 box('A4 sensor lens',(s*.82,-13.6,.02),(.30,.035,.17),3,'crew',.025)
# Rear cabin bulkhead and dorsal docking ring (Z axis), with real hollow throat.
loft('A4 crew service neck',[(-7.2,1.5,1.3),(-4.8,1.2,1.3),(-3.7,1.1,.8)],1,'crew',.10).location.z=.55

def annulus(name,center,axis,outer,inner,depth,tile=4,group='crew',segments=32):
 verts=[]
 for z in [-depth/2,depth/2]:
  for r in [outer,inner]:
   for i in range(segments):
    a=2*math.pi*i/segments;v=Vector((r*math.cos(a),r*math.sin(a),z));v=Vector(axis).to_track_quat('Z','Y')@v;verts.append(tuple(v+Vector(center)))
 faces=[]
 for i in range(segments):
  j=(i+1)%segments
  for a,b in [(0,segments),(2*segments,3*segments),(0,2*segments),(segments,3*segments)]:faces.append((a+i,a+j,b+j,b+i))
 return mesh(name,verts,faces,tile,group,.015)
annulus('A4 dorsal docking collar',(0,-5.65,2.35),(0,0,1),1.02,.76,.42)
box('A4 sealed docking hatch',(0,-5.65,2.18),(1.3,1.3,.10),1,'crew',.23)
for s in [-1,1]:bar('A4 hatch latch',(s*.48,-5.95,2.27),(s*.48,-5.35,2.27),.055,4,'crew')
loft('A4 aft power spine',[(7.6,.85,.70),(10.9,1.20,.9),(12.0,.9,.65)],1,'load_frame',.09).location.z=-.45
bar('A4 aft engine crossmember',(-3.5,10.7,-.5),(3.5,10.7,-.5),.34,4,'load_frame')
# Dual continuous thrust longerons and cross bulkheads (not a decorative center rod).
for s in [-1,1]:
 loft('A4 twin thrust longeron',[(-8.0,.28,.40),(6.5,.32,.45),(10.8,.35,.50)],4,'load_frame',.06).location=(s*1.35,0,-1.1)
 for y0 in [-3.8,4.5,8.2]:
  bar('A4 transverse load beam',(-3.7,y0,-1.25),(3.7,y0,-1.25),.22,1,'load_frame') if s<0 else None
  bar('A4 diagonal cargo brace',(s*1.35,y0-1.0,-1.1),(s*3.0,y0,.0),.12,4,'load_frame')
 # cargo is sealed against dust, UNPRESSURISED; no invented crew access through it.
 # Separate shells, recessed gasketed end doors and spaced protection frames.
 cx=s*3.9
 loft('A4 removable cargo pod',[(-5.0,1.30,1.45),(-3.9,1.72,1.90),(5.5,1.72,1.90),(6.5,1.24,1.38)],2,'cargo',.12).location=(cx,0,-.85)
 for y0,w,h in [(-4.35,1.6,1.80),(4.85,1.85,2.03)]:
  for edge in range(8):
   ob=shell_panel('A4 protective handling frame',y0-.22,y0+.22,w,h,edge,0,'cargo',.13);ob.location=(cx,0,-.85)
 # Roof access lids follow the flat load envelope; different sizes correspond to service bays.
 for yy,ll in [(-2.6,1.30),(.25,3.6),(3.45,1.65)]:
  box('A4 cargo roof gasket',(cx,yy,1.075),(2.30,ll,.07),7,'cargo',.08)
  box('A4 cargo roof cover',(cx,yy,1.12),(2.10,ll-.18,.06),0,'cargo',.07)
 # Visible side loading door and reinforced recessed perimeter, not flat orange box.
 box('A4 cargo side door gasket',(cx+s*1.70,1.0,-.85),(.08,6.3,2.35),7,'cargo',.10)
 box('A4 cargo removable access panel',(cx+s*1.77,1.0,-.85),(.08,6.05,2.10),2,'cargo',.12)
 for yy in [-1.25,3.3]:
  box('A4 cargo door latch',(cx+s*1.84,yy,-.85),(.12,.32,.70),4,'cargo',.035)
 for yy in [-3.8,4.5]:
  # Rail remains part of ship, receiver and lifting eyes stay on pod.
  box('A4 cargo receiver',(cx-s*1.67,yy,-.10),(.26,.86,.90),4,'cargo',.04)
  box('A4 cargo captive lock',(s*1.90,yy,-.10),(.65,.65,.48),1,'locks',.06)
  bar('A4 cargo locking pin',(s*1.85,yy,-.10),(cx-s*1.55,yy,-.10),.115,4,'locks')
  box('A4 lock status light',(s*1.9,yy,.17),(.32,.16,.05),5,'lights',.01)
  for xx in [cx-.9,cx+.9]:annulus('A4 cargo lifting eye',(xx,yy,1.04),(0,1,0),.18,.095,.09,4,'cargo',16)
 # Guide rail plus service walkway in the visible central gap.
 box('A4 maintenance walkway',(s*.68,1.2,.05),(.75,10.1,.20),4,'load_frame',.04)
 for yy in [-2,0,2,4]:box('A4 walkway grip plate',(s*.68,yy,.18),(.68,.80,.03),7,'load_frame',.015)
 # Engine load path, paired energy tanks and actual plumbing back to drives.
 loft('A4 drive equipment fairing',[(7.2,1.05,.75),(9.5,1.35,1.02),(11.3,1.20,.95)],0,'propulsion',.10).location=(s*3.5,0,.05)
 for yy in [8.1,10.8]:annulus('A4 nacelle thrust mount',(s*3.5,yy,.05),(0,1,0),1.27,1.03,.20,4,'propulsion')
 bar('A4 thrust diagonal',(s*1.35,5.5,-1.1),(s*3.5,9.8,.05),.24,4,'load_frame')
 bar('A4 thrust lower tie',(s*1.35,8.5,-1.1),(s*3.5,10.8,-.50),.19,4,'load_frame')
 # Tank cylinders are enclosed by cross-frame and shields, not floating greebles.
 bar('A4 propellant reservoir',(s*.65,5.8,.70),(s*.65,9.7,.70),.49,4,'services')
 bar('A4 protected feed line',(s*.65,8.9,.70),(s*3.5,9.0,.95),.095,4,'services')
 box('A4 drive service panel',(s*3.5,8.8,1.12),(1.35,1.75,.09),1,'propulsion',.12)
 # Folded radiator wings: a functional broad surface, attached to the aft frame.
 panel=box('A4 radiator panel',(s*2.35,6.35,1.65),(1.18,3.30,.16),7,'thermal',.08);panel.rotation_euler.y=s*math.radians(12)
 bar('A4 radiator hinge',(s*1.75,4.85,1.52),(s*1.75,7.85,1.52),.10,4,'thermal')
 bar('A4 radiator root',(s*1.35,6.2,-.7),(s*1.75,6.2,1.52),.10,4,'thermal')
 for yy in [5.1,5.65,6.2,6.75,7.3,7.65]:box('A4 radiator channel',(s*2.35,yy,1.77),(1.05,.045,.035),4,'thermal',.008)
 # Two RCS locations per side with transverse and vertical nozzles.
 for yy in [-10.7,10.1]:
  xx=s*(1.7 if yy<0 else 4.25);zz=-.5
  box('A4 RCS valve housing',(xx,yy,zz),(.46,.65,.55),1,'services',.08)
  annulus('A4 RCS lateral nozzle',(xx+s*.30,yy,zz),(s,0,0),.16,.095,.22,4,'services',16)
  annulus('A4 RCS vertical nozzle',(xx,yy,zz-.32),(0,0,1),.15,.085,.18,4,'services',16)
 # Geometric work-light housings. Emissive only, no extra game light or glow hull.
 for yy in [-6.8,7.4]:
  box('A4 recessed worklight housing',(s*1.2,yy,1.15),(.55,.44,.20),7,'lights',.05)
  box('A4 worklight lens',(s*1.2,yy,1.27),(.38,.26,.04),5,'lights',.025)
 box('A4 navigation marker',(s*5.60,4.9,.05),(.07,.35,.14),6 if s<0 else 5,'lights',.02)
# An elevated communications/service mast conveys an orbital craft, not a road cab.
bar('A4 dorsal comm pedestal',(0,-6.8,2.0),(0,-6.8,3.2),.12,4,'services')
box('A4 communications planar array',(0,-6.8,3.35),(1.40,.50,.22),1,'services',.08)
# Remove all unused legacy materials/images; save EDITABLE objects before draw batching.
meshes=[o for o in scene.objects if o.type=='MESH']
for ob in meshes:
 if ob.name.startswith('Recessed cold engine core'):
  # Quiescent drive: the inherited throat disk is refractory material, not a glowing front cap.
  for uv in ob.data.uv_layers.active.data:uv.uv.x += .5
  ob['atlas_tile']=7
 ob.data.materials.clear();ob.data.materials.append(mat)
 ob.data.uv_layers.active.name='AtlasUV'
 for uv in list(ob.data.uv_layers):
  if uv.name!='AtlasUV':ob.data.uv_layers.remove(uv)
for m in list(bpy.data.materials):
 if m!=mat:bpy.data.materials.remove(m)
for im in list(bpy.data.images):
 if im not in images.values() and im.users==0:bpy.data.images.remove(im)
scene['selected_option']='A';scene['a_v3_source_sha256']=OLD['source_sha256'];scene['owner_visual_approval']=False;scene['can_integrate']=False;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
bpy.ops.object.camera_add(location=(35,-42,26));cam=bpy.context.object;cam.rotation_euler=(-cam.location).to_track_quat('-Z','Y').to_euler();scene.camera=cam
bpy.context.preferences.filepaths.save_version=0
src=HERE/'source/c07_a_v4.blend';bpy.ops.wm.save_as_mainfile(filepath=str(src))
groups={}
for ob in meshes:groups.setdefault(ob['assembly'],[]).append(ob)
for group,objs in groups.items():
 bpy.ops.object.select_all(action='DESELECT')
 for ob in objs:ob.select_set(True)
 bpy.context.view_layer.objects.active=objs[0];bpy.ops.object.join();bpy.context.object.name='A4_'+group
bpy.ops.object.select_all(action='DESELECT');runtime=[o for o in scene.objects if o.type=='MESH']
for ob in runtime:ob.select_set(True)
out=OUT/'c07_a_v4.glb'
bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_texcoords=True,export_normals=True,export_materials='EXPORT',export_cameras=False,export_lights=False)
pts=[o.matrix_world@v.co for o in runtime for v in o.data.vertices];lo=[min(p[k] for p in pts) for k in range(3)];hi=[max(p[k] for p in pts) for k in range(3)]
record={'schema_version':1,'selected_option':'A','owner_visual_approval':False,'production_asset_approved':False,'release_approved':False,'can_integrate':False,'base_commit':'7946fd67139e3e728fa2f3428109b535fbd71f03','base_source_sha256':OLD['source_sha256'],'source':str(src.relative_to(ROOT)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'path':str(out.relative_to(ROOT)),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'retained_a_v3_objects':retained,'replaced_objects':removed,'dimensions_blender_xyz':[b-a for a,b in zip(lo,hi)],'triangles':sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in runtime),'surfaces':len(runtime),'materials':1,'textures':{'size':[1024,1024],'maps':['basecolor','orm','normal','emissive'],'provenance':'Original procedural seed 1504; no reference-image textures; AO is restrained atlas seam shading, not a geometry bake'},'cargo':'two unpressurised removable pods, paired receiver locks; no animated mechanism','review_status':'candidate_for_user_review'}
(OUT/'manifest.json').write_text(json.dumps(record,indent=2)+'\n');print('CANDIDATE',json.dumps(record))
