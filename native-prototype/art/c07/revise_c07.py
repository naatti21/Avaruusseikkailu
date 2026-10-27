"""PR13 targeted art revision. Edits the delivered Blender source in place.
Usage: blender --background --python revise_c07.py -- /path/to/e4c8052.blend
The input is hash-locked; obtain it with git show e4c8052:.../c07_courier.blend.
This is not a regenerated replacement ship. Existing named meshes are reshaped.
"""
import ast, bpy, math, json, hashlib, sys
from pathlib import Path
from mathutils import Vector, Matrix
import numpy as np
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
SOURCE=HERE/'source/c07_courier.blend'
OUT=ROOT/'native-prototype/production/models/c07_courier.glb'
base=Path(sys.argv[sys.argv.index('--')+1])
BASE_HASH='bd390a68d404063aa8cd25ca5a160d8ebf0d110613e4bcd6078203dbc1726ded'
assert hashlib.sha256(base.read_bytes()).hexdigest()==BASE_HASH, 'Use the reviewed e4c8052 source, not a repeated revision'
bpy.ops.wm.open_mainfile(filepath=str(base))
scene=bpy.context.scene
mat=bpy.data.materials['C07_shared_1k_PBR_atlas']
parts=[]
# Reuse modeling/UV helpers only, never execute the original scene deletion/build.
tree=ast.parse((HERE/'build_c07.py').read_text())
exec(compile(ast.Module(body=[x for x in tree.body if isinstance(x,ast.FunctionDef)],type_ignores=[]),str(HERE/'build_c07.py'),'exec'))
original={o.name for o in scene.objects if o.type=='MESH'}
removed=[]
def delete(ob):
 removed.append(ob.name);bpy.data.objects.remove(ob,do_unlink=True)
