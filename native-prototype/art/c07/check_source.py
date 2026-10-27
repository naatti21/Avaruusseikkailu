"""Run in Blender against the delivered .blend, independently of the generator."""
import bpy, math
s=bpy.context.scene
assert s.unit_settings.system=='METRIC' and s.unit_settings.scale_length==1
meshes=[o for o in s.objects if o.type=='MESH']
assert len(meshes)>100, 'Expected editable individual components, not only collapsed export'
assert len([o for o in meshes if 'Engine bell' in o.name])==2
assert len([o for o in meshes if 'Cockpit' in o.name or 'cockpit' in o.name])>=4
assert all(o.data.uv_layers and o.data.materials for o in meshes)
images={node.image for mat in bpy.data.materials if mat.use_nodes for node in mat.node_tree.nodes if node.type=='TEX_IMAGE'}
assert len(images)==4 and all(i.packed_file for i in images)
assert {i.name for i in images}=={'C07_basecolor','C07_metalrough','C07_normal','C07_emissive'}
verts=[o.matrix_world@v.co for o in meshes for v in o.data.vertices]
assert all(math.isfinite(x) for v in verts for x in v)
d=[max(v[k] for v in verts)-min(v[k] for v in verts) for k in range(3)]
assert abs(d[0]-12)<.5 and abs(d[1]-30)<.5 and abs(d[2]-8)<.5, d
print('PASS: editable source, two bell nozzles, cockpit, UV/materials, four packed maps and metre dimensions',d)
# PR13 revision: continuity and macro-shape checks, not a visual-quality oracle.
assert s.get('revision')==2
assert s.get('source_base_sha256')=='bd390a68d404063aa8cd25ca5a160d8ebf0d110613e4bcd6078203dbc1726ded'
inherited=[o for o in meshes if 'source_object' in o]
assert len(inherited)>=450
assert any(o.get('source_object')=='Continuous pressure hull' for o in inherited)
def dimensions(group):
 points=[o.matrix_world@v.co for o in meshes if o.get('assembly')==group for v in o.data.vertices]
 return [max(v[k] for v in points)-min(v[k] for v in points) for k in range(3)]
front=dimensions('armor_1');aft=dimensions('armor_2')
assert front[1]>aft[1]*1.5, (front,aft)
assert front[0]>aft[0]+.5, (front,aft)
assert all(o.get('atlas_tile')!=0 for o in meshes if o.get('assembly')=='armor_3')
for prefix in ['Engine gimbal bearing race','Engine thrust link','Propellant manifold supply','Segmented engine thermal shield','Revised visor perimeter']:
 assert any(o.name.startswith(prefix) for o in meshes), prefix
rough=bpy.data.images['C07_metalrough']
samples=[rough.pixels[(v*1024+u)*4+1] for u in [3,20,60,120,200,250] for v in [6,80,250,400,505]]
assert max(samples)-min(samples)>.1
print('PASS: original-source lineage, differentiated shoulder width/length, aft material hierarchy, visor and propulsion assemblies, roughness variation')
