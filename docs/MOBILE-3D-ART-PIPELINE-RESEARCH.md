# Avaruusseikkailu — Mobile 3D visual quality & scale: technical research brief

Date: 2026-10-25
Status: **RESEARCH / technical spike**, no release or engine commitment.
Owner: product direction by user; engineering prototype by Codex/ChatGPT; independent visual/UX QA by Work when enabled and assigned.
Repository context: native Godot proofs live in draft PR #4 (navigation) and draft PR #5 (docking). They proved Android APK build and deterministic scenario rules, **not visual quality or enjoyable flight**. Browser PWA in main is historical demo and is not the native architecture.

## User's non-negotiable goals

- A native-first Android space-career game, possible iOS later, not a browser game.
- Realistic-ish *industrial sci-fi*; **no blocky primitive-geometry final art**.
- Giant stations must feel physically enormous compared with ~30 m player courier; large station ~1.5–3 km nominal final art target, small outpost ~150–300 m. These are creative size targets, not measured outputs.
- Long-distance travel must not waste time. Station approach/docking can be interactive when there is a meaningful choice/risk/procedure (scans, cooling, shield/transponder states, local authority), not repetitive taps.
- Exploration, cargo, smuggling and ship development are the primary actions. Fighting secondary, optional.
- The user principally tests on an Android phone. GitHub is the source-of-truth and can build debug APK automatically.
- Keep all work separate from main until explicitly approved. No retroactive claims that earlier CI tested appearance.

## Preliminary technical choice, subject to measured validation

Start with **Godot 4.7.2 Mobile renderer** for a contemporary Android test, and test a **Compatibility** build on identical assets/camera/path for device coverage/performance. Mobile is optimized for new mobile GPUs using Vulkan. Compatibility targets older devices via OpenGL. Do **not** assume Mobile always wins on every device. Do not spend time on a complete Unity rewrite unless this spike exhibits a hard technical blocker; Unity URP is an alternate to record, not an ongoing parallel implementation.

Workflow: **Blender-authored modular meshes → glTF/GLB → Godot 4.7.x → Android ARM64 debug APK**.
Generate source .blend and export .glb reproducibly in a scripted desktop/CI asset pipeline; Android itself is not required to run Blender. Keep an asset provenance manifest (license/source/version/author where relevant). Blender->glTF is an established PBR workflow.

### Art direction: “industrial-cinematic realism on mobile”

- Silhouette and proportion first: enormous ring/spine, plausible docking bay, layered antennae, service vessels, cargo elevators, hull segmentation.
- Bevelled hard-surface details, chamfers, panel cutouts, trims. Avoid making every plate a runtime mesh.
- Use **PBR metal/rough**, normal maps, ambient-occlusion information, emissive navigation strips, subtle grime, controlled roughness variation. Realistic look comes more from credible materials/lighting/composition than unlimited polygon counts.
- Light static hull with **baked** detail/indirect light where applicable; sparingly use dynamic sun/shadows on player vessel. Avoid dozens of expensive shadow-casting lights, per-pixel transparent particles, runtime GI/volumetric effects by default.
- Different asset tiers: near foreground is real geometry, mid range uses simplified assemblies, far-away station is silhouette/low LOD. Do not render a high-poly 3 km station at full detail from thousands of metres away.
- Use a handful of tiny nearby shuttle ships, docking scaffolds, antennae, and berth marking for comparative scale. For static repeating surface segments, evaluate MultiMesh / shared materials and batch on spatial chunks. Avoid giant one-piece meshes that undermine culling.
- Reference materials, not reference IP: no copied Elite Dangerous / NMS mesh, textures or protected designs. License-audited CC0 surfaces from Poly Haven/ambientCG are options.

### Scale / cinematography

Real local 3D environment: keep a consistent scale in one scene; use **1 unit = 1 metre** in newly authored art. This differs from the earlier v0.3 test's 1 unit≈10m convention; do not mix assets blindly. Distances spanning star systems are separated into loading/travel cuts and logical jumps.

Produce exactly **3 camera beats** with a single physical station model:
1. *Reveal / silhouette*: tiny ship foreground with large station far in frame, readable ring/spine profile, no procedural wait.
2. *Flyby / approach*: station visibly dominates view; hull parallax, lights and service craft convey size, 4–7s illustrative, skippable.
3. *Docking aperture*: player vessel arrives at just one small opening; large structural elements crop off screen. Local scan/cooling choice only if situation demands.

Never fake the station's size by scaling the model frame-by-frame. Camera FOV and distance may change, but all object-world sizes remain consistent. Use cut/transitions as needed without hidden input stalls.

## Two-slice evaluation matrix

Implement **one** hero station (not an entire universe) and one courier in the same scripted flight path. Export two debug APKs from the exact same content snapshot:
- Variant M: Godot **Mobile** renderer, suitable modern Android GPU.
- Variant C: Godot **Compatibility** renderer, older-device fallback.

