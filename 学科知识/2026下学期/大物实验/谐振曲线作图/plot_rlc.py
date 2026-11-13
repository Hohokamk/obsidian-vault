# -*- coding: utf-8 -*-
"""
RLC 串联谐振曲线作图（实验十九）
数据表「1.2 f 谐振曲线数据表」共 23 组，两条曲线在同一坐标系对比。
注意：源图底部带「部分内容由 豆包工作 AI 生成」水印，本图仅作练习 / 格式参考，
      正式报告须使用经指导教师签字的原始记录数据。

输出：I-f 主图、U_R0-f 图、带宽分析图（半功率点 f1/f2/Δf/Q）、总图。
样式沿用实验报告规范：白底纯黑白、平滑曲线 + 原始数据点、坐标纸式刻度网格。
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.ticker import MultipleLocator, FormatStrFormatter

OUT = os.path.dirname(os.path.abspath(__file__))

# ---------- 中文字体 ----------
FONT_PATH = r"C:\Windows\Fonts\simhei.ttf"
fm.fontManager.addfont(FONT_PATH)
plt.rcParams["font.family"] = fm.FontProperties(fname=FONT_PATH).get_name()
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["mathtext.fontset"] = "dejavusans"

# ---------- 实验参数 ----------
L, C = 0.100, 0.0500e-6      # H, F
R_L, U_SRC = 20.0, 0.900     # Ω, V
R0, R0P = 100.0, 220.0       # Ω
R, RP = R0 + R_L, R0P + R_L  # 120 Ω, 240 Ω
F0_THEORY = 1 / (2 * np.pi * np.sqrt(L * C)) / 1000  # kHz

# ---------- 原始数据（逐行抄自数据表） ----------
F = np.array([
    1.40, 1.50, 1.60, 1.70, 1.80, 1.90, 2.00, 2.05, 2.10, 2.15, 2.20, 2.25,
    2.30, 2.35, 2.40, 2.45, 2.50, 2.60, 2.70, 2.80, 2.90, 3.00, 3.10])
URO = np.array([
    64.0, 74.0, 89.0, 111.0, 139.0, 181.0, 252.0, 308.0, 396.0, 505.0, 641.0,
    718.0, 621.0, 508.0, 402.0, 331.0, 278.0, 215.0, 169.0, 142.0, 121.0, 109.0,
    94.0])                                                    # mV, R0 = 100 Ω
I1 = np.array([
    0.640, 0.740, 0.890, 1.110, 1.390, 1.810, 2.520, 3.080, 3.960, 5.050, 6.410,
    7.180, 6.210, 5.080, 4.020, 3.310, 2.780, 2.150, 1.690, 1.420, 1.210, 1.090,
    0.940])                                                   # mA = URO/R0
UROP = np.array([
    129, 151, 162, 218, 272, 342, 457, 512, 608, 696, 764, 792, 764, 696, 618,
    546, 492, 395, 314, 271, 239, 213, 192], dtype=float)      # mV, R0' = 220 Ω
I2 = np.array([
    0.586, 0.686, 0.736, 0.991, 1.236, 1.555, 2.077, 2.327, 2.764, 3.164, 3.473,
    3.600, 3.473, 3.164, 2.809, 2.482, 2.236, 1.795, 1.427, 1.232, 1.086, 0.968,
    0.873])                                                   # mA = URO'/R0'

# 数据自洽自检：I 列必须等于 U_R / R
assert np.allclose(I1, URO / R0, atol=5.1e-4), "第一组 I 列与 U_R0/R0 不符"
assert np.allclose(I2, UROP / R0P, atol=5.1e-4), "第二组 I' 列与 U_R0'/R0' 不符"

NOTE1 = (r"$L=0.100\ \mathrm{H}\qquad C=0.0500\ \mu\mathrm{F}\qquad"
         r"r_L=20\ \Omega\qquad U=0.900\ \mathrm{V}$")
NOTE2 = (r"$R_0=100.0\ \Omega\ (R=120\ \Omega)\qquad"
         r"R_0^\prime=220.0\ \Omega\ (R^\prime=240\ \Omega)$"
         + "　　理论 " + r"$f_0=%.3f\ \mathrm{kHz}$" % F0_THEORY)

LBL1 = r"$R_0=100.0\ \Omega$（回路 $R=120\ \Omega$）"
LBL2 = r"$R_0^\prime=220.0\ \Omega$（回路 $R^\prime=240\ \Omega$）"


def pchip(x, y, xx):
    """单调分段三次 Hermite (Fritsch-Carlson)：保形、不产生虚假过冲。"""
    x = np.asarray(x, float); y = np.asarray(y, float)
    h = np.diff(x); delta = np.diff(y) / h; n = len(x)
    d = np.zeros(n)
    for k in range(1, n - 1):
        if delta[k - 1] * delta[k] <= 0:
            d[k] = 0.0
        else:
            w1, w2 = 2 * h[k] + h[k - 1], h[k] + 2 * h[k - 1]
            d[k] = (w1 + w2) / (w1 / delta[k - 1] + w2 / delta[k])

    def endpoint(h0, h1, dl0, dl1):
        v = ((2 * h0 + h1) * dl0 - h0 * dl1) / (h0 + h1)
        if v * dl0 <= 0:
            return 0.0
        if dl0 * dl1 < 0 and abs(v) > 3 * abs(dl0):
            return 3 * dl0
        return v

    d[0] = endpoint(h[0], h[1], delta[0], delta[1])
    d[-1] = endpoint(h[-1], h[-2], delta[-1], delta[-2])
    xx = np.asarray(xx, float)
    out = np.empty_like(xx)
    idx = np.clip(np.searchsorted(x, xx, side="right") - 1, 0, n - 2)
    for i in range(n - 1):
        m = idx == i
        if not np.any(m):
            continue
        t = (xx[m] - x[i]) / h[i]
        out[m] = ((2*t**3 - 3*t**2 + 1) * y[i]
                  + (t**3 - 2*t**2 + t) * h[i] * d[i]
                  + (-2*t**3 + 3*t**2) * y[i + 1]
                  + (t**3 - t**2) * h[i] * d[i + 1])
    return out


def style_axes(ax, ylim, ylabel, ymaj, ymin, xmaj=0.1, compact=False):
    ax.set_xlim(1.35, 3.15)
    ax.set_ylim(*ylim)
    ax.xaxis.set_major_locator(MultipleLocator(xmaj))
    ax.xaxis.set_minor_locator(MultipleLocator(0.05))
    ax.yaxis.set_major_locator(MultipleLocator(ymaj))
    ax.yaxis.set_minor_locator(MultipleLocator(ymin))
    ax.xaxis.set_major_formatter(FormatStrFormatter("%.1f"))
    ax.yaxis.set_major_formatter(FormatStrFormatter("%.0f"))
    ax.grid(which="major", color="#c4c4c4", lw=0.8, linestyle="-", zorder=0)
    ax.grid(which="minor", color="#e6e6e6", lw=0.5, linestyle=":", zorder=0)
    for sp in ax.spines.values():
        sp.set_color("black"); sp.set_linewidth(1.15); sp.set_zorder(5)
    fs_tick = 9 if compact else 10
    fs_lab = 10.5 if compact else 12
    ax.tick_params(which="major", direction="inout", length=6, width=1.0,
                   labelsize=fs_tick, top=True, right=True)
    ax.tick_params(which="minor", direction="in", length=3, width=0.7,
                   top=True, right=True)
    ax.set_xlabel(r"频率  $f$ / kHz", fontsize=fs_lab, labelpad=8)
    ax.set_ylabel(ylabel, fontsize=fs_lab, labelpad=8)


def series(ax, y, dashed=False, label=None):
    """一条谐振曲线：平滑线 + 原始数据点。黑白下用线型/点型区分。"""
    xs = np.linspace(F[0], F[-1], 800)
    ls = (0, (6, 3)) if dashed else "-"
    mk, mfc = ("s", "white") if dashed else ("o", "black")
    ax.plot(xs, pchip(F, y, xs), color="black", lw=1.7, ls=ls, zorder=3, label=label)
    ax.plot(F, y, linestyle="none", marker=mk, ms=6.2, mfc=mfc, mec="black",
            mew=1.0, zorder=4, label="_nolegend_")


def notes(fig, y1=0.048, y2=0.020, size=8.6):
    fig.text(0.5, y1, NOTE1, ha="center", fontsize=size, color="#444444")
    fig.text(0.5, y2, NOTE2, ha="center", fontsize=size, color="#444444")


def half_power(y):
    """由平滑曲线读半功率点，返回 Im, 0.707Im, f1, f2, Δf, f0(测), Q(测)。"""
    im = float(y.max()); lv = im / np.sqrt(2)
    xs = np.linspace(F[0], F[-1], 12000)
    s = pchip(F, y, xs) - lv
    idx = np.where(s[:-1] * s[1:] < 0)[0]
    roots = [xs[i] + (xs[i+1] - xs[i]) * (-s[i]) / (s[i+1] - s[i]) for i in idx]
    f1, f2 = roots[0], roots[-1]
    df = f2 - f1
    f0m = np.sqrt(f1 * f2)
    return im, lv, f1, f2, df, f0m, f0m / df


def save_main():
    fig, ax = plt.subplots(figsize=(8.6, 5.9), dpi=300, facecolor="white")
    style_axes(ax, (0, 8.0), r"电流  $I$ / mA", 1, 0.5)
    series(ax, I1, label=LBL1)
    series(ax, I2, dashed=True, label=LBL2)
    ax.set_title("RLC 串联谐振曲线（I - f，两组回路电阻对比）",
                 fontsize=13.5, loc="left", pad=12)
    ax.legend(loc="upper right", frameon=True, framealpha=1.0,
              edgecolor="black", fontsize=10, handlelength=2.6)
    notes(fig)
    fig.subplots_adjust(left=0.105, right=0.965, top=0.90, bottom=0.165)
    fig.savefig(os.path.join(OUT, "RLC谐振曲线_I-f.png"), dpi=300, facecolor="white")
    plt.close(fig); print("saved: RLC谐振曲线_I-f.png")


def save_voltage():
    fig, ax = plt.subplots(figsize=(8.6, 5.9), dpi=300, facecolor="white")
    style_axes(ax, (0, 850), r"电阻电压  $U_{R_0}$ / mV", 100, 50)
    series(ax, URO, label=LBL1)
    series(ax, UROP, dashed=True, label=LBL2)
    ax.set_title("电阻电压随频率变化曲线（原始读数）",
                 fontsize=13.5, loc="left", pad=12)
    ax.legend(loc="upper right", frameon=True, framealpha=1.0,
              edgecolor="black", fontsize=10, handlelength=2.6)
    notes(fig)
    fig.subplots_adjust(left=0.115, right=0.965, top=0.90, bottom=0.165)
    fig.savefig(os.path.join(OUT, "RLC谐振曲线_URo-f.png"), dpi=300, facecolor="white")
    plt.close(fig); print("saved: RLC谐振曲线_URo-f.png")


def draw_half_power(ax, y, title):
    """单组曲线：I_m、0.707 I_m 及其对应频率 f0、f1、f2 的全部辅助线。"""
    im, lv, f1, f2, df, f0m, q = half_power(y)
    fpk = float(F[np.argmax(y)])
    style_axes(ax, (0, 8.0 if im > 5 else 4.2), r"电流  $I$ / mA",
               1, 0.5, xmaj=0.2, compact=True)
    series(ax, y)
    ymax = ax.get_ylim()[1]
    AUX = dict(color="#777777", lw=0.9, ls=(0, (3, 3)), zorder=2)

    # ① 电流最大值 I_m：水平辅助线（至峰值频率）+ 峰值频率 f0 竖直辅助线
    ax.hlines(im, 1.35, fpk, **AUX)
    ax.vlines(fpk, 0, im, color="#555555", lw=1.0, ls=(0, (6, 3)), zorder=2)
    ax.plot(fpk, im, marker="o", ms=11, mfc="none", mec="black", mew=1.0, zorder=5)
    ax.text(1.37, im + 0.025 * ymax, r"$I_m=%.3f\ \mathrm{mA}$" % im,
            ha="left", va="bottom", fontsize=8.8)
    ax.text(fpk, im + 0.025 * ymax, r"$f_0=%.3f\ \mathrm{kHz}$" % fpk,
            ha="center", va="bottom", fontsize=8.8)

    # ② 0.707 I_m：水平辅助线 + 边界频率 f1、f2 竖直辅助线 + 交点
    ax.axhline(lv, **AUX)
    ax.text(1.37, lv + 0.018 * ymax, r"$0.707I_m=%.3f\ \mathrm{mA}$" % lv,
            ha="left", va="bottom", fontsize=8.8)
    ax.vlines([f1, f2], 0, lv, **AUX)
    ax.plot([f1, f2], [lv, lv], linestyle="none", marker="o", ms=8,
            mfc="white", mec="black", mew=1.3, zorder=5)
    for fv, tag in ((f1, r"$f_1$"), (f2, r"$f_2$")):
        ax.text(fv, 0.028 * ymax, tag + "\n" + "%.3f" % fv,
                ha="center", va="bottom", fontsize=8, linespacing=1.25)

    # 带宽双箭头
    yarr = 0.15 * ymax
    ax.annotate("", xy=(f2, yarr), xytext=(f1, yarr),
                arrowprops=dict(arrowstyle="<->", lw=1.0, color="black",
                                shrinkA=0, shrinkB=0))
    ax.text((f1 + f2) / 2, yarr + 0.03 * ymax,
            r"$\Delta f=%.3f\ \mathrm{kHz}$" % df,
            ha="center", va="bottom", fontsize=9)
    # 结果框
    txt = (r"$I_m=%.3f\ \mathrm{mA}$" % im + "\n"
           + r"$0.707I_m=%.3f\ \mathrm{mA}$" % lv + "\n"
           + r"$f_1=%.3f,\ f_2=%.3f\ \mathrm{kHz}$" % (f1, f2) + "\n"
           + r"$\Delta f=%.3f\ \mathrm{kHz}$" % df + "\n"
           + r"$\sqrt{f_1f_2}=%.3f\ \mathrm{kHz}$" % f0m + "\n"
           + r"$Q=\sqrt{f_1f_2}/\Delta f=%.2f$" % q)
    ax.text(0.975, 0.985, txt, transform=ax.transAxes, ha="right", va="top",
            fontsize=8.6, linespacing=1.25,
            bbox=dict(boxstyle="square,pad=0.45", fc="white", ec="black", lw=0.8))
    ax.set_title(title, fontsize=11.5, loc="left", pad=10)
    return im, lv, f1, f2, df, f0m, q


def save_half_power():
    fig, axes = plt.subplots(1, 2, figsize=(11.8, 5.4), dpi=300, facecolor="white")
    a = draw_half_power(axes[0], I1, "第一组  " + LBL1)
    b = draw_half_power(axes[1], I2, "第二组  " + LBL2)
    fig.text(0.5, 0.018, NOTE1 + "　　" + NOTE2, ha="center", fontsize=8.2,
             color="#444444")
    fig.subplots_adjust(left=0.075, right=0.975, top=0.89, bottom=0.16, wspace=0.24)
    fig.savefig(os.path.join(OUT, "RLC谐振曲线_带宽分析.png"), dpi=300, facecolor="white")
    plt.close(fig)
    print("saved: RLC谐振曲线_带宽分析.png")
    for name, v in (("R=120 Ω", a), ("R'=240 Ω", b)):
        print("  %s: Im=%.3f mA, 0.707Im=%.3f, f1=%.4f, f2=%.4f, "
              "dF=%.4f kHz, f0=%.4f kHz, Q=%.3f" % ((name,) + v))


def save_aux_combined():
    """两组电阻叠在同一坐标系：I_m、0.707I_m 及其频率 f0、f1、f2 辅助线一次画全。"""
    fig, ax = plt.subplots(figsize=(9.2, 6.8), dpi=300, facecolor="white")
    style_axes(ax, (0, 8.0), r"电流  $I$ / mA", 1, 0.5)
    series(ax, I1, label=LBL1)
    series(ax, I2, dashed=True, label=LBL2)
    AUX = dict(color="#777777", lw=0.9, ls=(0, (3, 3)), zorder=2)

    res = []
    for y in (I1, I2):
        im, lv, f1_, f2_, df_, f0m_, q_ = half_power(y)
        fpk = float(F[np.argmax(y)])
        res.append((im, lv, f1_, f2_, df_, fpk, q_))
        ax.hlines(im, 1.35, fpk, **AUX)                  # I_m 水平辅助线
        ax.hlines(lv, 1.35, f2_, **AUX)                  # 0.707 I_m 水平辅助线
        ax.vlines([f1_, f2_], 0, lv, **AUX)              # f1、f2 竖直辅助线
        ax.plot([f1_, f2_], [lv, lv], linestyle="none", marker="o", ms=7,
                mfc="white", mec="black", mew=1.2, zorder=5)
        ax.plot(fpk, im, marker="o", ms=11, mfc="none", mec="black", mew=1.0, zorder=5)

    # 两组峰值同频，共用一条 f0 竖线
    fpk0 = float(F[np.argmax(I1)])
    ax.vlines(fpk0, 0, I1.max(), color="#555555", lw=1.0, ls=(0, (6, 3)), zorder=2)
    ax.text(fpk0, 7.48, r"$f_0=%.3f$" % fpk0,
            ha="center", va="bottom", fontsize=9)

    # 左侧标注四个电流水平（对应两组）
    for k, (im, lv, *_rest) in enumerate(res, start=1):
        ax.text(1.36, im + 0.10, r"$I_{m%d}=%.3f$" % (k, im),
                ha="left", va="bottom", fontsize=8.2)
        ax.text(1.36, lv + 0.10, r"$0.707I_{m%d}=%.3f$" % (k, lv),
                ha="left", va="bottom", fontsize=8.2)

    ax.set_title("RLC 串联谐振曲线：两组电阻的 $I_m$ 与 $0.707I_m$ 辅助线",
                 fontsize=12.5, loc="left", pad=12)
    ax.legend(loc="upper right", framealpha=1.0, edgecolor="black",
              fontsize=9.2, handlelength=2.6)

    rows = []
    for name, v in ((r"第一组  $R=120\ \Omega$", res[0]),
                    (r"第二组  $R^\prime=240\ \Omega$", res[1])):
        im, lv, f1_, f2_, df_, fpk_, _q = v
        rows.append(
            name + r"：$I_m=%.3f$，$0.707I_m=%.3f\ \mathrm{mA}$；"
                   r"$f_1=%.3f$，$f_0=%.3f$，$f_2=%.3f\ \mathrm{kHz}$，$\Delta f=%.3f\ \mathrm{kHz}$"
            % (im, lv, f1_, fpk_, f2_, df_))
    fig.text(0.5, 0.100, rows[0], ha="center", fontsize=8.6, color="#333333")
    fig.text(0.5, 0.074, rows[1], ha="center", fontsize=8.6, color="#333333")
    fig.text(0.5, 0.048,
             r"细灰虚线：$I_m$、$0.707I_m$ 水平线及 $f_1$、$f_2$ 竖线"
             r"　　深灰长虚线：峰值频率 $f_0$ 竖线",
             ha="center", fontsize=8.2, color="#555555")
    fig.text(0.5, 0.021, NOTE1 + "　" + NOTE2, ha="center", fontsize=7.8,
             color="#666666")
    fig.subplots_adjust(left=0.10, right=0.965, top=0.90, bottom=0.215)
    fig.savefig(os.path.join(OUT, "RLC谐振曲线_辅助线总图.png"), dpi=300,
                facecolor="white")
    plt.close(fig)
    print("saved: RLC谐振曲线_辅助线总图.png")


def save_combined():
    fig, axes = plt.subplots(2, 1, figsize=(8.6, 10.6), dpi=300, facecolor="white")
    style_axes(axes[0], (0, 8.0), r"电流  $I$ / mA", 1, 0.5, compact=True)
    series(axes[0], I1, label=LBL1); series(axes[0], I2, dashed=True, label=LBL2)
    axes[0].set_title("图 1  RLC 串联谐振曲线（I - f）", fontsize=12, loc="left", pad=10)
    axes[0].legend(loc="upper right", framealpha=1.0, edgecolor="black",
                   fontsize=9.2, handlelength=2.4)
    style_axes(axes[1], (0, 850), r"电阻电压  $U_{R_0}$ / mV", 100, 50, compact=True)
    series(axes[1], URO, label=LBL1); series(axes[1], UROP, dashed=True, label=LBL2)
    axes[1].set_title("图 2  电阻电压随频率变化曲线", fontsize=12, loc="left", pad=10)
    axes[1].legend(loc="upper right", framealpha=1.0, edgecolor="black",
                   fontsize=9.2, handlelength=2.4)
    notes(fig, y1=0.042, y2=0.018, size=8.4)
    fig.subplots_adjust(left=0.115, right=0.965, top=0.945, bottom=0.115, hspace=0.36)
    fig.savefig(os.path.join(OUT, "RLC谐振曲线_总图.png"), dpi=300, facecolor="white")
    plt.close(fig); print("saved: RLC谐振曲线_总图.png")


if __name__ == "__main__":
    print("理论 f0 = %.4f kHz, dF(R) = %.4f kHz, dF(R') = %.4f kHz, "
          "Q(R) = %.3f, Q(R') = %.3f" %
          (F0_THEORY, R/(2*np.pi*L)/1000, RP/(2*np.pi*L)/1000,
           F0_THEORY/(R/(2*np.pi*L)/1000), F0_THEORY/(RP/(2*np.pi*L)/1000)))
    save_main()
    save_voltage()
    save_half_power()
    save_aux_combined()
    save_combined()
