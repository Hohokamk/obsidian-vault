# -*- coding: utf-8 -*-
"""
伏安特性曲线作图  小灯泡 / 二极管正向 / 二极管反向
数据来自实验原始记录；曲线用单调三次 Hermite (PCHIP) 平滑，逐点通过测量值。
样式按实验报告规范：白底、黑线、坐标纸式网格、完整刻度，黑白打印可用。
改数据后直接重跑本脚本即可刷新全部图片。
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.ticker import MultipleLocator

OUT = os.path.dirname(os.path.abspath(__file__))

# ---------- 中文字体 ----------
FONT_PATH = r"C:\Windows\Fonts\simhei.ttf"
fm.fontManager.addfont(FONT_PATH)
plt.rcParams["font.family"] = fm.FontProperties(fname=FONT_PATH).get_name()
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["mathtext.fontset"] = "dejavusans"

# ---------- 原始数据 ----------
# ① 小灯泡伏安特性
U_LAMP = np.array([0.00, 0.25, 0.50, 1.00, 1.50, 2.00, 2.50, 3.00])
I_LAMP = np.array([0, 95, 115, 160, 205, 235, 265, 300], dtype=float)  # mA

# ② 二极管正向伏安特性（原始表为「定电流 I，测电压 U」；作图仍按 U 横轴 / I 纵轴）
I_FWD = np.array([0.00, 0.30, 0.50, 1.00, 2.00, 5.00, 8.00, 11.00, 15.00])  # mA
U_FWD = np.array([-0.0139, 0.1112, 0.1575, 0.2084, 0.2984,
                  0.4738, 0.6144, 0.7321, 0.8699])  # V

# ③ 二极管反向伏安特性（单位按手写补注修正为 μA）
U_REV = np.array([0.00, 1.00, 2.00, 3.00, 5.00, 7.00, 9.00, 11.00, 13.00, 15.00])
I_REV = np.array([-0.54, 36.22, 61.82, 87.66, 113.35,
                  135.23, 155.41, 174.28, 194.82, 216.82])  # μA

NOTE = ("电压表  0～7.5 V / 0.5 级 / $R_V$ = 1.50 kΩ      "
        "电流表  0～750 mA / 0.5 级 / $R_A$ = 0.06 Ω")
NOTE2 = "注：图 2 电流为 mA、图 3 为 μA，两图坐标标尺不同，斜率不可直接比较。"


def pchip(x, y, xx):
    """单调分段三次 Hermite 插值 (Fritsch-Carlson)，曲线不产生虚假过冲。"""
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    h = np.diff(x)
    delta = np.diff(y) / h
    n = len(x)
    d = np.zeros(n)

    # 内部节点斜率：加权调和平均，保证单调性
    for k in range(1, n - 1):
        if delta[k - 1] * delta[k] <= 0:
            d[k] = 0.0
        else:
            w1 = 2 * h[k] + h[k - 1]
            w2 = h[k] + 2 * h[k - 1]
            d[k] = (w1 + w2) / (w1 / delta[k - 1] + w2 / delta[k])

    # 端点单侧三点公式 + 单调性限幅
    def endpoint(h0, h1, del0, del1):
        val = ((2 * h0 + h1) * del0 - h0 * del1) / (h0 + h1)
        if val * del0 <= 0:
            return 0.0
        if del0 * del1 < 0 and abs(val) > 3 * abs(del0):
            return 3 * del0
        return val

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
        out[m] = ((2 * t**3 - 3 * t**2 + 1) * y[i]
                  + (t**3 - 2 * t**2 + t) * h[i] * d[i]
                  + (-2 * t**3 + 3 * t**2) * y[i + 1]
                  + (t**3 - t**2) * h[i] * d[i + 1])
    return out


def draw(ax, x, y, title, ylabel, xlim, ylim, xmaj, ymaj, xmin, ymin,
         compact=False, legend_loc="lower right"):
    fs_label = 10.5 if compact else 12
    fs_title = 12 if compact else 13.5
    fs_tick = 9 if compact else 10
    fs_leg = 8.5 if compact else 9.5

    # 平滑曲线 + 原始数据点
    xs = np.linspace(x[0], x[-1], 500)
    ax.plot(xs, pchip(x, y, xs), color="black", lw=1.7, zorder=3,
            solid_capstyle="round", label="平滑特性曲线")
    ax.plot(x, y, linestyle="none", marker="o", ms=6.5,
            mfc="black", mec="white", mew=0.9, zorder=4, label="测量数据点")

    # 坐标范围与刻度
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.xaxis.set_major_locator(MultipleLocator(xmaj))
    ax.yaxis.set_major_locator(MultipleLocator(ymaj))
    ax.xaxis.set_minor_locator(MultipleLocator(xmin))
    ax.yaxis.set_minor_locator(MultipleLocator(ymin))

    # 零线
    ax.axhline(0, color="black", lw=1.0, zorder=1)
    ax.axvline(0, color="black", lw=1.0, zorder=1)

    # 网格：主刻度浅灰实线，次刻度更浅虚线
    ax.grid(which="major", color="#c4c4c4", lw=0.8, linestyle="-", zorder=0)
    ax.grid(which="minor", color="#e4e4e4", lw=0.5, linestyle=":", zorder=0)

    # 四边框 + 双向刻度
    for spine in ax.spines.values():
        spine.set_color("black")
        spine.set_linewidth(1.15)
        spine.set_zorder(5)
    ax.tick_params(which="major", direction="inout", length=6, width=1.0,
                   labelsize=fs_tick, top=True, right=True)
    ax.tick_params(which="minor", direction="in", length=3, width=0.7,
                   top=True, right=True)

    ax.set_xlabel("电压  $U$ / V", fontsize=fs_label, labelpad=8)
    ax.set_ylabel(ylabel, fontsize=fs_label, labelpad=8)
    ax.set_title(title, fontsize=fs_title, loc="left", pad=12)
    ax.legend(loc=legend_loc, frameon=True, framealpha=1.0,
              edgecolor="black", fontsize=fs_leg, handlelength=2.2)


CFG_LAMP = dict(title="图 1  小灯泡伏安特性曲线", ylabel="电流  $I$ / mA",
                xlim=(0, 3.2), ylim=(0, 320), xmaj=0.5, ymaj=50,
                xmin=0.25, ymin=10)
CFG_FWD = dict(title="图 2  二极管正向伏安特性曲线", ylabel="电流  $I$ / mA",
               xlim=(-0.05, 0.95), ylim=(0, 16), xmaj=0.1, ymaj=2,
               xmin=0.05, ymin=1)
CFG_REV = dict(title="图 3  二极管反向伏安特性曲线", ylabel="电流  $I$ / μA",
               xlim=(0, 15.5), ylim=(-15, 240), xmaj=1, ymaj=20,
               xmin=0.5, ymin=10)


def save_single(cfg, x, y, filename):
    fig, ax = plt.subplots(figsize=(8.4, 5.9), dpi=300, facecolor="white")
    draw(ax, x, y, **cfg)
    fig.text(0.5, 0.025, NOTE, ha="center", fontsize=8.5, color="#444444")
    fig.subplots_adjust(left=0.115, right=0.965, top=0.90, bottom=0.155)
    path = os.path.join(OUT, filename)
    fig.savefig(path, dpi=300, facecolor="white")
    plt.close(fig)
    print("saved:", filename)


def save_combined():
    fig = plt.figure(figsize=(11.7, 8.8), dpi=300, facecolor="white")
    gs = fig.add_gridspec(2, 2, height_ratios=[1.0, 1.18],
                          hspace=0.46, wspace=0.30,
                          left=0.075, right=0.965, top=0.935, bottom=0.13)
    ax1 = fig.add_subplot(gs[0, :])
    ax2 = fig.add_subplot(gs[1, 0])
    ax3 = fig.add_subplot(gs[1, 1])
    draw(ax1, U_LAMP, I_LAMP, compact=True, **CFG_LAMP)
    draw(ax2, U_FWD, I_FWD, compact=True, **CFG_FWD)
    draw(ax3, U_REV, I_REV, compact=True, **CFG_REV)
    fig.text(0.5, 0.055, NOTE, ha="center", fontsize=9, color="#444444")
    fig.text(0.5, 0.022, NOTE2, ha="center", fontsize=8.5, color="#666666")
    path = os.path.join(OUT, "伏安特性曲线_总图.png")
    fig.savefig(path, dpi=300, facecolor="white")
    plt.close(fig)
    print("saved: 伏安特性曲线_总图.png")


if __name__ == "__main__":
    save_single(CFG_LAMP, U_LAMP, I_LAMP, "小灯泡伏安特性曲线.png")
    save_single(CFG_FWD, U_FWD, I_FWD, "二极管正向伏安特性曲线.png")
    save_single(CFG_REV, U_REV, I_REV, "二极管反向伏安特性曲线.png")
    save_combined()
