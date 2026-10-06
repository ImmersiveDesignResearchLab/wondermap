"""
xi / WonderMap EEG bridge  -  built on g.tec's Unicorn Suite
Unicorn Recorder (band-pass + notch + OSCAR)  ->  LSL  ->  this bridge  ->  ws://localhost:8765  ->  WonderMap

g.tec cleans the signal. This bridge adds what a filter cannot do:
  1. FILTER   (g.tec)  Unicorn Recorder applies its cascading band-pass + notch filters (and OSCAR
                       artifact removal where enabled). Run this script with --prefiltered to use
                       that stream as-is. Without --prefiltered the bridge applies its own
                       1-40 Hz band-pass + mains notch as a fallback for a raw stream.
  2. REJECT   (xi)     any channel with peak-to-peak > --ptp uV -> window dropped, WonderMap holds
                       the last clean value (head bumps, electrode pops, big blinks).
  3. GATE     (xi)     the headset's accelerometer + gyroscope label each window STILL or MOVING.
                       WonderMap scores the wonder signature (theta up, beta down) only when STILL,
                       because walking artifacts overlap theta/alpha/beta and no filter can separate them.
  4. BANDS    (xi)     theta / alpha / beta power per electrode cluster, 4 updates per second.

Raw EEG stays on this Surface. Only 4 Hz band summaries are sent on.

Setup (once):   pip install pylsl numpy scipy websockets
Unicorn Suite:  start Unicorn Recorder, connect the headset, choose the band-pass + notch filters,
                enable LSL output, and note the LSL stream name.
Usage:
    python bridge.py --prefiltered                      # Recorder's filtered LSL stream (recommended)
    python bridge.py --prefiltered --stream "MyStream"  # pick the stream by name
    python bridge.py                                    # raw stream: bridge filters it itself
    python bridge.py --synthetic                        # fake EEG + walking, no headset needed
    python bridge.py --pid 2 --line 60 --ptp 150 --gyro 30 --acc 0.08
Stop with Ctrl+C.

NOTE: IMU channel positions assume the standard Unicorn stream order (8 EEG, then accelerometer
X/Y/Z, then gyroscope X/Y/Z). The channel labels are printed on connect: check them once, and
check that the Recorder's LSL stream includes the motion channels.
"""

import argparse
import asyncio
import collections
import json
import math
import random
import time

import numpy as np
import websockets
from scipy.signal import butter, iirnotch, sosfiltfilt, tf2sos

FS = 250
WIN_S, HOP_S = 2.0, 0.25
PORT = 8765
BANDS = {"theta": (4, 8), "alpha": (8, 12), "beta": (13, 30)}
CLUSTERS = {
    "theta": [0, 1, 2, 3],   # Fz, C3, Cz, C4   frontal-central
    "alpha": [4, 5, 6, 7],   # Pz, PO7, Oz, PO8 parieto-occipital
    "beta":  [1, 2, 3, 4],   # C3, Cz, C4, Pz   central-parietal
}
ACC_IDX, GYR_IDX = [8, 9, 10], [11, 12, 13]

clients = set()


# ── SIGNAL PROCESSING ────────────────────────────────────────────
def make_filter(line_hz: int):
    """Fallback filter, used only when the stream is NOT already filtered by g.tec's Recorder."""
    sos = butter(4, [1.0, 40.0], btype="band", fs=FS, output="sos")
    if line_hz:
        b, a = iirnotch(line_hz, 30.0, fs=FS)
        sos = np.vstack([sos, tf2sos(b, a)])
    return sos


def prepare_window(raw8: np.ndarray, sos=None) -> np.ndarray:
    """raw8: (samples, 8). sos=None means the stream is pre-filtered by g.tec: just centre it."""
    x = raw8 - raw8.mean(axis=0)
    return x if sos is None else sosfiltfilt(sos, x, axis=0)


def band_powers(eeg: np.ndarray) -> dict:
    taper = np.hanning(len(eeg))[:, None]
    spec = np.abs(np.fft.rfft(eeg * taper, axis=0)) ** 2
    freqs = np.fft.rfftfreq(len(eeg), 1.0 / FS)
    out = {}
    for band, (lo, hi) in BANDS.items():
        m = (freqs >= lo) & (freqs < hi)
        out[band] = round(float(spec[m][:, CLUSTERS[band]].mean()), 4)
    return out


