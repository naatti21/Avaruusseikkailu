"""Bounded design-choice contract. No visual approval from test results."""
import hashlib,importlib.util,json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/'native-prototype/design-review/c07-v3/manifest.json'
spec=importlib.util.spec_from_file_location('art',ROOT/'native-prototype/tools/check_production_art.py');art=importlib.util.module_from_spec(spec);spec.loader.exec_module(art)
class DesignStudyTests(unittest.TestCase):
 def test_reviewed_baseline_is_byte_identical(self):
  for name,sha in [('native-prototype/art/c07/source/c07_courier.blend','68086c196a1ec918f854e9e9522fba0b0b5da806c14536785c13c69cecd33808'),('native-prototype/production/models/c07_courier.glb','0e6eea9851d08c8764746b5b7dafc9c9a0126f1d0726a224ff8eff374122c3c0')]:
   self.assertEqual(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),sha)
 def test_choice_gate_is_unselected_and_unreleased(self):
  d=json.loads(MANIFEST.read_text());self.assertIsNone(d['selected_option']);self.assertFalse(d['release_approved'])
  self.assertEqual({x['option'] for x in d['options']},{'A','B'})
  for a in d['options']:self.assertEqual(a['review_status'],'unselected');self.assertFalse(a['can_integrate'])
 def test_sources_have_hashes_lineage_and_separate_safe_paths(self):
  for a in json.loads(MANIFEST.read_text())['options']:
   self.assertEqual(a['base_commit'],'764452a583c9c61a38ef8b229925247ad61aa2e6')
   self.assertIn('Continuous pressure hull',a['inherited_objects']);self.assertIn('Engine bell with recessed throat',a['inherited_objects'])
   self.assertTrue(a['source'].startswith('native-prototype/art/c07-v3/source/'))
   self.assertTrue(a['path'].startswith('native-prototype/design-review/c07-v3/'))
   for path,key in [('source','source_sha256'),('path','sha256')]:self.assertEqual(hashlib.sha256((ROOT/a[path]).read_bytes()).hexdigest(),a[key])
   self.assertEqual((ROOT/a['source']).read_bytes()[:7],b'BLENDER')
 def test_real_glb_geometry_and_provisional_material_budget(self):
  for a in json.loads(MANIFEST.read_text())['options']:
   g=art.read_glb(ROOT/a['path']);triangles=0;surfaces=0
   self.assertFalse(g.get('images',[]),'No new full-production texture work for the silhouette decision')
   for mesh in g['meshes']:
    for p in mesh['primitives']:
     surfaces+=1;self.assertIn('NORMAL',p['attributes']);self.assertEqual(p.get('mode',4),4)
     triangles+=g['accessors'][p['indices']]['count']//3
   self.assertEqual(triangles,a['triangles']);self.assertGreater(triangles,2000);self.assertLessEqual(triangles,100000)
   self.assertLessEqual(surfaces,32);self.assertLessEqual(len(g['materials']),8)
 def test_alternatives_are_distinct_delivered_assets(self):
  a,b=json.loads(MANIFEST.read_text())['options']
  self.assertNotEqual(a['sha256'],b['sha256']);self.assertNotEqual(a['source_sha256'],b['source_sha256'])
  for item in [a,b]:
   width,length,height=item['dimensions_blender_xyz']
   self.assertLess(abs(width-12),.75);self.assertLess(abs(length-30),.75);self.assertLess(abs(height-8),.75)
if __name__=='__main__':unittest.main()