Same assets, same three camera beats, same UI; only renderer/config differs. Do not spend time adding online, markets, missions or new monetization. One well-made asset beats 30 primitive stations.

Produce screen recordings/screenshots of beats 1, 2, 3 from the test device, not Godot editor alone.

## Performance and quality gates

Do not promise arbitrary triangle or texture caps before profiling the phone. Record:
- Actual device model/OS/GPU if accessible with permission; renderer used.
- Average FPS, a low-frame-rate measure / frame-time spikes, stutter, thermal deterioration over 10 min, memory footprint, approximate APK/app asset size, launch/load time.
- Rendering stats (draw calls, visible objects/vertices where profiler supports them), number/size of PBR texture atlases, GPU texture import format, number of runtime shadow lights.
- Test with and without mesh LOD, baked lighting, atlas/instancing on the exact same camera path. Confirm visually that simplified LOD does not pop distractingly.
- **Initial target for medium Android devices: steady 30 FPS after warm-up and ~10 minutes**, aspirational 60 FPS on capable phones. These are provisional release goals, not achieved performance.
- Texture baseline: share materials, prefer 1k-sized atlases for modular details and reserve larger textures for hero close-ups if measured and justified. ETC2 on broad Android support; ASTC / high-quality compression only when supported in selected renderer/device. Enable 3D mipmaps and measure memory.
- Runtime image quality must remain clearly beyond gray primitive boxes: curved or bevelled silhouette, consistent material response, purposeful lights, readable docking bay.
- Build/import validation and source asset/license audit must be automated where sensible; visual quality and Android fluidity require device evaluation.

Go/No-Go:
- GO for a wider playable mission only if user finds beat #2 and #3 visually credible *and* approach is not dead time, and warm-device FPS target is met.
- If visual improvement costs too much, profile scene before changing engines. First lower LOD/materials/shadows/transparency, not physical size or player ship/station ratio.
- If both renderers fail on representative midrange devices, document a bounded Unity-URP comparison rather than an uncontrolled engine rewrite.

## Division of labor

**ChatGPT — art director/technical lead:** maintain source-backed constraints, approve reference direction with user, decide which experiments to run, review measurable outcome, record GO/NO-GO in PR.

**Codex — engineering track (to be explicitly launched/assigned; not started by writing this brief):**
- in new test-only branch build scripted Blender asset generation/export pipeline or integrate a verified licensed high-quality modular hard-surface asset;
- create three reproducible camera beats around a detailed hero station and 30 m courier; no primitive-appearance production output;
- configure two Godot renderer variants, CI Android APK artifacts, metrics overlay and screenshot capture guidance;
- automate same-path tests; write actual asset provenance and measurement results;
- no merges/releases, no secrets, no edits to historical Pages demo.

**Work — independent visual UX QA (to be explicitly launched in Work mode after Codex evidence exists):**
- review *actual* screenshots/video and exact APK SHA, test reports and provenance; compare to acceptance criteria;
- check scale, camera, image readability, mobile interaction economy, performance evidence and missing tests;
- post PASS/FAIL/PARTIAL/NOT RUN to the GitHub PR; keep it independent from implementing the scene;
- Work cloud browser cannot substitute actual Android GPU benchmarking unless it has an appropriate connected device/test infrastructure. User phone playtest remains required.

**User:** selects whether realism/camera is right and whether interaction feels engaging from installed Android builds. No need to model, configure Blender, or manually copy whole repos.

## Verified reading / sources (2026-10-25)

1. Godot renderer options: https://docs.godotengine.org/en/4.7/tutorials/rendering/renderers.html
2. Godot 3D optimization and LOD: https://docs.godotengine.org/en/4.7/tutorials/performance/optimizing_3d_performance.html
3. Godot mesh LOD: https://docs.godotengine.org/en/4.7/tutorials/3d/mesh_lod.html
4. Godot texture import/compression: https://docs.godotengine.org/en/4.7/tutorials/assets_pipeline/importing_images.html
5. Godot LightmapGI: https://docs.godotengine.org/en/4.7/tutorials/3d/global_illumination/using_lightmap_gi.html
6. Godot recommended glTF 2.0 import: https://docs.godotengine.org/en/4.7/tutorials/assets_pipeline/importing_3d_scenes/available_formats.html
7. Blender glTF PBR asset workflow: https://docs.blender.org/manual/en/latest/addons/scene_gltf2.html
8. Poly Haven assets CC0: https://polyhaven.com/license
9. Unity URP optimization (fallback comparison only): https://docs.unity.com/en-us/engine/6000.3/manual/analysis/graphics-performance-profiling/in-urp/understand-performance/understand-performance

## Immediate next step

Do NOT build a larger game. First have Codex implement the **hero-station three-shot art/renderer benchmark** with a reproducible asset pipeline and deliver exact-SHA Android builds. Then independently review visuals and run actual-phone measurements. If this technical/art-quality bar fails, iterate the shot/pipeline, not gameplay scope.
