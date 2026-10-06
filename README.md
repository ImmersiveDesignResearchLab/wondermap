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

## xi: outdoor field kit (in development)

**xi (experiential intelligence in Design Happenings)** takes WonderMap out of the lab and into public outdoor space. Instead of a floor-plan image and simulated position, the map is a real satellite or street map. Participants share their own phone's GPS from a browser link, so several people appear at once. Anyone wearing a Unicorn Hybrid Black adds the EEG smoke field; everyone else still appears on the map, with trails and automatic zone entry and exit.

Try it with no hardware: open [`wondermap_outdoor.html`](wondermap_outdoor.html) and press **Run demo**.

### Status

| Piece | State |
|-------|-------|
| `wondermap_outdoor.html` (map, features, participants, smoke, baseline, QR, audience view, export) | Built. Tested in a headless browser with simulated walkers and a stand-in for the cloud relay. **Not yet tested in the field.** |
| `gps_tracker.html` (participant page) | Built. Same testing as above. **Not yet tested on real phones.** |
| `bridge/bridge.py` (Unicorn LSL to the map) | Built. Tested offline on simulated signals. **Not yet tested with a headset or on the field computer.** |
| Event Marker feeding events to the map live | Not built. The map can already receive them. |
| Offline map tiles | Not built. The map needs a network connection. |

### How the pieces fit

```
 Participant phones                                  Surface 2
 gps_tracker.html ──┐                         ┌──▶  audience view (?mode=viewer)
                    ▼                         │
              Supabase Realtime ◀─────────────┘
              (Broadcast only, nothing stored)
                    │
                    ▼
        Surface 1: wondermap_outdoor.html ◀── ws://localhost:8765 ◀── bridge/bridge.py
                                                                          ▲
                                       Unicorn ─▶ Unicorn Recorder ─▶ LSL ┘
```

Raw EEG never leaves the computer running the bridge. Only processed band summaries (about four per second) go to the audience screen.

### Setup

