"""
MysticHand - Magic effects engine.

Renders all Doctor Strange visual effects:
  - Shield Mandala (Orange/Gold runes around palm)
  - Attack Beam (Supercharged electric orange/white beam)
  - Sling Ring Portal (Sparking orange gateway)
  - Time Stone (Green Agamotto time dials & green aura)
  - Mirror Dimension (Prismatic glass fracture & kaleidoscopic shards)
  - Crimson Bands of Cyttorak (Red energy whip & ribbon trails)
"""

import math
import random
import cv2
import numpy as np
from utils import (
    ORANGE_CORE, ORANGE_GLOW, GOLD, AMBER, WHITE_HOT,
    PORTAL_ORANGE, SPARK_YELLOW, SHIELD_BLUE,
    TIME_GREEN_CORE, TIME_GREEN_GLOW, TIME_GREEN_DARK,
    CRIMSON_CORE, CRIMSON_GLOW, CRIMSON_HOT,
    GLASS_CYAN, GLASS_MAGENTA, GLASS_SHINE,
    PARTICLE_LIFETIME, TRAIL_LENGTH, GLOW_INTENSITY,
    distance, midpoint, rotate_point, lerp, clamp,
)


# ─── Particle System ────────────────────────────────────────────────────────

class Particle:
    __slots__ = ('x', 'y', 'vx', 'vy', 'life', 'max_life', 'color', 'size')

    def __init__(self, x, y, vx, vy, life, color, size=2):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.life = life
        self.max_life = life
        self.color = color
        self.size = size

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vx *= 0.95
        self.vy *= 0.95
        self.life -= 1

    @property
    def alive(self):
        return self.life > 0

    @property
    def alpha(self):
        return clamp(self.life / self.max_life, 0, 1)


class ParticleSystem:
    def __init__(self, max_particles=600):
        self.particles = []
        self.max_particles = max_particles

    def emit(self, x, y, count=1, speed=2.0, color=ORANGE_CORE,
             lifetime=PARTICLE_LIFETIME, size=2, spread=2 * math.pi):
        for _ in range(count):
            if len(self.particles) >= self.max_particles:
                break
            angle = random.uniform(0, spread)
            spd = random.uniform(speed * 0.3, speed)
            self.particles.append(Particle(
                x + random.uniform(-3, 3),
                y + random.uniform(-3, 3),
                math.cos(angle) * spd,
                math.sin(angle) * spd,
                lifetime + random.randint(-5, 5),
                color,
                size,
            ))

    def update(self):
        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if p.alive]

    def draw(self, frame):
        overlay = frame.copy()
        for p in self.particles:
            alpha = p.alpha
            color = tuple(int(c * alpha) for c in p.color)
            pos = (int(p.x), int(p.y))
            cv2.circle(overlay, pos, p.size + 2, color, -1)
            cv2.circle(overlay, pos, p.size, WHITE_HOT, -1)
        cv2.addWeighted(overlay, GLOW_INTENSITY, frame, 1 - GLOW_INTENSITY, 0, frame)


# ─── Shield Effect ───────────────────────────────────────────────────────────

