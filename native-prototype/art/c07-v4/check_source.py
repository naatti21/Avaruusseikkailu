"""Run after opening the actual delivered .blend, not only the generator."""
import bpy,math,json,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[3]
s=bpy.context.scene;m=json.loads((root/'native-prototype/design-review/c07-v4/manifest.json').read_text())
assert s['selected_option']=='A' and not s['owner_visual_approval'] and not s['can_integrate']
assert s['a_v3_source_sha256']==m['base_source_sha256']
assert s.unit_settings.scale_length==1 and s.unit_settings.system=='METRIC'
meshes=[o for o in s.objects if o.type=='MESH']
assert len(meshes)>100,'editable separate components retained'
for prefix,count in [('A4 removable cargo pod',2),('A4 cargo captive lock',4),('A4 cargo locking pin',4),('A4 cargo receiver',4),('A4 twin thrust longeron',2),('A4 radiator panel',2),('A4 propellant reservoir',2),('A4 inclined canopy',2),('A4 RCS lateral nozzle',4),('A4 RCS vertical nozzle',4),('Engine bell with recessed throat',2)]:
 assert sum(o.name.startswith(prefix) for o in meshes)==count,prefix
assert all(len(o.data.uv_layers)==1 and o.data.uv_layers[0].name=='AtlasUV' and len(o.data.materials)==1 for o in meshes), 'single shared atlas UV layer before assembly batching'
pts=[o.matrix_world@v.co for o in meshes for v in o.data.vertices]
assert all(math.isfinite(x) for p in pts for x in p)
d=[max(p[k] for p in pts)-min(p[k] for p in pts) for k in range(3)]
assert all(abs(a-b)<.75 for a,b in zip(d,[12,30,8])),d
assert len([im for im in bpy.data.images if im.name.startswith('A4_')])==4
assert all(im.size[:]==(1024,1024) and im.packed_file for im in bpy.data.images if im.name.startswith('A4_'))
# Lock pins must physically bridge both receiver/ship lock bounds on X.
def bound(ob,k):
 p=[(ob.matrix_world@v.co)[k] for v in ob.data.vertices];return min(p),max(p)
locks=[o for o in meshes if o.name.startswith('A4 cargo captive lock')];receivers=[o for o in meshes if o.name.startswith('A4 cargo receiver')]
for pin in [o for o in meshes if o.name.startswith('A4 cargo locking pin')]:
 p=pin.matrix_world.translation
 # Mesh helper origin is centered; associate by geometric Y and side.
 px=bound(pin,0);py=sum(bound(pin,1))/2
 for pool in [locks,receivers]:
  same=[o for o in pool if abs(sum(bound(o,1))/2-py)<.1 and sum(bound(o,0))*sum(px)>0]
  assert len(same)==1
  b=bound(same[0],0);assert min(px[1],b[1])-max(px[0],b[0])>.01,'disconnected lock pin'
print('PASS A4 actual editable source, lineage, UV/PBR, lock contact, paired structures; dimensions',d)

# Independent spatial check: glazing must sit above, not intersect, the actual pressure shell.
from mathutils import Vector
from mathutils.bvhtree import BVHTree
hull=bpy.data.objects['A4 forward pressure shell']
bvh=BVHTree.FromObject(hull,bpy.context.evaluated_depsgraph_get())
for ob in [o for o in meshes if o.name.startswith('A4 inclined canopy')]:
 for vertex in ob.data.vertices:
  p=ob.matrix_world@vertex.co
  origin=hull.matrix_world.inverted()@Vector((p.x,p.y,10))
  hit,normal,index,distance=bvh.ray_cast(origin,Vector((0,0,-1)))
  assert hit is not None,'canopy not over pressure cabin'
  roof=hull.matrix_world@hit
  assert .015 < p.z-roof.z < .16,('glazing clearance',p.z-roof.z)
print('PASS canopy clears the actual sloping pressure shell')