1. **Cloud relay.** Create a free [Supabase](https://supabase.com) project. Only Realtime Broadcast is used; no tables are needed.
2. **Config.** Put the Project URL and the **publishable** key in [`xi-config.js`](xi-config.js) (template: [`xi-config.example.js`](xi-config.example.js)). The publishable key is designed to be public. Never commit the secret or `service_role` key, or the database password.
3. **Hosting.** Serve the pages over HTTPS (GitHub Pages works). Phones will not share location on an insecure page.
4. **EEG bridge** (only for headset wearers). On the computer that runs Unicorn Suite:
   ```
   pip install -r bridge/requirements.txt
   python bridge/bridge.py --synthetic          # test without a headset
   python bridge/bridge.py --prefiltered        # live, using the filtered Unicorn Recorder stream
   ```
   In Unicorn Recorder, connect the headset, choose the filters, and enable LSL output. Run `python bridge/bridge.py --help` for the thresholds. The bridge was developed and tested on Python 3.12; install the requirements and run `--synthetic` on your own machine before relying on it, especially on a newer Python.
5. **Map.** Open `wondermap_outdoor.html` on the main computer. Use **Find** or **My location** to center on the site. The start view is only approximate.

### Running a session

1. **Setup mode:** place up to three features (they match the Event Marker's Feature A, B and C). Click **Place** then the map, or drag the handle. Or stand at a feature with a phone and press **Center**, then walk to its edge and press **Radius**.
2. Participants scan the **Share my GPS** QR code. Put the **Audience view** QR or link on the second screen.
3. For each headset wearer, link their EEG stream to their phone in the participant list and run the **90 second resting baseline** while they stand still.
4. **Start session.** At the start, make the agreed flash-and-clap and press **Sync mark** so every recording (screen capture, 360 video, EEG, Event Marker CSV) aligns to one moment.
5. When finished, **Stop session** and export. The page warns you if you try to close it with unsaved data.

Exports: a JSON file (the full session), an events CSV, and a frames CSV.

### What the smoke shows

Band values are divided by that wearer's own baseline, then smoothed. Theta is amber, alpha violet, beta cyan. Cyan fades as beta falls. The smoke is drawn only when the signal is clean and the wearer is still.

The **wonder signature** badge appears when theta is at least 1.35x baseline and beta at most 0.85x baseline, held for a few seconds (all adjustable). This is a **proposed** signature, not a validated detector. Theta up and beta down also occur with novelty, effort and surprise, which is why it is read alongside the observer's behavioral record.

### Movement artifacts

Walking and head movement contaminate EEG. The work is shared:

- **g.tec Unicorn Recorder** applies band-pass and notch filtering, and OSCAR artifact removal is part of Unicorn Suite. To confirm for each setup: that the Recorder's LSL stream is the filtered one, that it includes the motion channels, and whether OSCAR applies to the live stream or only to recordings.
- **`bridge.py`** adds two things a filter cannot: it rejects windows with large spikes, and it uses the headset's accelerometer and gyroscope to mark each window **still** or **moving**. Only still windows are scored. Thresholds are starting values and should be tuned on site.

### Why theta, alpha and beta

- **Theta** (frontal-central): mid-frontal theta reflects the brain registering a need for cognitive control, and novelty is one trigger (Cavanagh and Frank, 2014, *Trends in Cognitive Sciences*).
- **Beta** (central-parietal): beta is associated with maintaining the current sensorimotor or cognitive state, the "status quo" (Engel and Fries, 2010, *Current Opinion in Neurobiology*). Wonder is proposed to disrupt it.
- **Alpha** (parieto-occipital): widely linked to inhibiting task-irrelevant regions. In xi it is a context band and the most exploratory of the three.

### Data and privacy

Sessions record participants' positions and, for headset wearers, brain-derived band values. Treat both as sensitive.

- Participants see a plain-language notice on the sharing page, but **that notice is not a consent form.** Run your own ethics process and consent, in the participants' language.
- Positions are relayed through Supabase Broadcast and are not stored there. They are saved in the session export on the computer running the map.
- Each session has a random code that acts as the channel name. Anyone with the public key and the code could join, so share the QR codes only with participants and rotate the key after an event if you wish.
- `.gitignore` keeps session exports, recordings and secrets out of the repository. **Do not commit session data to a public repository.**

### Known limits

- GPS is typically accurate to a few meters in the open and worse near buildings or under trees. Features should be larger than that.
- The smoke shapes are not oriented to the head, because the phones give no heading.
- The street map uses OpenStreetMap's free tiles, which suit a small workshop but not heavy use.
- The first planned deployment is a single site (kokoka, Kyoto), but nothing in the code is specific to it.

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

The outdoor field kit exports a related file, `xi-outdoor-1`, where position is latitude and longitude instead of floor-plan coordinates:

```json
{
  "meta":  { "schema": "xi-outdoor-1", "session": "code", "crs": "WGS84", "started": "ISO time",
             "baseline": { "participant id": { "theta": 0, "alpha": 0, "beta": 0 } },
             "thresholds": { "theta": 1.35, "beta": 0.85, "holdSeconds": 3 } },
  "zones": [ { "id": "zA", "label": "Feature A", "lat": 0, "lng": 0, "radius_m": 8 } ],
  "participants": [ { "id": "p1", "name": "Sam", "eegStream": null } ],
  "frames": [ { "t": 12.4, "id": "p1", "k": "gps", "lat": 0, "lng": 0, "acc": 5 },
              { "t": 12.5, "id": "p1", "k": "eeg", "theta": 0, "alpha": 0, "beta": 0,
                "rel_theta": 1.2, "rel_alpha": 1.0, "rel_beta": 0.8, "clean": true, "still": true } ],
  "events": [ { "t": 12.4, "wall": "ISO time", "type": "ZONE_ENTER", "id": "p1", "zone": "zA" } ]
}
```

Event types: `SESSION_START`, `SESSION_END`, `SYNC`, `ZONE_ENTER`, `ZONE_EXIT`, `BASELINE_START`, `BASELINE_DONE`, `BASELINE_FAILED`, `WONDER_START`, `WONDER_END`.

---

## Development Trajectory

WonderMap is built in three tiers sharing a single portable data schema:

| Tier | Stack | Status |
|------|-------|--------|
| 01 | p5.js / Browser | **Current** — smoke field over floor plan image, live + replay |
| 02 | Three.js / Browser | Near term — live Gaussian splat base layer, real-time LSL stream |
| 03 | Unity / Gaussian Splat | Far goal — 3D spatial rendering, participant tracked in live splat environment |

---

## Live EEG data

Unicorn Recorder streams over **Lab Streaming Layer (LSL)**. [`bridge/bridge.py`](bridge/bridge.py) reads that stream, rejects artifact windows, labels each window still or moving from the headset's motion sensors, computes theta, alpha and beta power per electrode cluster four times a second, and sends the result to the map over a local WebSocket. See [xi: outdoor field kit](#xi-outdoor-field-kit-in-development) for setup and current status.

The portable JSON schema means the same data can feed p5.js, Three.js and Unity without restructuring.

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
