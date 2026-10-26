import importlib.util
import json
from pathlib import Path
import struct
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "check_production_art", ROOT / "native-prototype/tools/check_production_art.py")
art = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(art)
ORIGINAL = ROOT / "native-prototype/production/asset_manifest.json"


class ArtIntakeTests(unittest.TestCase):
    def test_real_manifest_remains_not_approved(self):
        result = art.validate(ORIGINAL)
        self.assertFalse(result["release_approved"])
        self.assertEqual({x["review_status"] for x in result["assets"]}, {"awaiting_artist"})

    def test_strict_fails_until_real_models_exist(self):
        with self.assertRaises(ValueError):
            art.validate(ORIGINAL, require_models=True)

    def test_missing_asset_cannot_be_claimed_as_approved(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp) / "asset_manifest.json"
            data = json.loads(ORIGINAL.read_text())
            data["assets"][0]["review_status"] = "approved"
            p.write_text(json.dumps(data))
            with self.assertRaises(ValueError):
                art.validate(p)

    def test_invalid_glb_cannot_pass(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp) / "bad.glb"
            p.write_bytes(b"not a glb")
            with self.assertRaises(ValueError):
                art.read_glb(p)

    def test_minimal_glb_header_and_embedded_scene(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp) / "ok.glb"
            raw = json.dumps({"meshes": [{"primitives": []}], "scenes": [{"nodes": [0]}]}).encode()
            raw += b" " * ((4 - len(raw) % 4) % 4)
            length = 12 + 8 + len(raw)
            p.write_bytes(struct.pack("<4sII", b"glTF", 2, length)
                          + struct.pack("<II", len(raw), 0x4E4F534A) + raw)
            self.assertEqual(len(art.read_glb(p)["meshes"]), 1)


if __name__ == "__main__":
    unittest.main()
