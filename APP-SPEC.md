# Avaruusseikkailu – APP-SPEC

Version: 0.1, 2026-10-24. Common app playbook: v1.9.2.

## Game promise
A mobile-first space career adventure inspired by trading/exploration, not by MMO complexity:
missions, legal and illicit cargo later, exploration, discoveries, and ship development.
Combat is optional and not the primary loop.

## Design decisions
- Short local free flight while exploring or approaching a station; automatic longer hops.
- Three main sections: cockpit/station, star map, log. Avoid menu nesting.
- Credible discoveries plus infrequent authored mysteries (future).
- Deterministically generated default planet name. Offline discoverer may submit one custom name in local save.
- Shared naming priority, factions, markets and governance are future online/server features.
- The first global claim cannot be guaranteed by localStorage. Server will own global first-discovery timestamps and moderation.
- Offline, mobile-first, no account, no third-party runtime dependencies.

## Prototype v0.1 (not the final architecture)
- One predefined four-system hyperlane network, two stations, two research bodies.
- Single delivery mission: Kestrel Port -> Vela Junction, +240 credits only once.
- Drag-to-look free flight, press-and-hold approach, assisted docking, instant map jumps.
- Scan when aligned and near, +70 credits once per planet; rename once per local save.
- 1 scanner upgrade, refuel, flight log. Deterministic names and local storage.
- Rendered 2D canvas with perspective effects: flight-feel validation, NOT a 3D physics engine.
- No multiplayer, NPC combat, smuggling, politics, procedural billions of systems or backend yet.

## Acceptance
1. Mobile viewport (~360–430 px) is navigable without hidden menus.
2. Courier delivers and pays exactly once, reload does not duplicate reward.
3. Fuel is deducted for legal hyperspace hops; a zero-credit stranded player can recover at a station.
4. A researched planet gets one local custom name; default identity remains deterministic.
5. Depleted fuel in flight allows a paid/discounted emergency tow back to Kestrel Port.
6. Project test command: npm test; PR runs quality workflow.
7. Independent mobile playtest and browser/offline QA remain pending; no release/merge without explicit user GO.

## Local data
Browser localStorage key avaruusseikkailu-save-v1; schema=1. Do not use this store for online identity or claim adjudication. Unknown or invalid saves reset in memory to a fresh start; there is no backup/import in v0.1. Avoid using real personal data for planet names during testing.

## Release
Keep main untouched until the developer's PR is reviewed and user explicitly approves. Configure GitHub Pages only when ready to release; a public repo is not by itself a live game.