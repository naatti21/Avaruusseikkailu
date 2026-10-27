#!/usr/bin/env python3
"""Independent art intake guard. NO automated visual-quality approval.
Usage: python3 native-prototype/tools/check_production_art.py [--require-models]
"""
import argparse
import json
from pathlib import Path
import struct
import sys

PROJECT = Path(__file__).resolve().parents[2]
MANIFEST = PROJECT / "native-prototype/production/asset_manifest.json"
REQUIRED = {"c07_courier", "twin_cylinder_colony", "twin_cylinder_berth"}
STATES = {"awaiting_artist", "candidate", "approved"}
GLB_HEADER = struct.Struct("<4sII")
CHUNK_HEADER = struct.Struct("<II")
JSON_CHUNK = 0x4E4F534A


def read_glb(path: Path):
    data = path.read_bytes()
    if len(data) < 20:
        raise ValueError(f"{path}: truncated GLB")
    magic, version, byte_length = GLB_HEADER.unpack_from(data, 0)
    if magic != b"glTF" or version != 2 or byte_length != len(data):
        raise ValueError(f"{path}: invalid GLB v2 header")
    chunk_size, chunk_kind = CHUNK_HEADER.unpack_from(data, 12)
    if chunk_kind != JSON_CHUNK or 20 + chunk_size > len(data):
        raise ValueError(f"{path}: invalid JSON chunk")
    gltf = json.loads(data[20:20 + chunk_size].decode("utf-8").strip())
    if not gltf.get("meshes") or not gltf.get("scenes"):
        raise ValueError(f"{path}: no scenes/meshes")
    for image in gltf.get("images", []):
        if "uri" in image:
            raise ValueError(f"{path}: external images are forbidden; embed PBR resources")
        if "bufferView" not in image:
            raise ValueError(f"{path}: image missing embedded bufferView")
    return gltf


def validate(manifest_path=MANIFEST, *, require_models=False, require_asset=None):
    if require_asset is not None and require_asset not in REQUIRED:
        raise ValueError("Unknown required asset")
    manifest_path = Path(manifest_path)
    project = manifest_path.resolve().parents[2] if manifest_path.name == "asset_manifest.json" else PROJECT
    info = json.loads(manifest_path.read_text(encoding="utf-8"))
    if info.get("schema_version") != 1:
        raise ValueError("Unknown production asset contract version")
    if info.get("release_approved") is not False:
        raise ValueError("Release gate must remain false; this is an unapproved art pilot")
    assets = info.get("assets")
    if not isinstance(assets, list) or {a.get("id") for a in assets} != REQUIRED:
        raise ValueError("Pilot must contain exactly three required assets")
    for asset in assets:
        ident = asset["id"]
        status = asset.get("review_status")
        if status not in STATES:
            raise ValueError(f"{ident}: unrecognized art review state")
        raw = asset.get("path")
        expected = f"native-prototype/production/models/{ident}.glb"
        if raw != expected:
            raise ValueError(f"{ident}: expected safe committed asset path {expected}")
        dimensions = asset.get("dimensions_m", {})
        if any(not isinstance(dimensions.get(k), (int, float)) or dimensions[k] <= 0
               for k in ("length", "width", "height")):
            raise ValueError(f"{ident}: invalid nominal metre dimensions")
        resource = project / raw
        exists = resource.is_file()
        if (require_models or ident == require_asset) and not exists:
            raise ValueError(f"{ident}: missing production GLB")
        if not exists:
            if status != "awaiting_artist" or asset.get("source_record") is not None:
                raise ValueError(f"{ident}: cannot claim candidate/approval without the file")
            print(f"PENDING ART: {ident}, no model (correctly blocked)")
            continue
        if status == "awaiting_artist":
            raise ValueError(f"{ident}: model exists but has no candidate review status")
        record = asset.get("source_record")
        if not isinstance(record, dict) or not all(record.get(x) for x in ("author", "license", "source", "sha256")):
            raise ValueError(f"{ident}: complete asset provenance required")
        import hashlib
        actual = hashlib.sha256(resource.read_bytes()).hexdigest()
        if actual.lower() != record["sha256"].lower():
            raise ValueError(f"{ident}: GLB checksum mismatch")
        gltf = read_glb(resource)
        pbr = [m for m in gltf.get("materials", [])
               if "normalTexture" in m and
               "metallicRoughnessTexture" in m.get("pbrMetallicRoughness", {}) and
               "baseColorTexture" in m.get("pbrMetallicRoughness", {})]
        if not pbr:
            raise ValueError(f"{ident}: no PBR material with base/roughness/normal maps")
        if status == "approved":
            print(f"TECHNICAL PASS (visual approval recorded separately): {ident}")
        else:
            print(f"TECHNICAL PASS, VISUAL REVIEW STILL NEEDED: {ident}")
    print("Art intake manifest valid. NO visual or Android performance approval implied.")
    return info


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--require-models", action="store_true")
    p.add_argument("--require-asset", choices=sorted(REQUIRED))
    args = p.parse_args()
    try:
        validate(require_models=args.require_models, require_asset=args.require_asset)
    except (ValueError, KeyError, OSError, json.JSONDecodeError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
