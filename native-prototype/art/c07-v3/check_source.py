"""Open each actual study .blend in Blender before running this checker."""
import bpy,math
s=bpy.context.scene
assert s['study_option'] in ['A','B'] and s['visual_approval']=='unselected'
assert s['base_source_sha256']=='68086c196a1ec918f854e9e9522fba0b0b5da806c14536785c13c69cecd33808'
assert s.unit_settings.system=='METRIC' and s.unit_settings.scale_length==1
meshes=[o for o in s.objects if o.type=='MESH'];inherited=[o for o in meshes if 'study_parent_object' in o]
assert len(inherited)>50
assert any(o.get('study_parent_object')=='Continuous pressure hull' for o in inherited)
assert sum(o.name.startswith('Engine bell with recessed throat') for o in meshes)==2
assert all(o.data.uv_layers and o.data.materials for o in meshes)
assert not any(n.type=='TEX_IMAGE' for m in bpy.data.materials if m.use_nodes for n in m.node_tree.nodes)
points=[o.matrix_world@v.co for o in meshes for v in o.data.vertices]
assert all(math.isfinite(x) for v in points for x in v)
d=[max(p[k] for p in points)-min(p[k] for p in points) for k in range(3)]
assert all(abs(x-target)<.75 for x,target in zip(d,[12,30,8])),d
assert sum('landing leg' in o.name for o in meshes)==4
if s['study_option']=='B':assert any('crew connection bridge' in o.name for o in meshes)
print('PASS editable study',s['study_option'],'metres',d,'inherited objects',len(inherited))
