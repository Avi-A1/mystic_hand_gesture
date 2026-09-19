"""
MysticHand - Audio effects engine with procedural sound synthesis.
Generates sound effects without external audio files using numpy and sounddevice.
"""

import numpy as np
import sounddevice as sd
import threading
import queue

# Audio settings
SAMPLE_RATE = 44100
VOLUME = 0.15  # Keep it reasonable


class AudioEngine:
    """Manages procedural sound effects for Doctor Strange spells."""

    def __init__(self, enabled=True):
        self.enabled = enabled
        self.sound_queue = queue.Queue()
        self.worker = threading.Thread(target=self._audio_worker, daemon=True)
        self.worker.start()

    def _audio_worker(self):
        """Background thread to play sounds without blocking the main loop."""
        while True:
            sound_data = self.sound_queue.get()
            if sound_data is None:
                break
            try:
                sd.play(sound_data, SAMPLE_RATE, blocking=True)
            except Exception:
                pass  # Suppress audio errors silently

    def play_async(self, sound_data):
        """Queue a sound to play asynchronously."""
        if self.enabled and sound_data is not None:
            self.sound_queue.put(sound_data)

    # ─── Shield Sounds ───────────────────────────────────────────────────

    def shield_activate(self):
        """Deep hum with harmonic overtones — shield activation."""
        duration = 0.4
        t = np.linspace(0, duration, int(SAMPLE_RATE * duration))

        # Fundamental + harmonics
        freq = 120
        sound = (
            0.5 * np.sin(2 * np.pi * freq * t) +
            0.3 * np.sin(2 * np.pi * freq * 2 * t) +
            0.2 * np.sin(2 * np.pi * freq * 3 * t)
        )

        # Envelope: fast attack, slow decay
        envelope = np.exp(-t * 3)
        sound = sound * envelope * VOLUME
        self.play_async(sound.astype(np.float32))

    def shield_hum(self):
        """Soft continuous hum for active shield."""
        duration = 0.15
        t = np.linspace(0, duration, int(SAMPLE_RATE * duration))

        freq = 110
        sound = 0.3 * np.sin(2 * np.pi * freq * t) + 0.2 * np.sin(2 * np.pi * freq * 1.5 * t)
        sound = sound * VOLUME * 0.4
        self.play_async(sound.astype(np.float32))

    # ─── Attack Beam Sounds ──────────────────────────────────────────────

    def beam_fire(self):
        """Electric zap with rising pitch — energy beam."""
        duration = 0.3
        t = np.linspace(0, duration, int(SAMPLE_RATE * duration))

        # Rising frequency sweep
        freq_start = 300
        freq_end = 800
        freq = np.linspace(freq_start, freq_end, len(t))

        # Add noise for electric crackle
        noise = np.random.uniform(-0.2, 0.2, len(t))
        sound = np.sin(2 * np.pi * freq * t) + noise

        envelope = np.exp(-t * 5)
        sound = sound * envelope * VOLUME * 1.2
        self.play_async(sound.astype(np.float32))

    def beam_sustain(self):
        """Crackling sustain for active beam."""
        duration = 0.1
        t = np.linspace(0, duration, int(SAMPLE_RATE * duration))

        freq = 600
        noise = np.random.uniform(-0.3, 0.3, len(t))
        sound = 0.4 * np.sin(2 * np.pi * freq * t) + 0.6 * noise
        sound = sound * VOLUME * 0.5
        self.play_async(sound.astype(np.float32))

    # ─── Portal Sounds ───────────────────────────────────────────────────

    def portal_open(self):
        """Whooshing swirl with descending pitch — portal opening."""
        duration = 0.8
        t = np.linspace(0, duration, int(SAMPLE_RATE * duration))

        # Descending frequency
        freq = np.linspace(900, 150, len(t))
        sound = np.sin(2 * np.pi * freq * t)

        # Add white noise for whoosh
        noise = np.random.uniform(-0.4, 0.4, len(t))
        sound = 0.6 * sound + 0.4 * noise

        envelope = 1 - np.exp(-t * 8)  # Fade in
        sound = sound * envelope * VOLUME
        self.play_async(sound.astype(np.float32))

    def portal_active(self):
        """Swirling hum for active portal."""
        duration = 0.2
        t = np.linspace(0, duration, int(SAMPLE_RATE * duration))

        freq = 200
        sound = (
            0.4 * np.sin(2 * np.pi * freq * t) +
            0.3 * np.sin(2 * np.pi * freq * 1.3 * t) +
            0.3 * np.sin(2 * np.pi * freq * 1.7 * t)
        )
        sound = sound * VOLUME * 0.3
        self.play_async(sound.astype(np.float32))

    # ─── Time Stone Sounds ───────────────────────────────────────────────

    def time_stone_activate(self):
        """Mystical chime with reverb — Time Stone activation."""
        duration = 1.0
        t = np.linspace(0, duration, int(SAMPLE_RATE * duration))

        # Bell-like harmonics
        freqs = [523, 659, 784]  # C major chord
        sound = sum(np.sin(2 * np.pi * f * t) / len(freqs) for f in freqs)

        envelope = np.exp(-t * 2)
        sound = sound * envelope * VOLUME * 0.8
        self.play_async(sound.astype(np.float32))

    def time_stone_rewind(self):
        """Reversed whoosh for time manipulation."""
        duration = 0.5
        t = np.linspace(0, duration, int(SAMPLE_RATE * duration))

        freq = np.linspace(100, 600, len(t))
        sound = np.sin(2 * np.pi * freq * t)
        sound = sound[::-1]  # Reverse it

        envelope = np.exp(-t * 4)
        sound = sound * envelope * VOLUME * 0.6
        self.play_async(sound.astype(np.float32))

    # ─── Mirror Dimension Sounds ─────────────────────────────────────────

    def mirror_shatter(self):
        """Glass shatter with high-frequency crash."""
        duration = 0.6
        t = np.linspace(0, duration, int(SAMPLE_RATE * duration))

        # High-frequency noise burst
        noise = np.random.uniform(-1, 1, len(t))

        # Add high ringing
        freq = 3000
        ring = 0.3 * np.sin(2 * np.pi * freq * t)

        sound = 0.7 * noise + 0.3 * ring
        envelope = np.exp(-t * 8)
        sound = sound * envelope * VOLUME * 0.9
        self.play_async(sound.astype(np.float32))

    # ─── Crimson Bands Sounds ────────────────────────────────────────────

    def crimson_bands_whoosh(self):
        """Whip crack with sharp attack."""
        duration = 0.25
        t = np.linspace(0, duration, int(SAMPLE_RATE * duration))

        freq = 200
        sound = np.sin(2 * np.pi * freq * t)

        # Sharp attack envelope
        attack = np.exp(-t * 30)
        sound = sound * attack * VOLUME * 1.5
        self.play_async(sound.astype(np.float32))

    def stop(self):
        """Stop the audio worker thread."""
        self.sound_queue.put(None)
        self.worker.join()
