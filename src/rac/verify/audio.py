"""rac.verify.audio — 渲染产物音频断言 (纯标准库: wave + audioop + Goertzel)

用法:
    expect_audio("out.wav").not_silent().duration(1.0, tol=0.05) \\
        .dominant_freq(440, tol=5).rms_above(0.1)
"""
from __future__ import annotations

import audioop
import math
import wave
from pathlib import Path


class AudioExpectError(AssertionError):
    pass


def _read_mono(path: str | Path) -> tuple[bytes, int, int]:
    """返回 (16bit mono pcm bytes, samplerate, frames)。

    立体声: 取 RMS 较大的声道 (0.5/0.5 下混会让反相内容抵消成静音——
    断言场景取较强声道更稳)。"""
    with wave.open(str(path), "rb") as w:
        nch, sw, sr, frames = w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getnframes()
        raw = w.readframes(frames)
        if sw == 3:  # 24-bit (REAPER 默认渲染位深) → 转 16-bit
            raw = audioop.lin2lin(raw, 3, 2)
            sw = 2
        elif sw != 2:
            raise AudioExpectError(f"unsupported sampwidth {sw} (expect 16/24bit)")
        if nch == 2:
            left = audioop.tomono(raw, 2, 1.0, 0.0)
            right = audioop.tomono(raw, 2, 0.0, 1.0)
            raw = left if audioop.rms(left, 2) >= audioop.rms(right, 2) else right
        elif nch != 1:
            raise AudioExpectError(f"unsupported channels {nch}")
        return raw, sr, frames


def _goertzel(pcm: bytes, sr: int, target: float) -> float:
    """目标频率的能量 (Goertzel, 全文件窗口)。
    短音频守卫: n*target/sr < 1 时 bin 量化为 0 (无意义), 返回 0。"""
    n = len(pcm) // 2
    if n == 0:
        return 0.0
    k = int(0.5 + n * target / sr)
    if k == 0:
        return 0.0
    w = 2 * math.pi * k / n
    cw = math.cos(w)
    coeff = 2 * cw
    s0 = s1 = s2 = 0.0
    for i in range(n):
        v = int.from_bytes(pcm[2 * i:2 * i + 2], "little", signed=True) / 32768.0
        s0 = v + coeff * s1 - s2
        s2 = s1
        s1 = s0
    return math.sqrt(s1 * s1 + s2 * s2 - coeff * s1 * s2) / n