def recolor(ob,tile):
 old=int(ob.get('atlas_tile',0))
 for uv in ob.data.uv_layers.active.data:
  uv.uv.x+=(tile%4-old%4)/4;uv.uv.y+=(tile//4-old//4)/2
 ob['atlas_tile']=tile

# Continuous structural deformation: wide fore cargo saddle, staggered aft shoulder,
# narrower machinery tail. Every connected inherited detail follows its parent section.
ys=[-15,-10,-7.4,-5.5,-2.3,4.3,7.2,10.3,11.8,15]
newys=[-15,-10,-7.5,-6.2,-2.6,5.3,7.15,10.6,11.8,15]
def shape(p):
 x,y,z=p;ny=float(np.interp(y,ys,newys))
 sx=float(np.interp(ny,[-15,-11,-9,-6.2,-2.6,0,3,5.3,7.15,10,12,15],[1,.96,.9,1,1,.94,.94,.94,.91,.86,.87,1]))
 sz=float(np.interp(ny,[-15,-10,-7,-6.2,-2.6,2,5.3,7.15,12,15],[1,.96,.91,1,1,.96,.91,.88,.88,1]))
 return Vector((x*sx,ny,z*sz))
for ob in list(scene.objects):
 if ob.type!='MESH':continue
 ob['source_object']=ob.name
 # Remove repetitive fine tubing replaced by an actual gimbal/feed system below.
 if ob.name.startswith('Engine external cooling tube'):
  delete(ob);continue
 # Four paired corner mounts per belt remain; eliminate redundant radial struts.
 if ob.name.startswith('Armor radial attachment'):
  index=0 if '.' not in ob.name else int(ob.name.rsplit('.',1)[1])
  if index%2:delete(ob);continue
 if ob.name.startswith(('Visor armored mullion','Visor cross mullion')):
  delete(ob);continue
 if ob.name.startswith('Cockpit side glazing'):
  side=1 if sum(v.co.x for v in ob.data.vertices)>0 else -1
  coords=[(side*2.83,-14.72,.15),(side*3.88,-11.7,.20),(side*3.88,-11.7,1.78),(side*2.83,-14.72,1.35)]
  for v,p in zip(ob.data.vertices,coords):v.co=p
 engine=ob['assembly']=='engines' or ob.name.startswith('Recessed cold engine core')
 if not engine:
  inverse=ob.matrix_world.inverted()
  for v in ob.data.vertices:v.co=inverse@shape(ob.matrix_world@v.co)
  # Recompute normals after the non-uniform shape edit; do not retain stale split normals.
  ob.data.normals_split_custom_set([(0,0,0)]*len(ob.data.loops))
  ob.data.update()
 # Colored hierarchy, not four identical white rings. Keep only purposeful shoulder armor.
 group=ob['assembly']
 if group=='armor_3' and ob.get('atlas_tile')==0:recolor(ob,4)
 if group=='armor_0' and ('facet 0' in ob.name or 'facet 4' in ob.name or 'Dorsal access' in ob.name):recolor(ob,1)
 if group=='armor_2' and 'facet 4' in ob.name:recolor(ob,1)
 # Rear cargo receives weathered machinery plating; orange belongs to the main load bay.
 if ob.name.startswith('Cargo cassette 2'):recolor(ob,4)

# Layered cockpit glazing frame and cheek armor following the original window locations.
for side in [-1,1]:
 coords=[shape(p) for p in [(side*2.83,-14.72,.15),(side*3.88,-11.7,.20),(side*3.88,-11.7,1.78),(side*2.83,-14.72,1.35)]]
 for i in range(4):bar('Revised visor perimeter',coords[i],coords[(i+1)%4],.085,4,'cockpit')
 bar('Revised visor separator',coords[0].lerp(coords[1],.55),coords[3].lerp(coords[2],.55),.06,0,'cockpit')
 # Chamfered layered nose cheeks, purposeful protection of the light/sensor recess.
 points=[(side*2.76,-14.68,-1.22),(side*3.7,-11.75,-1.62),(side*3.75,-11.75,-.65),(side*2.8,-14.68,-.38)]
 verts=[shape(p) for p in points]
 verts+= [v+Vector((side*.13,0,0)) for v in verts]
 mesh('Armored sensor cheek',verts,[(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)],4,'cockpit',.045)
 bar('Brow armor edge',shape((side*.14,-14.55,1.86)),shape((side*2.24,-14.55,1.86)),.12,1,'cockpit')
 # Visible service recess below windshield, not a painted window placeholder.
 box('Nose sensor bezel',(side*1.17,-14.78,-.75),(1.13,.10,.33),1,'cockpit',.045)
 box('Nose sensor optic',(side*1.17,-14.85,-.75),(.75,.035,.12),3,'cockpit',.02)
# Three overlapping keel/rib guards establish a longitudinal line, not square hoop outlines.
for side in [-1,1]:
 for y,w in [(-4.2,5.85),(1.5,4.9),(8.2,4.2)]:
  a=(side*w,y-1.5,-2.55);b=(side*(w-.3),y+1.5,-2.5)
  bar('Cargo load path rail',a,b,.115,4,'keel')
# Aft propulsion integration: twin gimbal races, struts, feed manifolds and heat shields.
for x in [-2.55,2.55]:
 bpy.ops.mesh.primitive_torus_add(major_segments=40,minor_segments=6,major_radius=2.10,minor_radius=.12,location=(x,13.05,0),rotation=(math.pi/2,0,0))
 finish(bpy.context.object,'Engine gimbal bearing race',4,'engines',0)
 for a in [math.pi/2,math.pi*7/6,math.pi*11/6]:
  radial=Vector((math.cos(a),0,math.sin(a)))
  front=Vector((x,12.72,0))+radial*1.65;back=Vector((x,14.2,0))+radial*2.22
  bar('Engine thrust link',front,back,.12,1,'engines')
  bar('Gimbal actuator rod',front.lerp(back,.4),back,.065,4,'engines')
 # Two feed loops connecting dorsal machinery to engine casing.
 for sign in [-1,1]:
  a=(x+sign*.85,9.6,3.2);b=(x+sign*.95,12.8,3.25);c=(x+sign*1.50,13.35,1.3)
  bar('Propellant manifold supply',a,b,.115,4,'engines');bar('Propellant manifold elbow',b,c,.115,4,'engines')
 box('Engine service manifold',(x,10.15,3.1),(1.3,1.85,.5),1,'engines',.12)
 for y in [9.6,9.85,10.1,10.35,10.6]:box('Manifold cooling vane',(x,y,3.40),(1.05,.07,.15),4,'engines',.01)
 for i in range(8):
  a=(i+.08)*math.tau/8;b=(i+.92)*math.tau/8
  vs=[(x+r*math.cos(t),y,r*math.sin(t)) for y,r in [(12.5,2.03),(14.15,1.94)] for t in [a,b]]
  # Shell wall is closed with a 6cm inner skin.
  vs += [(vx-.06*math.cos(t),vy,vz-.06*math.sin(t)) for (vx,vy,vz),t in zip(vs,[a,b,a,b])]
  mesh('Segmented engine thermal shield',vs,[(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)],1,'engines',.015)
# A deliberate replaced plate breaks mirror symmetry and communicates maintenance.
box('Replaced port access cover',(-5.99,-4.05,-.62),(.07,1.55,.86),4,'armor_1',.06)
# Geometry maintenance labels, restrained and located at actual access/cargo interfaces.
for side in [-1,1]:
 bpy.ops.object.text_add(location=(side*5.22,-.95,.8))
 ob=bpy.context.object;ob.data.body='CARGO / 02';ob.data.size=.27;ob.data.extrude=.001
 ob.rotation_euler=Matrix(((0,0,side),(side,0,0),(0,1,0))).to_euler()
 bpy.ops.object.convert(target='MESH');finish(bpy.context.object,'Cargo access stencil',0,'markings',0)

# Rework existing four packed atlas maps. Dirt follows seams, repaired paint and vent areas;
# random noise is only sub-pixel surface grain, never a source of geometry/detail placement.
W=1024;yy,xx=np.mgrid[:W,:W];tile=xx//256+(yy//512)*4;u=xx%256;v=yy%512
edge=np.minimum.reduce([u,255-u,v*.5,(511-v)*.5])
grime=np.exp(-edge/15)*.34
streak=(np.sin(u*.13+np.sin(v*.017)*.6)*.5+.5)*np.exp(-edge/38)*.13
noise=np.random.default_rng(1307).uniform(-.009,.009,(W,W))
colors=[(.43,.445,.415),(.09,.112,.12),(.39,.205,.068),(.025,.073,.102),(.27,.29,.275),(.65,.79,.85),(.82,.35,.065),(.027,.033,.034)]
basepix=np.array(colors)[tile]*(1-grime[:,:,None]-streak[:,:,None])+noise[:,:,None]
# Visible panel-scale variation and localized repaired paint, without dirtying the glass.
basepix*= (0.94+.09*np.sin(v*.006)+.035*np.cos(u*.022))[:,:,None]
patch=(tile==0)&(u>175)&(u<226)&(v>135)&(v<195)
basepix[patch]*=1.16
# Edge abrasion and fastener-area wear against darker seam dirt.
wear=(edge>5)&(edge<8)&(((u*3+v*7)%53)<20)&(tile!=3)
basepix[wear]=np.array([.34,.35,.33])
# Muted registration/maintenance strips on the cargo material, not saturated toy orange.
band=(tile==2)&(v>400)&(v<421)
basepix[band]*=.34
orm=np.ones((W,W,3));orm[:,:,1]=np.clip(np.array([.57,.56,.65,.18,.43,.3,.4,.8])[tile]+grime*.55+streak*.4+noise*2,.12,.92)
orm[:,:,2]=np.array([.22,.7,.22,.55,.83,.1,.2,.62])[tile]*(1-grime)
normal=np.ones((W,W,3));normal[:]=(.5,.5,1);normal[:,:,0]+=np.sin(xx*.7)*.006;normal[:,:,1]+=np.sin(yy*.3)*.006
normal[edge<4,0]=.53
em=np.zeros((W,W,3));em[tile==5]=(.10,.35,.6);em[tile==6]=(.7,.13,.012)
# Glazing has a subtle coating gradient; actual silhouette/mullions remain mesh work.
basepix[tile==3]*=(.8+.25*np.sin(v[tile==3]*.006))[:,None]
for name,pixels in [('basecolor',basepix),('metalrough',orm),('normal',normal),('emissive',em)]:
 im=bpy.data.images['C07_'+name];rgba=np.ones((W,W,4),dtype=np.float32);rgba[:,:,:3]=np.clip(pixels,0,1)
 im.pixels.foreach_set(rgba.ravel());im.update();im.pack()
scene['revision']=2;scene['source_base_sha256']=BASE_HASH
scene['source_base_commit']='e4c80525ac7ef5320eeecda54839b41d909b24a6'
scene['visual_approval']='candidate_only'
meshes=[o for o in scene.objects if o.type=='MESH']
retained=[o['source_object'] for o in meshes if 'source_object' in o]
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
source_count=len(meshes)
# Export the revised source with the original batching contract.
groups={}
for ob in meshes:groups.setdefault(ob['assembly'],[]).append(ob)
for group,objects in groups.items():
 bpy.ops.object.select_all(action='DESELECT')
 for ob in objects:ob.select_set(True)
 bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();bpy.context.object.name='C07_'+group
bpy.ops.object.select_all(action='DESELECT');meshes=[o for o in scene.objects if o.type=='MESH']
for ob in meshes:ob.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(OUT),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_texcoords=True,export_normals=True,export_materials='EXPORT',export_cameras=False,export_lights=False)
verts=[o.matrix_world@v.co for o in meshes for v in o.data.vertices]
stats={'blender':bpy.app.version_string,'revision':2,'source_objects':source_count,'retained_source_objects':len(retained),'base_source_sha256':BASE_HASH,'runtime_meshes':len(meshes),'triangles':sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in meshes),'dimensions_blender_xyz_m':[max(v[k] for v in verts)-min(v[k] for v in verts) for k in range(3)],'texture_size':1024,'texture_maps':4,'glb_bytes':OUT.stat().st_size,'glb_sha256':hashlib.sha256(OUT.read_bytes()).hexdigest(),'blend_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest()}
(HERE/'build_metrics.json').write_text(json.dumps(stats,indent=2)+'\n')
(HERE/'revision_lineage.json').write_text(json.dumps({'base_commit':scene['source_base_commit'],'base_source_sha256':BASE_HASH,'retained_objects':retained,'removed_objects':removed},indent=2)+'\n')
print('C07_REVISION',json.dumps(stats))
