# C-07 v3 — A/B silhouette studies, not production assets

Two alternative mass-distribution designs based on the owner's original C-07 concept and the editable source reviewed in PR #13. Option **A is selected for further design only**, not approved as finished art and not integrated. B stays as separate reference. The original production candidate remains byte-identical.

- **A / compact industrial courier:** centered crew cabin, exposed longitudinal keel, two low removable side cargo modules, swept load paths and paired aft drives.
- **B / asymmetric utility courier:** port-side crew cabin and main/secondary cargo, starboard service/drive spine, staggered main/auxiliary engines, structural crossbeams and a folded service gantry.

The same source cockpit, cropped forward pressure hull, two cassette meshes and engine components are retained and reshaped. New coarse structural masses replace the constant box body. Some inherited fine engine detail remains, but no new micro-detail pass or full texture work was undertaken. Seven provisional flat materials communicate crew/cargo/structure/glazing; the palette is authored in sRGB and converted to linear shader values. These are design studies, not completed UV/PBR production assets.

## Files and provenance

- `source/c07_option_a.blend` and `source/c07_option_b.blend`: editable separate sources; metre units and named components.
- `../../design-review/c07-v3/c07_option_a.glb` and `c07_option_b.glb`: runtime geometry used by the capture script.
- `../../design-review/c07-v3/manifest.json`: hashes, counts, source lineage, dimensions and design-only/release gates. `../../design-review/c07-v3/selection.json` is the durable owner decision source.
- `build_options.py`: reads a hash-locked copy of the existing C-07 source; never writes that input or the production candidate. It imports only geometry-helper function definitions from the original recipe, not the scene-clearing/build code.
- `check_source.py`: independent source reopen/lineage/material/scale checks.
- `../../tools/c07_design_review.gd`: isolated Godot inspection using PR #11's preview infrastructure. It renders A, B or the unchanged baseline. The default main scene is untouched.

Base source: commit `764452a583c9c61a38ef8b229925247ad61aa2e6`, SHA-256 `68086c196a1ec918f854e9e9522fba0b0b5da806c14536785c13c69cecd33808`. The original user-supplied `Avaruusseikkailu_Pilotti01_Konseptireferenssit.zip` was visually consulted; it is not redistributed or used as a texture. No external model, texture library or generated 2D art was used. New contributions inherit the repository's original project-art provenance; no license to redistribute the reference image is assumed.

## Reproduce

Use Blender **4.3.2** and Godot **4.7.2**. From repository root:

```sh
git show 764452a583c9c61a38ef8b229925247ad61aa2e6:native-prototype/art/c07/source/c07_courier.blend > /tmp/c07-v3-base.blend
blender --background --python native-prototype/art/c07-v3/build_options.py -- /tmp/c07-v3-base.blend
for option in a b; do
  blender --background "native-prototype/art/c07-v3/source/c07_option_$option.blend" --python-exit-code 1 --python native-prototype/art/c07-v3/check_source.py
done
python3 -m unittest discover -s tests -p 'test_*.py' -v
npm test
godot --headless --editor --path native-prototype --quit
for option in A B baseline; do
  C07_DESIGN="$option" godot --headless --path native-prototype --script res://tools/c07_design_review.gd
  C07_DESIGN="$option" C07_CAPTURE_DIR="/tmp/c07-v3/$option/studio" xvfb-run -a -s '-screen 0 1600x1200x24' godot --audio-driver Dummy --path native-prototype --rendering-method gl_compatibility --script res://tools/c07_design_review.gd -- --capture
  C07_DESIGN="$option" C07_CAPTURE_DIR="/tmp/c07-v3/$option/game" xvfb-run -a -s '-screen 0 1600x1200x24' godot --audio-driver Dummy --path native-prototype --rendering-method gl_compatibility --script res://tools/c07_design_review.gd -- --capture --game-lighting
done
```

The generator writes the study manifest from actual output hashes; Blender source-file metadata need not be byte-reproducible across saves. Regeneration must be followed by tests and new captures. `.gdignore` keeps authoring sources out of automatic Godot import. The technical tests explicitly protect the original candidate's hashes and do not change its existing validation thresholds.

All review images are actual Godot viewport output at 1440 × 1000. A shared fixed 13 × 9 × 31 m framing box, identical camera directions and lighting are used for all three models. The game-lighting mode calls the native game's real `main.gd::_build_lights()` on an off-tree instance, avoiding gameplay/storage and studio fill. The source and GLB remain metres at unit scale; screenshots are not rescaled to make one model appear larger.

No flight, mass balance, cargo handling, collision, Android frame time or production texture acceptance is implied. In particular B's offset/staggered propulsion needs engineering/handling work if selected. User choice precedes any refinement or integration.
