# C-07 A v4 — isolated candidate for Issue #15

A continuation of PR #14's selected **design direction**, not approved production art.
`build_candidate.py` opens the hash-verified editable A v3 `.blend`, preserves its keel, paired drive bells, yokes and landing gear, replaces the road-cab front and simple cassette shells, and saves **only** the new A v4 source and GLB. B, A v3, production art and game logic are not modified.

## Authoring and provenance

- Blender **4.3.2**, Godot **4.7.2 Compatibility**, metre units; Blender forward −Y maps to Godot +Z.
- Editable [source](source/c07_a_v4.blend): separate named mechanical assemblies, original A lineage tags, packed maps.
- [GLB and manifest](../../design-review/c07-v4/): grouped meshes, source/GLB SHA-256, counts, source commit and closed approval gates.
- New geometry and deterministic atlas are original project contributions. Existing A v3 components and the project's geometry helpers are reused. No downloaded model/texture or concept-image projection.
- Original user concept remains a visual reference; no redistribution rights to it are assumed. No separate open asset license is asserted where the repository has not supplied one.
- One 1024² atlas set: base color, ORM, tangent-space normal and emissive. Four packed images, embedded in GLB. ORM R is **authored seam shading**, not baked geometric occlusion. Normal detail is restrained material finish, not a substitute for mechanical geometry. UV islands are tiled/shared, not unique hand-unwrapped artwork.
- All meshes use one named `AtlasUV` layer before batching. Joining differently named UV layers formerly caused new covers to sample the wrong atlas tile; this is checked in the actual editable source.

## Functional design assumptions

The forward hull is a pressure cabin with inclined glazing, sensor prow, sealed dorsal docking hatch and aft service neck. The two cargo pods are **unpressurised weather/dust shells**; no crew corridor enters them. Four captive pins connect ship-side locks to pod receivers; the source check verifies X-overlap. Protection frames, lifting eyes, access covers and door latches belong to the removable pods. Neither detachment animation nor full removal-clearance certification is included.

Twin longerons, transverse beams and diagonal supports tie cargo mounts to paired propulsion mounts. Reservoirs, protected feed lines, drive access panels, radiators/hinges and RCS housings explain the visible hardware. Engines are in a quiescent review state with dark refractory throats. Work/navigation lenses are emissive materials, **not added scene lights**. Their lighting throw is not simulated. No mass, centre-of-gravity, pressure, thermal or thrust calculations are claimed.

## Repeat the delivered checks

From repository root, with the exact tool versions above (`godot` must resolve to 4.7.2):

```sh
# Optional regeneration — writes only the v4 source, GLB and manifest.
blender --background --python-exit-code 1 --python native-prototype/art/c07-v4/build_candidate.py
blender --background native-prototype/art/c07-v4/source/c07_a_v4.blend --python-exit-code 1 --python native-prototype/art/c07-v4/check_source.py
python3 -m unittest discover -s tests -p 'test_*.py' -v
npm test
godot --headless --editor --path native-prototype --import
for design in A3 A4; do
  C07_DESIGN="$design" godot --headless --path native-prototype --script res://tools/c07_a_v4_review.gd
  C07_DESIGN="$design" C07_CAPTURE_DIR="/tmp/c07-a-v4/$design/studio" xvfb-run -a -s '-screen 0 1600x1200x24' godot --audio-driver Dummy --path native-prototype --rendering-method gl_compatibility --script res://tools/c07_a_v4_review.gd -- --capture
  C07_DESIGN="$design" C07_CAPTURE_DIR="/tmp/c07-a-v4/$design/game" xvfb-run -a -s '-screen 0 1600x1200x24' godot --audio-driver Dummy --path native-prototype --rendering-method gl_compatibility --script res://tools/c07_a_v4_review.gd -- --capture --game-lighting
  C07_DESIGN="$design" C07_CAPTURE_DIR="/tmp/c07-a-v4/$design/closeups" xvfb-run -a -s '-screen 0 1600x1200x24' godot --audio-driver Dummy --path native-prototype --rendering-method gl_compatibility --script res://tools/c07_a_v4_review.gd -- --capture --closeups
done
```

The new review script uses PR #11's preview scene and the v3 fixed camera/lighting method. It does not replace the default scene. Six common studio views, two actual `main.gd::_build_lights()` views and three fixed closeups are captured for **each** version, without image retouching. Headless geometry checks do not replace actual captures.

Source save metadata need not be binary-reproducible; any regeneration requires updating hashes, rerunning tests and recapturing changed outputs. See [the review report](../../../docs/c07-v4/README.md) for measured evidence and limitations. Android/FPS/thermal work follows a separate user visual decision.
