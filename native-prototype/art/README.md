# Hero Station v0.2 — bounded Android art benchmark

Based on PR #8 `f1245a378412dac9a7201b19ad85ab0a13762d7d`, with PR #6's
art-pipeline research as reference. **DRAFT; neither visual nor device acceptance granted.**
See [delivery report](../../docs/HERO-STATION-v0.2.md) and its actual screenshots.

## Authoring

Blender 4.3.2 was used locally. `generate_hero.py` authors original geometry and
512×512 albedo, packed roughness/metalness and tangent-space normal trim atlases.
Data textures are explicitly Non-Color **before** saving. No downloaded models,
material photographs, proprietary spacecraft or real user data are used. Berth
lettering uses Blender's bundled Bfont; application icon is original SVG geometry.
Blender/Godot/Android tooling is not claimed as repository-authored software.

```sh
blender --background --factory-startup --python native-prototype/art/generate_hero.py -- --output native-prototype/assets
python3 native-prototype/tools/verify_hero_assets.py
godot --headless --editor --path native-prototype --quit
godot --headless --path native-prototype --script res://tools/hero_smoke.gd
godot --headless --path native-prototype --script res://tools/smoke.gd
```

Use **Godot 4.7.2 with matching export templates**. Local downloads were checked
against the release SHA-512 list. The existing docking project's main scene and
renderer settings stay unchanged; building hero APKs creates isolated copies.

## Geometry strategy

The colony is a 6,000 m axial utility/cargo backbone, not an enlarged wheel.
Four staggered habitation districts contain faceted pressure vessels, terrace
sunshades, greenhouse strips, lifts, exterior ribs and 456 instanced window panes.
A separate refinery/radiator district, two transit guideways, diagonal supports,
four secondary docking terminals and a central logistics hull provide distinct
functions and asymmetry. Small moving 12 m service-craft variants use the same
courier resources; the hero courier itself remains unscaled.

The courier's 30.12 m measured length includes its nozzle rims (nominal 30 m).
Lofted hull sections, an angular canopy, pressure/cargo pods, external bracing,
service hatches, dorsal access panels, RCS housings, landing skids and open exhaust
petals provide actual geometry beyond the material pattern. Its beam is 11.8 m.

The main berth has 76×48 m clear space and 200 m real depth. It has open framing,
retracted shutters, hydraulic rams, internal walkways/bridges, cargo cradles and
recessed guidance strips. No solid cap blocks the mouth: an imported-triangle ray
reaches the rear wall at approximately z=520 from z=800.

Meshes batch by material **and 750 m station region**, instead of one whole-world
material mesh. A separately authored distant station cuts source triangles by more
than 10×; camera distance switches tiers without changing either physical transform.
Godot's generated mesh LOD is also enabled by its GLB importer. Window panes and stars
use MultiMesh. Six service craft share imported resources. There is one local berth
fill light and one sun; sun shadows are enabled only for close approaches with a
320 m shadow distance. No GI, volumetric effects or dozens of shadow lights.

## Build and download

The PR workflow `Hero station Mobile versus Compatibility APKs` builds both ARM64
variants. After a **successful** run, open its artifact
`hero-station-v02-mobile-vs-compat-android-apks`, download/unzip it, then install:

- `hero-v02-mobile-arm64.apk`
- `hero-v02-compat-arm64.apk`

These are debug-signed experiments with separate `.hero.v02.mobile` and
`.hero.v02.compat` package IDs, leaving older tests installed. `APK-MANIFEST.json`
contains the exact download hashes. A local successful build does not mean a GitHub
artifact already exists; check the delivery report for remote execution status.

Local exporter (Linux, SDK platform/build-tools 36.0.0, Java 21):

```sh
python3 native-prototype/tools/build_hero_variants.py \
  --godot /path/to/Godot_v4.7.2-stable_linux.x86_64 \
  --output /tmp/hero-v02-build --sdk /path/to/android-sdk --java /path/to/jdk
```

Configure the matching templates and standard Godot debug-keystore environment
variables first; never commit signing keys. In a restricted cloud workspace set
`XDG_CONFIG_HOME`, `XDG_DATA_HOME` and `XDG_CACHE_HOME` to writable task directories.
The exporter checks both signatures, ARM64-only native libraries and unchanged
source project/export settings. It fails rather than silently using another Godot.

## Android acceptance (NOT RUN)

On the same phone, test both applications through reveal, approach and docking;
check that approach skips immediately. Record device/GPU, OS and the **actual**
renderer shown in the overlay, including any fallback. Keep a warm 10-minute loop,
record FPS/average/p99, draw calls and primitives, stutters, heat and memory if
measurable. Frame-time statistics retain long stalls rather than discarding them.

Capture the ship, the whole colony, near habitation and the berth interior. Judge
readable physical scale, material response, repeated modules, lighting, LOD pop and
whether the courier appears functional. Target 30 FPS midrange / aspire 60 FPS on
stronger devices; these are goals, **not measured results**. No merge or release
until user visual approval and real-device performance acceptance.