class ShieldEffect:
    def __init__(self):
        self.angle = 0.0
        self.particles = ParticleSystem(max_particles=200)
        self.active = False
        self._warmup = 0.0

    def update(self, center, radius):
        self.active = True
        self.angle += 0.05
        self._warmup = min(self._warmup + 0.1, 1.0)

        for _ in range(3):
            a = random.uniform(0, 2 * math.pi)
            r = radius * self._warmup
            sx = center[0] + math.cos(a) * r
            sy = center[1] + math.sin(a) * r
            self.particles.emit(sx, sy, count=1, speed=1.2,
                                color=random.choice([SPARK_YELLOW, GOLD]),
                                lifetime=15, size=1)
        self.particles.update()

    def deactivate(self):
        self.active = False
        self._warmup = max(self._warmup - 0.12, 0)
        self.particles.update()

    def draw(self, frame, center, radius):
        if self._warmup < 0.01:
            return

        r = int(radius * self._warmup)
        cx, cy = int(center[0]), int(center[1])
        overlay = frame.copy()

        cv2.circle(overlay, (cx, cy), r, ORANGE_GLOW, 2, cv2.LINE_AA)
        cv2.circle(overlay, (cx, cy), int(r * 0.75), ORANGE_CORE, 1, cv2.LINE_AA)
        cv2.circle(overlay, (cx, cy), int(r * 0.45), GOLD, 1, cv2.LINE_AA)

        num_segments = 6
        for i in range(num_segments):
            seg_angle = self.angle + (2 * math.pi * i / num_segments)
            p1 = (cx + int(math.cos(seg_angle) * r * 0.85),
                  cy + int(math.sin(seg_angle) * r * 0.85))
            p2 = (cx + int(math.cos(seg_angle) * r),
                  cy + int(math.sin(seg_angle) * r))
            cv2.line(overlay, p1, p2, ORANGE_CORE, 2, cv2.LINE_AA)

            inner_angle = -self.angle * 1.5 + (2 * math.pi * i / num_segments)
            p3 = (cx + int(math.cos(inner_angle) * r * 0.45),
                  cy + int(math.sin(inner_angle) * r * 0.45))
            p4 = (cx + int(math.cos(inner_angle) * r * 0.75),
                  cy + int(math.sin(inner_angle) * r * 0.75))
            cv2.line(overlay, p3, p4, GOLD, 1, cv2.LINE_AA)

        hex_r = int(r * 0.55)
        hex_pts = [
            (cx + int(math.cos(self.angle * 0.8 + (math.pi / 3) * i) * hex_r),
             cy + int(math.sin(self.angle * 0.8 + (math.pi / 3) * i) * hex_r))
            for i in range(6)
        ]
        for i in range(6):
            cv2.line(overlay, hex_pts[i], hex_pts[(i + 1) % 6], AMBER, 1, cv2.LINE_AA)

        for i in range(0, 6, 2):
            cv2.line(overlay, hex_pts[i], hex_pts[(i + 3) % 6], SHIELD_BLUE, 1, cv2.LINE_AA)

        cv2.addWeighted(overlay, 0.75, frame, 0.25, 0, frame)
        self.particles.draw(frame)


# ─── Attack Beam Effect ──────────────────────────────────────────────────────

class AttackBeamEffect:
    def __init__(self):
        self.particles = ParticleSystem(max_particles=600)
        self.active = False
        self.beam_points = []
        self.pulse = 0.0

    def update(self, pinch_point, direction_vec):
        self.active = True
        self.pulse += 0.2

        beam_length = 500
        end_x = pinch_point[0] + direction_vec[0] * beam_length
        end_y = pinch_point[1] + direction_vec[1] * beam_length
        self.beam_points = [pinch_point, (int(end_x), int(end_y))]

        num_segments = 15
        for i in range(num_segments):
            t = i / num_segments
            px = int(pinch_point[0] + direction_vec[0] * beam_length * t)
            py = int(pinch_point[1] + direction_vec[1] * beam_length * t)
            self.particles.emit(
                px, py, count=2, speed=3.5,
                color=random.choice([ORANGE_CORE, GOLD, SPARK_YELLOW, WHITE_HOT]),
                lifetime=20, size=3,
            )

        self.particles.update()

    def deactivate(self):
        self.active = False
        self.beam_points = []
        self.particles.update()

    def draw(self, frame):
        if not self.beam_points or len(self.beam_points) < 2:
            self.particles.draw(frame)
            return

        overlay = frame.copy()
        pt1, pt2 = self.beam_points[0], self.beam_points[1]
        base_thick = 8 + int(math.sin(self.pulse) * 3)

        cv2.line(overlay, pt1, pt2, ORANGE_GLOW, base_thick + 14, cv2.LINE_AA)
        cv2.line(overlay, pt1, pt2, ORANGE_CORE, base_thick + 6, cv2.LINE_AA)
        cv2.line(overlay, pt1, pt2, GOLD, base_thick + 2, cv2.LINE_AA)
        cv2.line(overlay, pt1, pt2, WHITE_HOT, max(2, base_thick - 3), cv2.LINE_AA)

        dx = pt2[0] - pt1[0]
        dy = pt2[1] - pt1[1]
        length = math.hypot(dx, dy)
        if length > 0:
            nx, ny = -dy / length, dx / length
            for _ in range(4):
                t1 = random.uniform(0.1, 0.8)
                t2 = min(t1 + random.uniform(0.1, 0.2), 0.95)
                arc_p1 = (int(pt1[0] + dx * t1), int(pt1[1] + dy * t1))
                arc_p2 = (int(pt1[0] + dx * t2), int(pt1[1] + dy * t2))
                offset = random.uniform(-20, 20)
                mid = (int((arc_p1[0] + arc_p2[0]) / 2 + nx * offset),
                       int((arc_p1[1] + arc_p2[1]) / 2 + ny * offset))
                cv2.line(overlay, arc_p1, mid, SPARK_YELLOW, 2, cv2.LINE_AA)
                cv2.line(overlay, mid, arc_p2, SPARK_YELLOW, 2, cv2.LINE_AA)

        cv2.circle(overlay, pt1, 22, ORANGE_GLOW, -1, cv2.LINE_AA)
        cv2.circle(overlay, pt1, 12, ORANGE_CORE, -1, cv2.LINE_AA)
        cv2.circle(overlay, pt1, 6, WHITE_HOT, -1, cv2.LINE_AA)

        cv2.circle(overlay, pt2, 16, ORANGE_GLOW, -1, cv2.LINE_AA)
        cv2.circle(overlay, pt2, 8, SPARK_YELLOW, -1, cv2.LINE_AA)
        cv2.circle(overlay, pt2, 4, WHITE_HOT, -1, cv2.LINE_AA)

        cv2.addWeighted(overlay, 0.8, frame, 0.2, 0, frame)
        self.particles.draw(frame)