def motion_state(imu: np.ndarray, gyro_thr: float, acc_thr: float):
    """imu: last 1 s of [accX,accY,accZ,gyrX,gyrY,gyrZ]. Returns (still, gyro_dps, acc_g)."""
    gyro = float(np.linalg.norm(imu[:, 3:6], axis=1).mean())        # head rotation, deg/s
    acc = float(np.linalg.norm(imu[:, 0:3], axis=1).std())          # dynamic acceleration, g
    return (gyro < gyro_thr and acc < acc_thr), round(gyro, 2), round(acc, 4)


# ── WEBSOCKET ────────────────────────────────────────────────────
async def broadcast(msg: dict) -> None:
    if not clients:
        return
    data = json.dumps(msg)
    for c in list(clients):
        try:
            await c.send(data)
        except Exception:
            clients.discard(c)


async def handler(ws):
    clients.add(ws)
    print(f"  WonderMap connected ({len(clients)} open)")
    try:
        async for _ in ws:
            pass
    finally:
        clients.discard(ws)
        print(f"  WonderMap disconnected ({len(clients)} open)")


# ── LIVE ─────────────────────────────────────────────────────────
async def live_loop(args) -> None:
    from pylsl import StreamInlet, resolve_streams

    print("Looking for the LSL stream - in Unicorn Recorder, enable LSL output...")
    stream = None
    while stream is None:
        found = await asyncio.to_thread(resolve_streams, 2.0)
        if args.stream:
            cands = [s for s in found if args.stream.lower() in s.name().lower()]
        else:
            cands = ([s for s in found if s.type().lower() == "eeg"]
                     or [s for s in found if "unicorn" in s.name().lower()] or found)
        cands = [s for s in cands if s.channel_count() >= 8]
        if cands:
            stream = cands[0]
        else:
            print("  ...not found yet, still looking")

    inlet = StreamInlet(stream, max_buflen=10)
    nch = stream.channel_count()
    has_imu = nch >= 14
    sos = None if args.prefiltered else make_filter(args.line)
    print(f"Connected to '{stream.name()}' ({nch} channels).")
    print(f"  Filtering : {'g.tec Unicorn Recorder (stream used as-is)' if args.prefiltered else f'bridge fallback 1-40 Hz + {args.line} Hz notch (stream assumed raw)'}")
    print(f"  Motion gate: {'ON (accelerometer + gyroscope found)' if has_imu else 'OFF - stream has no motion channels'}")
    try:
        ch = inlet.info().desc().child("channels").child("channel")
        labels = []
        for _ in range(nch):
            labels.append(ch.child_value("label") or "?")
            ch = ch.next_sibling()
        print("  Channel labels:", ", ".join(labels))
    except Exception:
        pass

    n, n_imu = int(WIN_S * FS), FS
    buf = np.zeros((0, nch))
    last_data, warned = time.time(), False
    history = collections.deque(maxlen=40)          # 10 s of clean/rejected flags
    last_print = 0.0

    while True:
        chunk, _ = inlet.pull_chunk(timeout=0.0, max_samples=FS)
        if chunk:
            buf = np.vstack([buf, np.asarray(chunk, dtype=float)])[-n:]
            last_data, warned = time.time(), False

        if time.time() - last_data > 2.0:
            if not warned:
                print("  !! No EEG for 2 s - check Bluetooth range / headset")
                warned = True
            await broadcast({"type": "EEG_STATUS", "id": args.pid, "status": "no_signal"})
        elif len(buf) >= n:
            eeg = prepare_window(buf[:, :8], sos)
            ptp = float(np.ptp(eeg, axis=0).max())
            still, gyro, acc = (motion_state(buf[-n_imu:, ACC_IDX + GYR_IDX], args.gyro, args.acc)
                                if has_imu else (None, None, None))
            clean = ptp <= args.ptp
            history.append(clean)
            quality = round(sum(history) / len(history), 2)
            msg = {"type": "EEG", "id": args.pid, "t": time.time(), "clean": clean,
                   "still": still, "quality": quality, "ptp_uv": round(ptp, 1),
                   "prefiltered": args.prefiltered,
                   "motion": {"gyro_dps": gyro, "acc_g": acc}}
            if clean:
                msg.update(band_powers(eeg))
            else:
                msg["reason"] = "amplitude"
            await broadcast(msg)

            if time.time() - last_print > 2.0:          # live console readout for tuning
                state = "STILL " if still else ("MOVING" if still is False else "no IMU")
                print(f"  {state}  clean {int(quality*100):3d}%  ptp {ptp:6.1f} uV  "
                      f"gyro {gyro} dps  acc {acc} g")
                last_print = time.time()

        await asyncio.sleep(HOP_S)


