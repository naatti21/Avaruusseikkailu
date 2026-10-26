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
