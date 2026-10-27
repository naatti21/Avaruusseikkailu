# C-07 / Issue #12 — original Blender art candidate

This is the second **unapproved model candidate**, revised from the reviewed source, not a release or an assertion of visual acceptance. Only C-07 is implemented. The berth and colony slots remain `awaiting_artist`.

## Reference and interpretation

The owner supplied `Avaruusseikkailu_Pilotti01_Konseptireferenssit.zip` (26 October 2026). Its README and all three concept images informed the silhouette; the courier crop `03_c07_aluksen_referenssi.jpg` is the direct reference. The concept is not mutually consistent orthographic CAD. The model interprets its broad chamfered pressure hull, framed dark cockpit, discontinuous pale armor collars, orange removable cargo, exposed service gaps and two deep aft engines at a real 30 × 12 × 8 metre scale. No old `courier_30m.glb` geometry is reused.

The reference raster images are **not** used as textures or substituted for Godot screenshots, and are not redistributed. The manifest records the reference crop hash. Geometry, texture pixels and the construction script are original contributions to this repository. Blender's bundled Bfont produces geometric registration lettering. No external model, asset store texture, AI image generation or downloaded sci-fi kit was used. No new third-party asset license is asserted for the owner's reference.

## Source and runtime assets

- `source/c07_courier.blend`: editable, named individual components, packed maps, metre units, review cameras. Open this directly in Blender **4.3.2**. It contains the actual mesh, not a dependency on running the generator.
- `revise_c07.py`: loads the SHA-locked original `.blend` from commit `e4c8052`, reshapes its named meshes, revises its packed maps and saves the edited source before batching. 479 original components survive. `revision_lineage.json` lists retained/removed names. It refuses an already-revised input.
- `build_c07.py`: historical first-candidate recipe and shared modeling helpers; running it alone recreates v1, not this revision. The revision imports only its function definitions, never its scene-clearing/build code. Blender save metadata can change hashes between runs; record hashes from the actual delivered files.
- `../../production/models/c07_courier.glb`: glTF 2.0, metre units; forward +Z and up +Y after import into Godot.
- `build_metrics.json`: counts measured during construction; the independent Godot test rechecks actual imported vertices and runtime surfaces.
- `source/.gdignore`: prevents Godot from automatically exporting the Blender authoring file. Only the explicit production GLB is a runtime input.

556 individually editable mesh objects become 13 runtime assembly meshes, sharing one atlas material. LOD0 contains 87,572 triangles. Four embedded 1024² PNG maps provide base color, packed metallic/roughness, tangent normal and emissive. The plain uncompressed four-map RGBA mip-chain budget is about 21.3 MiB before compression; actual GPU allocation is device-dependent. Godot import uses embedded Basis Universal textures, generated mesh LODs and shadow meshes. No exterior windows use transparent overdraw. The GLB is about 8.8 MiB, source about 10 MiB. See exact sizes and hashes in metrics/manifest.

The bevels, ports, panel layering, cargo restraints, nozzle walls, recessed engine throats, pipework, docking socket and retracted saddles are mesh geometry. Texture details are restrained surface variation, not a substitute for this shape. The cockpit uses dark opaque glazing; no cabin interior is claimed. No collision, animation or gameplay integration is included in this art-only delivery.

## Reproduce and inspect

From repository root, with Blender 4.3.2 and Godot 4.7.2 installed:

```sh
git show e4c80525ac7ef5320eeecda54839b41d909b24a6:native-prototype/art/c07/source/c07_courier.blend > /tmp/c07-reviewed-original.blend
blender --background --python native-prototype/art/c07/revise_c07.py -- /tmp/c07-reviewed-original.blend
blender --background native-prototype/art/c07/source/c07_courier.blend --python-exit-code 1 --python native-prototype/art/c07/check_source.py
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 native-prototype/tools/check_production_art.py --require-asset c07_courier
godot --headless --editor --path native-prototype --quit
godot --headless --path native-prototype --script res://tools/production_art_preview_smoke.gd
godot --headless --path native-prototype --script res://tools/c07_review.gd
```

After intentionally regenerating the model, update `sha256` and `source_sha256` in the manifest from the actual GLB/source before the contract tests. Do not change the approval state to make a check pass. The all-three-assets `--require-models` gate intentionally remains closed because the colony and berth are out of scope.

Open `native-prototype/scenes/production_art_preview.tscn` in Godot to use PR #11's orbiting inspection scene. The new capture script instantiates that same scene and same model slot, disables orbit, and records front, side, top, rear and two three-quarter views. It never substitutes another mesh. For fixed review images on a Linux desktop:

```sh
C07_CAPTURE_DIR=/tmp/c07-review xvfb-run -a -s '-screen 0 1600x1200x24' godot --audio-driver Dummy --path native-prototype --rendering-method gl_compatibility --script res://tools/c07_review.gd -- --capture
```

The capture pass explicitly sets a landscape viewport, neutral studio reflections, key/fill lighting and mesh shadows. This is a controlled art-review setup, not a claim about in-game lighting or Android performance. `docs/c07-pilot/` contains the actual Godot output, not Blender renders. The production-art-intake CI workflow repeats technical tests/captures and packages the source/GLB as a review artifact; a successful local run is not evidence of remote CI success.

## PR13 visual-review revision

The fore shoulder is now wider/longer than the aft shoulder; the tail narrows and its armor is dark machinery plating. Cockpit frames are remapped to the glazing surface rather than partly intersecting the hull. Engine gimbal races, thrust links, feed loops and cooling manifolds are placed in visible service space. Existing maps receive seam grime, restrained paint repair/abrasion and spatial roughness variation; no image reference is baked onto the model.

Add `--game-lighting` to the capture command to render two extra views with the actual `main.gd::_build_lights()` function. It is called on an off-tree instance so gameplay `_ready()` and storage do not run. No copied lighting constants or studio fill remain in that mode. This isolates material readability under native-game lighting without integrating the model into gameplay. The studio camera directions, projection, viewport, lights and framing algorithm stay unchanged for before/after comparison.