# ── SYNTHETIC ────────────────────────────────────────────────────
async def synthetic_loop(args) -> None:
    print("SYNTHETIC mode - wonder episodes ~every 2 min, walking every 30 s, occasional artifacts.")
    t0 = time.time()
    history = collections.deque(maxlen=40)
    while True:
        t = time.time() - t0
        walking = (t % 30) < 10
        wonder = math.sin(t / 20.0) > 0.6 and not walking
        clean = random.random() > (0.15 if walking else 0.03)
        history.append(clean)
        g = lambda: random.gauss(0, 0.05)
        msg = {"type": "EEG", "id": args.pid, "t": time.time(), "clean": clean, "still": not walking,
               "quality": round(sum(history) / len(history), 2), "synthetic": True,
               "prefiltered": args.prefiltered,
               "motion": {"gyro_dps": round(random.uniform(40, 90) if walking else random.uniform(2, 12), 2),
                          "acc_g": round(random.uniform(0.1, 0.3) if walking else random.uniform(0.005, 0.03), 4)}}
        if clean:
            msg.update({
                "theta": round(10 * (1 + 0.15 * math.sin(t / 3) + (0.6 if wonder else 0) + g()), 4),
                "alpha": round(12 * (1 + 0.20 * math.sin(t / 5 + 1) + (0.3 if wonder else 0) + g()), 4),
                "beta":  round(6 * (1 + 0.10 * math.sin(t / 4 + 2) - (0.4 if wonder else 0) + g()), 4)})
        else:
            msg["reason"] = "amplitude"
        await broadcast(msg)
        await asyncio.sleep(HOP_S)


# ── MAIN ─────────────────────────────────────────────────────────
async def main() -> None:
    p = argparse.ArgumentParser(description="xi / WonderMap bridge: g.tec-filtered EEG + motion gate")
    p.add_argument("--prefiltered", action="store_true",
                   help="stream is already filtered by g.tec's Unicorn Recorder: do not filter again")
    p.add_argument("--stream", default="", help="LSL stream name (or part of it) to connect to")
    p.add_argument("--synthetic", action="store_true", help="fake EEG for testing")
    p.add_argument("--pid", default="1", help="participant ID wearing the headset")
    p.add_argument("--line", type=int, default=60, choices=[0, 50, 60],
                   help="fallback mains notch (Hz), only used without --prefiltered; 0 = off")
    p.add_argument("--ptp", type=float, default=150.0, help="reject window if any channel exceeds this uV")
    p.add_argument("--gyro", type=float, default=30.0, help="still if mean head rotation below (deg/s)")
    p.add_argument("--acc", type=float, default=0.08, help="still if dynamic acceleration below (g)")
    args = p.parse_args()

    async with websockets.serve(handler, "localhost", PORT):
        print(f"Bridge at ws://localhost:{PORT}  participant {args.pid}  "
              f"filtering: {'g.tec Recorder' if args.prefiltered else 'bridge fallback'}  "
              f"reject >{args.ptp} uV  still: gyro<{args.gyro} dps, acc<{args.acc} g")
        print("Open WonderMap on this Surface. Ctrl+C to stop.\n")
        await (synthetic_loop if args.synthetic else live_loop)(args)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBridge stopped.")
