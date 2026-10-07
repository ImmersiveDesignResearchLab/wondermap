# Setting up the outdoor field kit (xi)

How to run [`wondermap_outdoor.html`](wondermap_outdoor.html) with participants' phones and, optionally, a Unicorn Hybrid Black. For what the kit is and what state it is in, see the [README](README.md#xi-outdoor-field-kit-in-development).

You can try the map with no setup at all: open it and press **Run demo**.

## What you need

- A computer with Edge or Chrome to show the map. For headset wearers it also runs Unicorn Suite and the bridge, and should stay within Bluetooth range of the wearer.
- A g.tec Unicorn Hybrid Black and Unicorn Suite (Unicorn Recorder).
- Participants' phones with a web browser and location services.
- A network every device can reach. A mobile hotspot works.
- A free [Supabase](https://supabase.com) account.
- An HTTPS host for the pages. GitHub Pages works.

## 1. Cloud relay

Create a Supabase project, in a region close to the site. Only Realtime Broadcast is used, so no tables are needed. Keep public channel access enabled in the project's Realtime settings, because the session channels are public by design.

The free tier is enough for a small workshop (about 200 simultaneous connections and 100 messages per second at the time of writing). Free projects are paused after a period of inactivity, so open the project or run a test session shortly before an event.

## 2. Config

Put the Project URL and the **publishable** key in [`xi-config.js`](xi-config.js) (template: [`xi-config.example.js`](xi-config.example.js)). Both `wondermap_outdoor.html` and `gps_tracker.html` read it, so phones and the audience screen need no typing.

The publishable key is designed to be public. **Never put the secret key, the `service_role` key, or the database password in this repository.**

## 3. Hosting

Serve every page from the same folder over HTTPS. Phones will not share location from an insecure page. If you host somewhere other than this repository's GitHub Pages site, the QR codes adapt to wherever the map page is served from.

## 4. EEG bridge (headset wearers only)

On the computer that runs Unicorn Suite:

```
pip install -r bridge/requirements.txt
python bridge/bridge.py --synthetic        # test without a headset
python bridge/bridge.py --prefiltered      # live, using the filtered Unicorn Recorder stream
```

In Unicorn Recorder, connect the headset, choose the filters, and enable LSL output. When the bridge connects it prints the stream's channel labels and whether the **motion gate** is on. Check that the stream is the filtered one and that it includes the accelerometer and gyroscope channels. Without them the bridge still runs, but it cannot tell still from moving.

| Option | Default | Meaning |
|--------|---------|---------|
| `--prefiltered` | off | The stream is already filtered by Unicorn Recorder, so do not filter again. Without it the bridge applies a fallback 1-40 Hz band-pass and a mains notch. |
| `--stream NAME` | any EEG stream | Connect to the LSL stream whose name contains NAME. |
| `--synthetic` | off | Generate fake EEG with walking episodes, for testing. |
| `--pid ID` | `1` | Label for the participant wearing the headset. |
| `--line` | `60` | Fallback mains notch in Hz (`0`, `50` or `60`). Only used without `--prefiltered`. |
| `--ptp` | `150` | Reject a window if any channel exceeds this many microvolts peak to peak. |
| `--gyro` | `30` | Count the wearer as still below this mean head rotation (degrees per second). |
| `--acc` | `0.08` | Count the wearer as still below this dynamic acceleration (g). |

The map connects to the bridge at `ws://localhost:8765`, so open the map in Edge or Chrome on the same computer. The browser may ask permission to reach devices on your local network. Allow it.

The bridge prints a readout every two seconds (still or moving, percent clean, peak-to-peak, motion values). Use it to tune `--ptp`, `--gyro` and `--acc` on site, by watching it while someone stands still and then walks.

## 5. Map

Open `wondermap_outdoor.html`. Use **Find** (it searches for a place name) or **My location** to center on the site. The remembered start view is only approximate.

## 6. Running a session

1. **Setup mode.** Place up to three features. They match the Event Marker's Feature A, B and C. Click **Place** then the map, or drag the handle. Or stand at a feature with a phone and press **Center**, then walk to its edge and press **Radius**.
2. **Join.** Participants scan the **Share my GPS** QR code. Put the **Audience view** link on a second screen.
3. **Baseline.** For each headset wearer, link their EEG stream to their phone in the participant list and run the 90 second resting baseline while they stand still.
4. **Start session.** At the start, make the agreed flash-and-clap and press **Sync mark**, so every recording (screen capture, 360 video, EEG, Event Marker CSV) aligns to one moment.
5. **Stop and export.** Use **Stop session**, then export the JSON, events CSV and frames CSV. The page warns you if you try to close it with unsaved data.

Keep the exports out of this repository (`.gitignore` covers the default file names). They contain participants' locations and brain-derived data.

## Tuning the display

- **Smoke memory** sets how long the smoke lingers. Short follows the participant closely, longer shows where they have been.
- **Wonder thresholds** (theta at least, beta at most, and the hold time) are adjustable in the Display panel. They are a proposed signature, not a validated detector.
- The smoke is drawn only when the signal is clean and the wearer is still.

## Troubleshooting

| What you see | What to check |
|--------------|---------------|
| **Cloud** light never turns green | The URL and key in `xi-config.js`. Whether the Supabase project is paused. Whether Realtime accepts the key you are using. If it does not accept the new publishable key, try the legacy anon key from the project's API settings. |
| **Bridge** light stays orange | Is `bridge.py` running on this computer? Is LSL output enabled in Unicorn Recorder? Is the map open in Edge or Chrome on the same computer? |
| A phone's dot does not appear | Location permission on the phone. The page must be on HTTPS. The phone must use the current QR code (a new session code changes the link). Zoom out: your view may be centered elsewhere. |
| A dot looks hollow | GPS accuracy is worse than 30 m, so it is ignored for zone entry and exit. Move to open sky. |
| A headset wearer shows "moving, not scored" while still | Raise `--gyro` or `--acc`, or check that the stream's channel order matches the labels the bridge printed. |
| "Baseline failed" | Too little clean, still data in the 90 seconds. Ask the wearer to stand still, check the electrodes, and repeat. |

## Before an event

- Open the Supabase project (or run a short test session) so it is not paused.
- Run `bridge.py --synthetic`, then once with the headset on.
- Scan the QR code with a real phone outdoors and watch its dot.
- Check the map tiles load on the venue's network, and do a trial export.
