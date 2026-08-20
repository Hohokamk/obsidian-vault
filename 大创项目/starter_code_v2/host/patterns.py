"""
patterns.py - 图案生成模块
功能：根据配置文件，生成各种 LED 阵列图案（0/1 矩阵）
"""

import yaml
import numpy as np
import os

# 配置文件路径（自动定位）
CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'config', 'array_config.yaml')


def load_config(path=None):
    """读取 YAML 配置文件，返回字典"""
    if path is None:
        path = CONFIG_PATH
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def get_array_size(config):
    """从配置中获取阵列行数、列数"""
    rows = config['array']['rows']
    cols = config['array']['cols']
    return rows, cols


# ========== 下面是各种图案生成函数 ==========

def pattern_all_off(config):
    """全灭图案：所有 LED 关闭"""
    rows, cols = get_array_size(config)
    return np.zeros((rows, cols), dtype=np.uint8)


def pattern_all_on(config):
    """全亮图案：所有 LED 打开"""
    rows, cols = get_array_size(config)
    return np.ones((rows, cols), dtype=np.uint8)


def pattern_checker(config):
    """棋盘格图案：0和1交替"""
    rows, cols = get_array_size(config)
    pattern = np.zeros((rows, cols), dtype=np.uint8)
    for r in range(rows):
        for c in range(cols):
            if (r + c) % 2 == 0:
                pattern[r, c] = 1
    return pattern


def pattern_one(config, row, col):
    """单点图案：只点亮指定坐标的 LED"""
    rows, cols = get_array_size(config)
    pattern = np.zeros((rows, cols), dtype=np.uint8)
    pattern[row, col] = 1
    return pattern


def pattern_random(config, seed=42, density=0.3):
    """随机图案：按概率随机点亮"""
    rows, cols = get_array_size(config)
    rng = np.random.RandomState(seed)  # 固定种子，保证可复现
    pattern = (rng.random((rows, cols)) < density).astype(np.uint8)
    return pattern


def pattern_rows(config, target_row):
    """整行点亮"""
    rows, cols = get_array_size(config)
    pattern = np.zeros((rows, cols), dtype=np.uint8)
    pattern[target_row, :] = 1
    return pattern


def pattern_cols(config, target_col):
    """整列点亮"""
    rows, cols = get_array_size(config)
    pattern = np.zeros((rows, cols), dtype=np.uint8)
    pattern[:, target_col] = 1
    return pattern


# ========== 可视化：在终端里"画"出图案 ==========

def print_pattern(pattern, title=""):
    """在终端用字符画显示图案"""
    if title:
        print(f"\n{'='*40}")
        print(f"  {title}")
        print(f"{'='*40}")

    rows, cols = pattern.shape

    # 打印列号
    print("     ", end="")
    for c in range(cols):
        print(f"{c:2d}", end="")
    print()
    print("     " + "--" * cols)

    # 打印每一行
    for r in range(rows):
        print(f"  {r:2d} | ", end="")
        for c in range(cols):
            if pattern[r, c] == 1:
                print("██", end="")  # 亮
            else:
                print("  ", end="")  # 灭
        print(f" | {r:2d}")

    print("     " + "--" * cols)
    print(f"  共 {rows}x{cols} = {rows*cols} 通道, "
          f"点亮 {pattern.sum()} 个, "
          f"占比 {pattern.sum()/(rows*cols)*100:.1f}%")


if __name__ == "__main__":
    # 直接运行这个文件时，演示所有图案
    config = load_config()

    print_pattern(pattern_all_off(config), "全灭 ALL OFF")
    print_pattern(pattern_all_on(config), "全亮 ALL ON")
    print_pattern(pattern_checker(config), "棋盘格 CHECKER")
    print_pattern(pattern_one(config, 3, 5), "单点 ONE (row=3, col=5)")
    print_pattern(pattern_random(config, seed=2026, density=0.3), "随机 RANDOM (seed=2026)")
    print_pattern(pattern_rows(config, 7), "第7行整行亮")
    print_pattern(pattern_cols(config, 10), "第10列整列亮")
