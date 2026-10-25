# Hero Station v0.2 — implementation and review handoff

**Bounded prototype; NO-GO for release pending Android visual/performance acceptance.**
Base: PR #8, `f1245a378412dac9a7201b19ad85ab0a13762d7d`.
PR #6 research was read from its Git commit `4986d99219d7e663968fcc1c3900438bcbb0f0cb`.
The browser game, docking scene/rules, main branch and deployed versions are unchanged.

## What changed

- Replaced the ~1.8 km wheel with a physically 6 km axial industrial colony:
  pressure-vessel habitation, transit/lifts, refinery tanks/radiators, structural
  layers and five distinct docking facilities. This is newly authored geometry,
  not runtime scaling of the wheel.
- Rebuilt the courier with a tapered lofted hull, canopy, cargo pods, service panels,
  RCS, folded landing hardware and open engine nozzles. Nominal length remains 30 m.
- Replaced the capped berth with a 200 m deep, open, mechanically framed interior.
- Added original albedo/roughness/metalness/normal atlases, region batching, a much
  lighter distant station, instanced windows and shared-resource background vessels.
- Retained three camera stages and immediate approach skip. Close views keep the
  courier visible, and metrics now include long stalls and the actual renderer.
- Added reproducible dual-APK export using isolated project copies, separate v0.2
  install IDs, an original icon, asset contracts and imported-geometry tests.

## Actual evidence

| Check | Result |
| --- | --- |
| Existing browser logic/static suite | 9/9 PASS; static manifest check PASS |
| Blender 4.3.2 generation | PASS, all four GLBs and three original atlases generated |
| Independent GLB checks | PASS: embedded meshes/materials/maps; far geometry reduction |
| Godot 4.7.2 import / hero smoke | PASS: actual vertices, unit scales, open throat, LOD extents, all camera endpoints/midpoints, visible courier, skip and retained 750 ms stall sample |
| Existing Godot docking-rule smoke | PASS |
| Mobile + Compatibility ARM64 exports | Both built locally; signatures and ARM64-only libraries verified |
| Compatibility desktop visual capture | Three actual Godot/OpenGL screenshots, Mesa llvmpipe software rendering |
| Mobile desktop visual capture | NOT VERIFIED: Vulkan initialization failed and Godot fell back to Compatibility |
| Real Android FPS, frame pacing, thermal behavior, installation | NOT RUN |
| Independent visual quality gate | PENDING; CI cannot approve it |

Imported triangle measurements: station width **6,000.0 m**; courier
**11.8 × 5.6897 × 30.12 m**; unobstructed centerline reaches rear wall at
approximately **z=520 m**, behind the mouth at **z=720 m**. The nominal ratio is
200:1; the measured ship includes its 0.12 m nozzle-rim extension.

Source geometry before Godot LOD: distant station **2,808 triangles**; near station
approximately **30k**; courier **5,956**. Exact generated counts and file hashes
are archived alongside this report. Windows: **456** instances; stars: **280**.
These are geometry counts, not FPS predictions. Shadow and instancing passes make
rendered primitive counts different from source triangle counts.

## Actual desktop captures — not Android evidence

[Reveal](hero-station-v02/reveal.png) · [Approach](hero-station-v02/approach.png) ·
[Docking](hero-station-v02/docking.png) · [Courier asset inspection](hero-station-v02/courier-detail.png)

The source and final APK hashes are in [build evidence](hero-station-v02/evidence.json).
The screenshot overlay deliberately identifies desktop software rendering. No
successful Mobile-renderer screenshot is claimed from this environment.

## Remaining shortcomings / honest quality assessment

The prototype now has pressure-vessel silhouettes and a real open berth rather
than the old wheel/capped entrance. It still uses visibly repeated procedural
modules; it is **not** a production art pass. There is no baked AO/lightmap atlas,
hand-authored grime/decals, populated interior or independently approved art direction.
The distant/near tier switch can pop; service craft reuse the courier silhouette;
the global window batch has coarse culling. The colony's long horizontal silhouette
leaves substantial negative space in portrait reveal. Review these in the screenshots,
then judge scale and visual credibility on the phone rather than declaring success
from geometry counts. Mobile material/shadow parity remains unverified.

Initial local failures were investigated, not hidden: the first measurement used
transformed mesh bounding boxes, which overestimated rotated batches; the corrected
independent test measures actual imported vertices. The first framing check compared
logical camera pixels against the headless OS's 64×64 window; it now uses the actual
viewport's visible rectangle. Both keep the requested physical/framing thresholds.
The original SDK helper called a nonexistent EditorSettings.save API; the new isolated
exporter writes checked editor settings after import exits, without invoking that helper.
The first exports lacked SDK settings; subsequent verified builds used SDK/build-tools
36 to match the Godot template. An optional ADB discovery probe still warns that the
sandbox home is read-only; no Android device session is claimed. APK export/signature
verification itself completes successfully. Local Java is 21; the hero CI workflow now requests Java 21 as well.

## APK download and review

Local APKs are under `native-prototype/build/hero-v02/` (ignored build outputs),
with `APK-MANIFEST.json`. For GitHub downloads, open the new Draft PR's successful
**Hero station Mobile versus Compatibility APKs** check, then download artifact
**hero-station-v02-mobile-vs-compat-android-apks**. Do not confuse a pending/unrun CI
job with an available artifact. See the [build/install/device protocol](../native-prototype/art/README.md).

No merge, release, Pages deployment or production integration is authorized.
Next action: independent screenshot/source review, followed by both APKs on an
actual midrange Android phone. User acceptance must cover appearance AND warm-device
performance before integration.
