"""
arrayctl.py - 阵列控制命令行工具（v2：集成协议）
用法:
  python arrayctl.py off              全灭
  python arrayctl.py on               全亮
  python arrayctl.py checker          棋盘格
  python arrayctl.py one <row> <col>  点亮单点
  python arrayctl.py random           随机图案
  python arrayctl.py row <n>          整行亮
  python arrayctl.py col <n>          整列亮

  加 --dry-run 只显示协议帧，不发送（调试用）
  加 --port COM5 指定串口（联调时用）
"""

import sys
import os
import argparse

sys.path.insert(0, os.path.dirname(__file__))
import patterns
import protocol


def main():
    parser = argparse.ArgumentParser(description='大规模阵列控制工具 v2')
    sub = parser.add_subparsers(dest='command', help='可用命令')

    sub.add_parser('off', help='全灭')
    sub.add_parser('on', help='全亮')
    sub.add_parser('checker', help='棋盘格')

    p_one = sub.add_parser('one', help='点亮单个LED')
    p_one.add_argument('row', type=int)
    p_one.add_argument('col', type=int)

    p_rand = sub.add_parser('random', help='随机图案')
    p_rand.add_argument('--seed', type=int, default=42)
    p_rand.add_argument('--density', type=float, default=0.3)

    p_row = sub.add_parser('row', help='整行点亮')
    p_row.add_argument('n', type=int)

    p_col = sub.add_parser('col', help='整列点亮')
    p_col.add_argument('n', type=int)

    # 全局参数
    parser.add_argument('--dry-run', action='store_true', help='只显示帧，不发送')
    parser.add_argument('--port', type=str, default=None, help='串口名 (如 COM5)')
    parser.add_argument('--seq', type=int, default=0, help='序列号')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    config = patterns.load_config()

    # 生成图案
    cmd = args.command
    if cmd == 'off':
        pattern = patterns.pattern_all_off(config)
        title = "全灭 ALL OFF"
        frame = protocol.encode_frame(protocol.CMD_ALL_OFF, b'', args.seq)
    elif cmd == 'on':
        pattern = patterns.pattern_all_on(config)
        title = "全亮 ALL ON"
        payload = protocol.pattern_to_bytes(pattern)
        frame = protocol.encode_frame(protocol.CMD_SET_FRAME, payload, args.seq)
    elif cmd == 'checker':
        pattern = patterns.pattern_checker(config)
        title = "棋盘格 CHECKER"
        payload = protocol.pattern_to_bytes(pattern)
        frame = protocol.encode_frame(protocol.CMD_SET_FRAME, payload, args.seq)
    elif cmd == 'one':
        pattern = patterns.pattern_one(config, args.row, args.col)
        title = f"单点 ONE (row={args.row}, col={args.col})"
        payload = protocol.pattern_to_bytes(pattern)
        frame = protocol.encode_frame(protocol.CMD_SET_FRAME, payload, args.seq)
    elif cmd == 'random':
        pattern = patterns.pattern_random(config, seed=args.seed, density=args.density)
        title = f"随机 RANDOM (seed={args.seed})"
        payload = protocol.pattern_to_bytes(pattern)
        frame = protocol.encode_frame(protocol.CMD_SET_FRAME, payload, args.seq)
    elif cmd == 'row':
        pattern = patterns.pattern_rows(config, args.n)
        title = f"第{args.n}行整行亮"
        payload = protocol.pattern_to_bytes(pattern)
        frame = protocol.encode_frame(protocol.CMD_SET_FRAME, payload, args.seq)
    elif cmd == 'col':
        pattern = patterns.pattern_cols(config, args.n)
        title = f"第{args.n}列整列亮"
        payload = protocol.pattern_to_bytes(pattern)
        frame = protocol.encode_frame(protocol.CMD_SET_FRAME, payload, args.seq)

    # 显示图案
    patterns.print_pattern(pattern, title)

    # 显示协议帧
    print(f"\n{'─'*50}")
    print(f"  协议帧 (seq={args.seq}, {len(frame)} bytes):")
    protocol.hex_dump(frame)

    if args.dry_run:
        print("\n  [DRY-RUN] 未发送，仅显示")
    else:
        print(f"\n  [TODO] 需要连接串口 {args.port or 'COM5'} 才能发送")
        print(f"  用法: python arrayctl.py {cmd} --port COM5")


if __name__ == "__main__":
    main()
