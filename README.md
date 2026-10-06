# WonderMap

**Neuroarchitectural field visualization tools for the IDRL Design Happenings research program.**

[Live site](https://immersivedesignresearchlab.github.io/wondermap/) · [WonderMap](https://immersivedesignresearchlab.github.io/wondermap/wondermap.html) · [Event Marker](https://immersivedesignresearchlab.github.io/wondermap/wondermap_event_marker.html)

---

## Overview

WonderMap is a suite of open research tools for visualizing mobile EEG data spatially, aligning it with ethnographic observation, and building shared assessment infrastructure for the experiential quality of designed space.

The tools operationalize the **Neuro-Architectural Analysis Framework (NAAF)** developed at the Immersive Design Research Lab (IDRL), California State University Long Beach. The NAAF triangulates three data layers — environmental sensing, mobile EEG, and design ethnography — to investigate the neurophysiological and behavioral conditions that produce wonder in designed environments.

EEG hardware: **g.tec Unicorn Hybrid Black** (8-channel, 250Hz, hybrid electrodes).

---

## Tools

### WonderMap — Visualization Interface

A browser-based neuroarchitectural field visualization tool. Renders live EEG data as an animated smoke field spatially situated within an architectural floor plan. Supports live streaming and session replay.

**Three frequency bands drive the visualization:**

| Band | Color | Meaning |
|------|-------|---------|
| θ Theta (4–8 Hz) | Amber | Absorbed attention — expands as wonder deepens |
| α Alpha (8–12 Hz) | Violet | Open receptive processing — blooms with contemplative awareness |
| β Beta (13–30 Hz) | Cyan | Cognitive load — recedes as wonder takes hold |

Band colors are space-wide and consistent — amber is always theta, anywhere in the floor plan. A viewer scanning the full floor plan reads the neurological state of the space from color alone.

**Key features:**
- Puff geometry derived from Unicorn electrode cluster topology — shape reflects scalp origin
- EMA smoothing applied before any visual output — the field breathes rather than flickers
- Smoke follows the participant — the data field belongs to the person, not the place
- Persistent path line traces the full session route
- Memory slider controls how long smoke lingers (tight follow → temporal analysis window)
- Wonder detection badge — fires when theta is elevated and beta is suppressed simultaneously
- Uploadable base layer — photograph, collage, or Gaussian splat top-down render
- Live and replay modes with scrubbable timeline
- Band toggles and real-time parameter controls

---

### WonderMap Event Marker — Ethnographic Companion Tool

A mobile-optimized companion interface for live session observation. Bridges mobile EEG and ethnographic observation by logging zone entries, behavioral tags, voice notes, and images with millisecond-precise timestamps aligned to the EEG record.

**Designed to run on iPhone, iPad, or Android during field sessions.**

**Key features:**
- Feature setup — name, description, and 12-sense phenomenological vocabulary per zone
- Zone entry / exit logging aligned to Unicorn sample timestamps (elapsed × 250Hz)
- Behavioral tags: dwell · gesture · touch · play · engage · emote
- Voice notes via Web Speech API — hands-free, eyes on participant
- Still image capture with timestamped filenames cross-referenced in CSV export
- Notable moment flag (Space bar shortcut on desktop)
- CSV export with zone metadata header block and image index
- 52px minimum touch targets — operable one-handed

**Phenomenological sense vocabulary:**
Seeing · Smelling · Tasting · Hearing · Haptics · Proprioception · Mobility · Proximity · Agency · Connectedness · Surprise · Possibility

---

## Data Schema

Both tools use a portable JSON data schema designed for compatibility across all development tiers. The schema includes:

```json
{
  "meta": {
    "id": "session_id",
    "space": "space name",
    "channels": ["Fz","C3","Cz","C4","Pz","PO7","Oz","PO8"],
    "sampleRate": 250,
    "baseline": { "theta": 1.0, "alpha": 1.0, "beta": 1.0 }
  },
  "zones": [
    { "id": "zA", "label": "Feature A", "x": 0.38, "y": 0.48, "rx": 0.082, "ry": 0.078, "rot": 0.38 }
  ],
  "frames": [
    { "t": 0.0, "x": 0.5, "y": 0.5, "theta": 1.0, "alpha": 1.0, "beta": 1.0 }
  ]
}
```

The Event Marker CSV export aligns to the EEG record via three timestamp columns: `elapsed_s`, `wall_clock`, and `unicorn_sample` (elapsed × 250Hz).

---

## Development Trajectory

WonderMap is built in three tiers sharing a single portable data schema:

| Tier | Stack | Status |
|------|-------|--------|
| 01 | p5.js / Browser | **Current** — smoke field over floor plan image, live + replay |
| 02 | Three.js / Browser | Near term — live Gaussian splat base layer, real-time LSL stream |
| 03 | Unity / Gaussian Splat | Far goal — 3D spatial rendering, participant tracked in live splat environment |

---

## Live Data Integration (Planned)

To connect real Unicorn data to WonderMap:

1. **Unicorn Suite** broadcasts data over **Lab Streaming Layer (LSL)** by default
2. A lightweight Python bridge (`pylsl` + `websockets`) listens to the LSL stream, computes rolling band power via FFT, and forwards values to WonderMap via WebSocket
3. WonderMap receives the stream and populates `SESSION.frames` in real time

The portable JSON schema means the same data pipeline feeds p5.js, Three.js, and Unity without restructuring.

---

## Research Context

**Design Happenings** are structured sensory installations deployed in the IDRL's publicly accessible downtown Long Beach lab space. Public participants interact with multi-sensory features while a researcher wearing the Unicorn Hybrid Black moves freely through the space. A dedicated observer runs the Event Marker on a phone or tablet, logging behavioral observations with timestamps aligned to the EEG record.

The research investigates wonder — not awe — as the target experiential state: absorbed, eudaimonic engagement with designed environments that silences the internal monologue, fosters pro-social connection, and primes the brain for new information.

---

## Citation

If you use WonderMap in your research, please cite:

> Barker, H.R. (2026). *WonderMap: Neuroarchitectural Field Visualization Tools for the IDRL Design Happenings Research Program.* Immersive Design Research Lab, California State University Long Beach. https://github.com/ImmersiveDesignResearchLab/wondermap

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

**Prof. Heather Renée Barker** · Director, Immersive Design Research Lab  
California State University Long Beach · Architectures of Experience