# ─── Portal Effect ───────────────────────────────────────────────────────────

class PortalEffect:
    def __init__(self):
        self.angle = 0.0
        self.particles = ParticleSystem(max_particles=400)
        self.active = False
        self._warmup = 0.0

    def update(self, center, radius, rotation_amount):
        self.active = True
        self.angle += 0.06
        self._warmup = min(self._warmup + 0.05, 1.0)
        effective_r = radius * self._warmup

        num_sparks = int(8 * self._warmup)
        for _ in range(num_sparks):
            a = random.uniform(0, 2 * math.pi)
            sx = center[0] + math.cos(a) * effective_r
            sy = center[1] + math.sin(a) * effective_r
            self.particles.emit(
                sx, sy, count=1, speed=2.5,
                color=random.choice([PORTAL_ORANGE, SPARK_YELLOW, GOLD]),
                lifetime=18, size=2,
            )
        self.particles.update()

    def deactivate(self):
        self.active = False
        self._warmup = max(self._warmup - 0.06, 0)
        self.particles.update()

    def draw(self, frame, center, radius):
        if self._warmup < 0.01:
            return

        r = int(radius * self._warmup)
        cx, cy = int(center[0]), int(center[1])
        overlay = frame.copy()

        wobble = math.sin(self.angle * 3) * 0.1
        axes = (r, int(r * (0.95 + wobble)))

        cv2.ellipse(overlay, (cx, cy), (r + 8, axes[1] + 8), 0, 0, 360, ORANGE_GLOW, 4, cv2.LINE_AA)
        cv2.ellipse(overlay, (cx, cy), axes, math.degrees(self.angle * 0.3), 0, 360, PORTAL_ORANGE, 3, cv2.LINE_AA)

        num_spark_points = 12
        for i in range(num_spark_points):
            sa = self.angle * 2 + (2 * math.pi * i / num_spark_points)
            sx = cx + int(math.cos(sa) * r)
            sy = cy + int(math.sin(sa) * axes[1])
            cv2.circle(overlay, (sx, sy), 3 if i % 3 == 0 else 2, SPARK_YELLOW, -1, cv2.LINE_AA)

        cv2.addWeighted(overlay, 0.65, frame, 0.35, 0, frame)
        self.particles.draw(frame)


# ─── Time Stone (Eye of Agamotto) Effect ─────────────────────────────────────

