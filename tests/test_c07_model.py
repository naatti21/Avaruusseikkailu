"""Independent GLB contract checks on delivered bytes, not builder counters."""
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import unittest
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('art',ROOT/'native-prototype/tools/check_production_art.py')
art=importlib.util.module_from_spec(spec);spec.loader.exec_module(art)
GLB=ROOT/'native-prototype/production/models/c07_courier.glb'

class C07ModelTests(unittest.TestCase):
 def test_editable_blender_source_matches_provenance(self):
  a=json.loads((ROOT/'native-prototype/production/asset_manifest.json').read_text())['assets'][0]
  source=ROOT/a['source_record']['source']
  self.assertEqual(source.read_bytes()[:7],b'BLENDER')
  self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(),a['source_record']['source_sha256'])
  self.assertFalse(source.name.startswith('courier_30m'))
 def test_glb_has_real_geometry_normals_uv_and_bounded_cost(self):
  g=art.read_glb(GLB)
  self.assertLessEqual(len(g['meshes']),20)
  self.assertGreaterEqual(len(g['meshes']),8)
  triangles=0
  for m in g['meshes']:
   for p in m['primitives']:
    self.assertEqual(p.get('mode',4),4)
    for k in ['POSITION','NORMAL','TEXCOORD_0']: self.assertIn(k,p['attributes'])
    count=g['accessors'][p['indices']]['count']
    self.assertEqual(count%3,0)
    triangles+=count//3
  self.assertGreater(triangles,10000)
  self.assertLessEqual(triangles,100000)
  self.assertLess(GLB.stat().st_size,12*1024*1024)
 def test_maps_are_embedded_and_all_materials_use_full_pbr(self):
  g=art.read_glb(GLB)
  self.assertEqual(len(g['materials']),1)
  self.assertEqual(len(g['images']),4)
  for m in g['materials']:
   self.assertIn('baseColorTexture',m['pbrMetallicRoughness'])
   self.assertIn('metallicRoughnessTexture',m['pbrMetallicRoughness'])
   self.assertIn('normalTexture',m)
   self.assertIn('emissiveTexture',m)
  # Read embedded PNG headers independently: all maps must be 1024 square.
  raw=GLB.read_bytes(); json_len=struct.unpack_from('<I',raw,12)[0]
  binary_start=20+json_len+8
  for image in g['images']:
   self.assertNotIn('uri',image)
   view=g['bufferViews'][image['bufferView']]
   start=binary_start+view.get('byteOffset',0)
   png=raw[start:start+view['byteLength']]
   self.assertEqual(png[:8],b'\x89PNG\r\n\x1a\n')
   self.assertEqual(struct.unpack_from('>II',png,16),(1024,1024))
 def test_functional_assemblies_survive_export(self):
  names={x.get('name') for x in art.read_glb(GLB)['nodes']}
  for n in ['C07_cockpit','C07_engines','C07_cargo','C07_keel','C07_dorsal','C07_markings']:
   self.assertIn(n,names)
 def test_c07_gate_does_not_claim_station_or_berth(self):
  d=art.validate(require_asset='c07_courier')
  self.assertFalse(d['release_approved'])
  with self.assertRaisesRegex(ValueError,'missing production GLB'):
   art.validate(require_models=True)

if __name__=='__main__': unittest.main()