class AudioExpect:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        if not self.path.exists():
            raise AudioExpectError(f"audio not found: {path}")
        self.pcm, self.sr, self.frames = _read_mono(self.path)
        self._rms = None

    @property
    def rms(self) -> float:
        if self._rms is None:
            self._rms = audioop.rms(self.pcm, 2) / 32768.0
        return self._rms

    def duration(self, seconds: float, tol: float = 0.1) -> "AudioExpect":
        actual = self.frames / self.sr
        if abs(actual - seconds) > tol:
            raise AudioExpectError(f"duration: expect {seconds}s±{tol}, got {actual:.3f}s")
        return self

    def not_silent(self, rms_floor: float = 0.001) -> "AudioExpect":
        if self.rms < rms_floor:
            raise AudioExpectError(f"silent: rms {self.rms:.6f} < {rms_floor}")
        return self

    def rms_above(self, floor: float) -> "AudioExpect":
        if self.rms < floor:
            raise AudioExpectError(f"rms {self.rms:.4f} < {floor}")
        return self

    def rms_below(self, ceil: float) -> "AudioExpect":
        if self.rms > ceil:
            raise AudioExpectError(f"rms {self.rms:.4f} > {ceil}")
        return self

    def dominant_freq(self, freq: float, tol: float = 10.0) -> "AudioExpect":
        """主峰频率断言: 过零率粗估 + Goertzel 局部细化。
        (对数粗扫会整段错过 bin 中心峰值——Goertzel 整数 k 即 DFT bin,
        泄漏为零, 粗扫极易假绿/假负; 过零率对 tonal 信号稳)"""
        n = len(self.pcm) // 2
        if n == 0:
            raise AudioExpectError("empty audio")
        # 过零率粗估 (下采样到 ~8k 以提速)。
        # 在最响 50ms 窗内统计: 全文件 ZCR 会被静音间隙稀释 (lofi gap-tone 实测
        # est=1607 ≠ 真实 2000, Goertzel 细化区间随之跑偏); 稳态音结果不变。
        step = max(1, self.sr // 8000)
        win = max(self.sr // 20, step * 4)
        best_rms, best_off = -1.0, 0
        for w_off in range(0, n - win + 1, win):
            r = audioop.rms(self.pcm[2 * w_off:2 * (w_off + win)], 2)
            if r > best_rms:
                best_rms, best_off = r, w_off
        crossings = 0
        prev = int.from_bytes(self.pcm[2 * best_off:2 * best_off + 2], "little", signed=True)
        count = 0
        for i in range(best_off + step, best_off + win, step):
            v = int.from_bytes(self.pcm[2 * i:2 * i + 2], "little", signed=True)
            if (prev < 0) != (v < 0):
                crossings += 1
            prev = v
            count += 1
        dur = count * step / self.sr
        if crossings == 0 or dur == 0:
            raise AudioExpectError("no zero crossings (DC/silent?)")
        est = crossings / (2 * dur)
        # 谐波陷阱: ZCR 会锁到强谐波 (如 440+0.9*880 时 zcr≈880),
        # 候选必须含次谐波: est/4, est/3, est/2 与 est 自身各做整数 bin 细化
        def refine(center: float) -> tuple[float, float]:
            bf, be = center, 0.0
            for k in range(max(1, int(center * 0.9)), int(center * 1.1) + 2):
                e = _goertzel(self.pcm, self.sr, float(k))
                if e > be:
                    bf, be = float(k), e
            return bf, be
        best_f, best_e = est, 0.0
        for cand in {est, est / 2, est / 3, est / 4}:
            if cand < 20:
                continue
            f_c, e_c = refine(cand)
            if e_c > best_e:
                best_f, best_e = f_c, e_c
        if abs(best_f - freq) > tol:
            raise AudioExpectError(
                f"dominant_freq: expect {freq}Hz±{tol}, got {best_f:.1f}Hz "
                f"(zcr est {est:.1f})")
        return self

    def no_clipping(self, peak: float = 0.99) -> "AudioExpect":
        mx = audioop.max(self.pcm, 2) / 32768.0
        if mx >= peak:
            raise AudioExpectError(f"clipping: peak {mx:.4f} >= {peak}")
        return self

    def lufs(self, target: float, tol: float = 1.5) -> "AudioExpect":
        """K 加权响度断言 (BS.1770 简化实现: K 加权 biquad 两级 + 绝对门控,
        不含相对门控积分；用于近似断言，不是完整的 BS.1770 一致性测量)。"""
        measured = measure_lufs(self.pcm, self.sr)
        if abs(measured - target) > tol:
            raise AudioExpectError(
                f"lufs: expect {target}±{tol}, got {measured:.2f}")
        return self


def _biquad_coeffs(kind: str, sr: int):
    """ITU-R BS.1770 K 加权滤波器系数 (按采样率换算, DeMan 公式)。"""
    if kind == "shelf":  # stage 1: high shelf
        G, Q = 3.99984385397, 0.7071752369554193
        fc = 1681.974450955533
    else:  # stage 2: high pass (RLB)
        G, Q = -0.691, 0.5003270373253953
        fc = 38.13547087602444
    K = math.tan(math.pi * fc / sr)
    Vh = 10 ** (G / 20)
    Vb = Vh ** 0.499666774155
    if kind == "shelf":
        a0 = 1 + K / Q + K * K
        b0 = (Vh + Vb * K / Q + K * K) / a0
        b1 = 2 * (K * K - Vh) / a0
        b2 = (Vh - Vb * K / Q + K * K) / a0
        a1 = 2 * (K * K - 1) / a0
        a2 = (1 - K / Q + K * K) / a0
    else:
        a0 = 1 + K / Q + K * K
        b0 = 1 / a0
        b1 = -2 / a0
        b2 = 1 / a0
        a1 = 2 * (K * K - 1) / a0
        a2 = (1 - K / Q + K * K) / a0
    return b0, b1, b2, a1, a2


def _apply_biquad(samples: list[float], c) -> list[float]:
    b0, b1, b2, a1, a2 = c
    out = []
    x1 = x2 = y1 = y2 = 0.0
    for x in samples:
        y = b0 * x + b1 * x1 + b2 * x2 - a1 * y1 - a2 * y2
        x2, x1 = x1, x
        y2, y1 = y1, y
        out.append(y)
    return out


def measure_lufs(pcm: bytes, sr: int) -> float:
    """K 加权 + 绝对门控 (-70 LUFS) 的积分响度估计。"""
    n = len(pcm) // 2
    if n == 0:
        return -150.0
    # 下采样限幅防慢 (长文件截断到 30s)
    max_samples = sr * 30
    if n > max_samples:
        pcm = pcm[: max_samples * 2]
        n = max_samples
    samples = [int.from_bytes(pcm[2 * i:2 * i + 2], "little", signed=True) / 32768.0
               for i in range(n)]
    samples = _apply_biquad(samples, _biquad_coeffs("shelf", sr))
    samples = _apply_biquad(samples, _biquad_coeffs("hp", sr))
    # 400ms 块 (75% overlap 省略, 直接不重叠) 门控
    block = int(sr * 0.4)
    energies = []
    for i in range(0, n - block + 1, block):
        e = sum(v * v for v in samples[i:i + block]) / block
        loud = -0.691 + 10 * math.log10(max(e, 1e-12))
        if loud > -70:
            energies.append(e)
    if not energies:
        return -150.0
    mean_e = sum(energies) / len(energies)
    return -0.691 + 10 * math.log10(max(mean_e, 1e-12))


def expect_audio(path: str | Path) -> AudioExpect:
    return AudioExpect(path)