class TimeStoneEffect:
    """Green glowing Agamotto time dials with rotating clock glyphs & rewind aura."""

    def __init__(self):
        self.angle = 0.0
        self.particles = ParticleSystem(max_particles=300)
        self.active = False
        self._warmup = 0.0

    def update(self, center, radius):
        self.active = True
        self.angle -= 0.08  # Counter-clockwise rotation for time rewind!
        self._warmup = min(self._warmup + 0.08, 1.0)

        # Green sparks
        for _ in range(4):
            a = random.uniform(0, 2 * math.pi)
            r = radius * self._warmup * random.uniform(0.6, 1.1)
            sx = center[0] + math.cos(a) * r
            sy = center[1] + math.sin(a) * r
            self.particles.emit(
                sx, sy, count=1, speed=1.5,
                color=random.choice([TIME_GREEN_CORE, TIME_GREEN_GLOW, WHITE_HOT]),
                lifetime=20, size=2,
            )
        self.particles.update()

    def deactivate(self):
        self.active = False
        self._warmup = max(self._warmup - 0.1, 0)
        self.particles.update()

    def draw(self, frame, center, radius):
        if self._warmup < 0.01:
            return

        r = int(radius * self._warmup)
        cx, cy = int(center[0]), int(center[1])
        overlay = frame.copy()

        # Concentric Time Dials
        cv2.circle(overlay, (cx, cy), r, TIME_GREEN_GLOW, 3, cv2.LINE_AA)
        cv2.circle(overlay, (cx, cy), int(r * 0.75), TIME_GREEN_CORE, 2, cv2.LINE_AA)
        cv2.circle(overlay, (cx, cy), int(r * 0.45), TIME_GREEN_DARK, 2, cv2.LINE_AA)

        # Eye of Agamotto almond shape at center
        eye_w = int(r * 0.35)
        eye_h = int(r * 0.18)
        cv2.ellipse(overlay, (cx, cy), (eye_w, eye_h), 0, 0, 360, TIME_GREEN_CORE, 2, cv2.LINE_AA)
        cv2.circle(overlay, (cx, cy), int(r * 0.08), WHITE_HOT, -1, cv2.LINE_AA)

        # 12 Clock Rune Marks (like a mystical time dial)
        for i in range(12):
            clock_a = self.angle + (2 * math.pi * i / 12)
            p1 = (cx + int(math.cos(clock_a) * r * 0.8),
                  cy + int(math.sin(clock_a) * r * 0.8))
            p2 = (cx + int(math.cos(clock_a) * r * 0.98),
                  cy + int(math.sin(clock_a) * r * 0.98))
            thick = 3 if i % 3 == 0 else 1
            cv2.line(overlay, p1, p2, TIME_GREEN_CORE, thick, cv2.LINE_AA)

        # Reverse time spiral
        num_spiral_pts = 20
        spiral_pts = []
        for i in range(num_spiral_pts):
            sa = self.angle * 2 + i * 0.3
            sr = (r * 0.7) * (i / num_spiral_pts)
            spiral_pts.append((
                cx + int(math.cos(sa) * sr),
                cy + int(math.sin(sa) * sr),
            ))
        for i in range(len(spiral_pts) - 1):
            cv2.line(overlay, spiral_pts[i], spiral_pts[i + 1], TIME_GREEN_CORE, 2, cv2.LINE_AA)

        cv2.addWeighted(overlay, 0.75, frame, 0.25, 0, frame)
        self.particles.draw(frame)


# ─── Mirror Dimension Effect ─────────────────────────────────────────────────

