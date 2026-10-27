"""Issue 15 delivery contracts; cannot approve appearance or phone performance."""
import hashlib,importlib.util,json,unittest,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DIR=ROOT/'native-prototype/design-review/c07-v4'
spec=importlib.util.spec_from_file_location('art4',ROOT/'native-prototype/tools/check_production_art.py');art=importlib.util.module_from_spec(spec);spec.loader.exec_module(art)
class A4Tests(unittest.TestCase):
 def setUp(self):self.m=json.loads((DIR/'manifest.json').read_text());self.g=art.read_glb(ROOT/self.m['path'])
 def test_all_three_predecessors_are_preserved(self):
  for p,sha in json.loads((ROOT/'native-prototype/art/c07-v4/preserved-assets.json').read_text()).items():self.assertEqual(hashlib.sha256((ROOT/p).read_bytes()).hexdigest(),sha,p)
 def test_selection_is_not_approval(self):
  self.assertEqual(self.m['selected_option'],'A')
  for k in ['owner_visual_approval','production_asset_approved','release_approved','can_integrate']:self.assertIs(self.m[k],False,k)
  self.assertEqual(self.m['review_status'],'candidate_for_user_review')
 def test_real_source_lineage_and_export_hashes(self):
  old=json.loads((DIR.parent/'c07-v3/manifest.json').read_text())['options'][0]
  self.assertEqual(self.m['base_source_sha256'],old['source_sha256'])
  self.assertIn('A structural keel',self.m['retained_a_v3_objects'])
  for p,h in [('source','source_sha256'),('path','sha256')]:self.assertEqual(hashlib.sha256((ROOT/self.m[p]).read_bytes()).hexdigest(),self.m[h])
 def test_runtime_geometry_and_material_budget(self):
  prim=[p for mesh in self.g['meshes'] for p in mesh['primitives']]
  triangles=sum(self.g['accessors'][p['indices']]['count']//3 for p in prim)
  self.assertEqual(triangles,self.m['triangles']);self.assertLessEqual(triangles,70000)
  self.assertEqual(len(prim),self.m['surfaces']);self.assertLessEqual(len(prim),12)
  for p in prim:
   self.assertIn('NORMAL',p['attributes']);self.assertIn('TEXCOORD_0',p['attributes'])
  self.assertEqual(len(self.g['materials']),1)
 def test_embedded_pbr_with_real_normal_and_occlusion(self):
  m=self.g['materials'][0]
  self.assertIn('baseColorTexture',m['pbrMetallicRoughness']);self.assertIn('metallicRoughnessTexture',m['pbrMetallicRoughness'])
  for k in ['normalTexture','occlusionTexture','emissiveTexture']:self.assertIn(k,m)
  self.assertEqual(len(self.g['images']),4)
  self.assertTrue(all('bufferView' in x and 'uri' not in x for x in self.g['images']))
 def test_geometry_assemblies_remain_inspectable(self):
  names={x.get('name') for x in self.g['nodes']}
  for assembly in ['crew','cargo','locks','load_frame','thermal','services','propulsion']:self.assertIn('A4_'+assembly,names)
  self.assertFalse(self.g.get('cameras'));self.assertNotIn('KHR_lights_punctual',self.g.get('extensions',{}))
 def test_render_evidence_matches_actual_assets(self):
  for version,path in [('A3',ROOT/'native-prototype/design-review/c07-v3/c07_option_a.glb'),('A4',ROOT/self.m['path'])]:
   sha=hashlib.sha256(path.read_bytes()).hexdigest()
   for mode,views in [('studio',['front','side','top','rear','three-quarter','rear-quarter']),('game',['three-quarter','rear-quarter']),('closeups',['cockpit','cargo-locks','propulsion'])]:
    directory=ROOT/'docs/c07-v4'/version/mode
    metrics=json.loads((directory/'metrics.json').read_text())
    self.assertEqual(metrics['model_sha256'],sha)
    self.assertEqual(set(metrics['views']),set(views))
    self.assertIs(metrics['owner_visual_approval'],False)
    self.assertEqual(metrics['lighting'],'main.gd::_build_lights' if mode=='game' else 'studio')
    for view in views:
     raw=(directory/(view+'.png')).read_bytes()
     self.assertEqual(raw[:8],b'\x89PNG\r\n\x1a\n')
     self.assertEqual(struct.unpack('>II',raw[16:24]),(1440,1000))
if __name__=='__main__':unittest.main()
