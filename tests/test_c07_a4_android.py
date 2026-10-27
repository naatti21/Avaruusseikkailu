"""Same C-07 A4 source model, no release, independent mobile inspection scene."""
import hashlib,json,unittest
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]/"native-prototype"
class C07A4AndroidTests(unittest.TestCase):
 def test_model_identity_and_not_approved(self):
  d=json.loads((BASE/"design-review/c07-v4/manifest.json").read_text())
  self.assertEqual(hashlib.sha256((BASE/"design-review/c07-v4/c07_a_v4.glb").read_bytes()).hexdigest(),d["sha256"])
  for k in ("owner_visual_approval","production_asset_approved","release_approved","can_integrate"):self.assertFalse(d[k],k)
 def test_separate_scene_does_not_change_game(self):
  s=(BASE/"scripts/c07_a4_android_benchmark.gd").read_text()
  self.assertIn("res://design-review/c07-v4/c07_a_v4.glb",s)
  self.assertIn("set_lighting",s)
  self.assertIn("set_view",s)
  self.assertIn("samples_ms",s)
  self.assertIn('run/main_scene="res://scenes/main.tscn"',(BASE/"project.godot").read_text())
 def test_disposable_dual_export(self):
  s=(BASE/"tools/build_c07_a4_android.py").read_text()
  self.assertIn("shutil.copytree",s)
  self.assertIn('("mobile","mobile","Mobile")',s)
  self.assertIn('("compat","gl_compatibility","GL Compatibility")',s)
if __name__=="__main__":unittest.main()