class MirrorDimensionEffect:
    """Kaleidoscopic glass fracture lines shattering reality across the frame."""

    def __init__(self):
        self.active = False
        self._warmup = 0.0
        self.fracture_lines = []
        self.angle = 0.0

    def update(self, center):
        self.active = True
        self.angle += 0.03
        self._warmup = min(self._warmup + 0.1, 1.0)

        # Generate shards once
        if not self.fracture_lines:
            cx, cy = center
            for _ in range(16):
                angle = random.uniform(0, 2 * math.pi)
                length = random.uniform(200, 600)
                end_x = int(cx + math.cos(angle) * length)
                end_y = int(cy + math.sin(angle) * length)
                self.fracture_lines.append(((cx, cy), (end_x, end_y)))

    def deactivate(self):
        self.active = False
        self._warmup = max(self._warmup - 0.1, 0)
        if self._warmup == 0:
            self.fracture_lines = []

    def draw(self, frame, center):
        if self._warmup < 0.01 or not center:
            return

        h, w = frame.shape[:2]
        cx, cy = center
        overlay = frame.copy()

        # Prismatic Glass Shard Lines radiating from center
        for (p1, p2) in self.fracture_lines:
            target = (
                int(cx + (p2[0] - cx) * self._warmup),
                int(cy + (p2[1] - cy) * self._warmup),
            )
            cv2.line(overlay, (cx, cy), target, GLASS_SHINE, 2, cv2.LINE_AA)
            cv2.line(overlay, (cx, cy), target, GLASS_CYAN, 1, cv2.LINE_AA)

            # Secondary cracks branching off
            mid = ((cx + target[0]) // 2, (cy + target[1]) // 2)
            branch = (mid[0] + random.randint(-40, 40), mid[1] + random.randint(-40, 40))
            cv2.line(overlay, mid, branch, GLASS_MAGENTA, 1, cv2.LINE_AA)

        # Central prismatic shatter portal
        r = int(70 * self._warmup)
        for i in range(6):
            poly_a = self.angle + (math.pi / 3) * i
            poly_p1 = (cx + int(math.cos(poly_a) * r), cy + int(math.sin(poly_a) * r))
            poly_p2 = (cx + int(math.cos(poly_a + math.pi / 3) * r), cy + int(math.sin(poly_a + math.pi / 3) * r))
            cv2.line(overlay, poly_p1, poly_p2, GLASS_SHINE, 3, cv2.LINE_AA)

        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)


# ─── Crimson Bands of Cyttorak Effect ────────────────────────────────────────

