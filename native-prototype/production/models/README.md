# Production models — source slots (not yet populated)

Do not place old `hero_station.glb` or `courier_30m.glb` here as if they were accepted production assets.

This directory will receive:
- `c07_courier.glb` — 30m player courier (first)
- `twin_cylinder_berth.glb` — close-range docking environment (second)
- `twin_cylinder_colony.glb` — far LOD / distinct habitat silhouette (third)

When adding a candidate, update `../asset_manifest.json` with provenance, SHA256, and `review_status=candidate`. Run `python3 native-prototype/tools/check_production_art.py --require-models` only when all three are actually present; otherwise run without that flag. No one should claim visual quality from this check alone.

The actual 2D concept panels from the chat are visual source references. They are **not GLB meshes**; the production artwork must be independently modeled and inspected before Android integration.