class CrimsonBandsEffect:
    """Enhanced ruby red energy whip/ribbon with velocity-based intensity and flowing motion."""

    def __init__(self):
        self.trail = []
        self.particles = ParticleSystem(max_particles=500)
        self.active = False
        self.pulse = 0.0
        self.prev_point = None

    def update(self, tip_point):
        self.active = True
        self.pulse += 0.18

        # Calculate velocity for intensity
        velocity = 0
        if self.prev_point:
            velocity = distance(tip_point, self.prev_point)
        self.prev_point = tip_point

        self.trail.append((tip_point, velocity))
        if len(self.trail) > 35:  # Longer trail
            self.trail.pop(0)

        # More crimson particles based on velocity
        particle_count = int(5 + min(velocity * 0.5, 15))
        self.particles.emit(
            tip_point[0], tip_point[1],
            count=particle_count, speed=4.0 + velocity * 0.1,
            color=random.choice([CRIMSON_CORE, CRIMSON_HOT, WHITE_HOT]),
            lifetime=25, size=3,
            spread=math.pi  # Emit behind the motion
        )
        self.particles.update()

    def deactivate(self):
        self.active = False
        if self.trail:
            self.trail.pop(0)
        self.particles.update()
        self.prev_point = None

    def draw(self, frame):
        if len(self.trail) < 2:
            self.particles.draw(frame)
            return

        overlay = frame.copy()

        # Draw flowing ribbon whip with velocity-reactive thickness
        for i in range(1, len(self.trail)):
            alpha = i / len(self.trail)
            point, velocity = self.trail[i]

            # Thickness increases with velocity
            base_thickness = 12 + int(min(velocity * 0.3, 10))
            thickness = max(2, int(base_thickness * alpha))

            pt1 = (int(self.trail[i - 1][0][0]), int(self.trail[i - 1][0][1]))
            pt2 = (int(point[0]), int(point[1]))

            # Multi-layer whip ribbon
            # Outer crimson glow aura
            cv2.line(overlay, pt1, pt2, CRIMSON_GLOW, thickness + 18, cv2.LINE_AA)

            # Middle ruby red band
            cv2.line(overlay, pt1, pt2, CRIMSON_CORE, thickness + 8, cv2.LINE_AA)

            # Inner hot pink/white core
            if alpha > 0.4:
                cv2.line(overlay, pt1, pt2, CRIMSON_HOT, max(2, thickness + 2), cv2.LINE_AA)

            # Brightest center streak
            if alpha > 0.7:
                cv2.line(overlay, pt1, pt2, WHITE_HOT, max(1, thickness - 4), cv2.LINE_AA)

        # Massive glowing orb at the whip tip
        if self.trail:
            tip, tip_velocity = self.trail[-1]
            tip_pos = (int(tip[0]), int(tip[1]))

            # Velocity makes the tip bigger
            tip_size = int(20 + min(tip_velocity * 0.4, 15))

            cv2.circle(overlay, tip_pos, tip_size + 12, CRIMSON_GLOW, -1, cv2.LINE_AA)
            cv2.circle(overlay, tip_pos, tip_size + 4, CRIMSON_CORE, -1, cv2.LINE_AA)
            cv2.circle(overlay, tip_pos, tip_size, CRIMSON_HOT, -1, cv2.LINE_AA)
            cv2.circle(overlay, tip_pos, max(4, tip_size // 2), WHITE_HOT, -1, cv2.LINE_AA)

            # Velocity streaks radiating from tip
            if tip_velocity > 5:
                for _ in range(6):
                    streak_angle = random.uniform(0, 2 * math.pi)
                    streak_len = random.uniform(20, 50)
                    streak_end = (
                        int(tip_pos[0] + math.cos(streak_angle) * streak_len),
                        int(tip_pos[1] + math.sin(streak_angle) * streak_len)
                    )
                    cv2.line(overlay, tip_pos, streak_end, CRIMSON_HOT, 2, cv2.LINE_AA)

        cv2.addWeighted(overlay, 0.8, frame, 0.2, 0, frame)
        self.particles.draw(frame)


# ─── Unified Effects Engine ──────────────────────────────────────────────────

class EffectsEngine:
    """Manages all 6 Doctor Strange effects."""

    def __init__(self):
        self.shields = [ShieldEffect(), ShieldEffect()]
        self.attack = AttackBeamEffect()
        self.portal = PortalEffect()
        self.time_stone = TimeStoneEffect()
        self.mirror = MirrorDimensionEffect()
        self.crimson = CrimsonBandsEffect()

    def update_shield(self, hand_idx, center, radius):
        if hand_idx < len(self.shields):
            self.shields[hand_idx].update(center, radius)

    def update_attack(self, pinch_point, direction_vec):
        self.attack.update(pinch_point, direction_vec)

    def update_portal(self, center, radius, rotation):
        self.portal.update(center, radius, rotation)

    def update_time_stone(self, center, radius):
        self.time_stone.update(center, radius)

    def update_mirror(self, center):
        self.mirror.update(center)

    def update_crimson(self, tip_point):
        self.crimson.update(tip_point)

    def deactivate_shield(self, hand_idx=None):
        if hand_idx is not None and hand_idx < len(self.shields):
            self.shields[hand_idx].deactivate()
        else:
            for s in self.shields:
                s.deactivate()

    def deactivate_attack(self):
        self.attack.deactivate()

    def deactivate_portal(self):
        self.portal.deactivate()

    def deactivate_time_stone(self):
        self.time_stone.deactivate()

    def deactivate_mirror(self):
        self.mirror.deactivate()

    def deactivate_crimson(self):
        self.crimson.deactivate()

    def draw(self, frame, shields_data=None, attack_data=None, portal_data=None,
             time_stone_data=None, mirror_data=None, crimson_data=None):
        # 1. Shields
        if shields_data:
            for idx, s_data in enumerate(shields_data):
                if idx < len(self.shields) and s_data:
                    self.shields[idx].draw(frame, s_data[0], s_data[1])
        else:
            for s in self.shields:
                if s._warmup > 0:
                    s.draw(frame, (0, 0), 0)

        # 2. Attack Beam
        if attack_data or self.attack.active:
            self.attack.draw(frame)

        # 3. Portal
        if portal_data:
            self.portal.draw(frame, portal_data[0], portal_data[1])
        elif self.portal._warmup > 0:
            self.portal.draw(frame, (0, 0), 0)

        # 4. Time Stone
        if time_stone_data:
            self.time_stone.draw(frame, time_stone_data[0], time_stone_data[1])
        elif self.time_stone._warmup > 0:
            self.time_stone.draw(frame, (0, 0), 0)

        # 5. Mirror Dimension
        if mirror_data:
            self.mirror.draw(frame, mirror_data)
        elif self.mirror._warmup > 0:
            self.mirror.draw(frame, None)

        # 6. Crimson Bands
        if crimson_data or self.crimson.trail:
            self.crimson.draw(frame)
