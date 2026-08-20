"""
protocol.py - 二进制通信协议模块
功能：将图案矩阵编码为串口字节帧，以及从字节帧解码

帧格式（共 12 + payload 字节）：
  [A5] [5A] [VER] [CMD] [SEQ_LO] [SEQ_HI] [LEN_LO] [LEN_HI] [PAYLOAD...] [CRC_LO] [CRC_HI]
   SOF0  SOF1  版本  命令   序列号低   序列号高   长度低    长度高    数据...     CRC低     CRC高
"""

import struct
import numpy as np

# ========== 常量定义 ==========

SOF0 = 0xA5       # 帧头第1字节
SOF1 = 0x5A       # 帧头第2字节
VERSION = 1       # 协议版本

# 命令字
CMD_PING      = 0x01   # 心跳测试
CMD_GET_STATUS = 0x02  # 获取状态
CMD_SET_FRAME  = 0x03  # 设置整帧图案
CMD_ALL_OFF    = 0x04  # 全部关闭
CMD_SET_CHANNEL = 0x05 # 设置单通道
CMD_PLAY       = 0x06  # 播放图案序列
CMD_STOP       = 0x07  # 停止播放

# 状态码
STATUS_OK          = 0x00
STATUS_BAD_CRC     = 0x01
STATUS_BAD_LENGTH  = 0x02
STATUS_BUSY        = 0x03
STATUS_TIMEOUT     = 0x04


# ========== CRC16-CCITT 校验算法 ==========

def crc16_ccitt(data: bytes) -> int:
    """
    计算 CRC16-CCITT 校验值
    测试向量: crc16_ccitt(b'123456789') == 0x29B1
    """
    crc = 0xFFFF
    for byte in data:
        crc ^= byte << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc = crc << 1
            crc &= 0xFFFF
    return crc


# 验证 CRC 算法正确性
assert crc16_ccitt(b"123456789") == 0x29B1, "CRC算法错误！"
print("[OK] CRC16-CCITT 算法验证通过")


# ========== 编码：把命令+数据打包成字节帧 ==========

def encode_frame(command: int, payload: bytes = b'', sequence: int = 0) -> bytes:
    """
    编码一帧数据

    参数:
        command: 命令字 (如 CMD_SET_FRAME)
        payload: 数据内容 (如 32字节的图案数据)
        sequence: 序列号 (0-65535, 用于匹配请求和响应)

    返回:
        完整的字节帧 (bytes)
    """
    # 检查序列号范围
    if not (0 <= sequence <= 0xFFFF):
        raise ValueError(f"序列号超出范围: {sequence}")

    # 检查 payload 长度
    if len(payload) > 0xFFFF:
        raise ValueError(f"payload 太长: {len(payload)} 字节")

    # 打包头部（不含 SOF 和 CRC）
    # < 表示小端字节序, B=1字节, H=2字节
    header = struct.pack('<BBHH',
        VERSION,      # 1字节: 协议版本
        command,      # 1字节: 命令字
        sequence,     # 2字节: 序列号
        len(payload)  # 2字节: payload长度
    )

    # 计算 CRC（覆盖 header + payload，不覆盖 SOF 和 CRC 本身）
    crc_data = header + payload
    crc = crc16_ccitt(crc_data)

    # 组装完整帧
    frame = bytes([SOF0, SOF1]) + header + payload + struct.pack('<H', crc)

    return frame


# ========== 解码：从字节帧还原出命令和数据 ==========

def decode_frame(frame: bytes) -> dict:
    """
    解码一帧数据

    参数:
        frame: 完整的字节帧

    返回:
        字典: {'version', 'command', 'sequence', 'payload', 'crc_ok'}
    """
    # 最小帧长度: 2(SOF) + 6(header) + 0(payload) + 2(CRC) = 10
    if len(frame) < 10:
        raise ValueError(f"帧太短: {len(frame)} 字节")

    # 检查帧头
    if frame[0] != SOF0 or frame[1] != SOF1:
        raise ValueError(f"帧头错误: {frame[0]:02X} {frame[1]:02X}")

    # 解析头部
    version, command, sequence, length = struct.unpack('<BBHH', frame[2:8])

    # 检查总长度
    expected_len = 2 + 6 + length + 2
    if len(frame) != expected_len:
        raise ValueError(f"长度不匹配: 期望{expected_len}, 实际{len(frame)}")

    # 提取 payload
    payload = frame[8:8+length]

    # 提取并验证 CRC
    received_crc = struct.unpack('<H', frame[8+length:8+length+2])[0]
    crc_data = frame[2:8+length]  # header + payload
    calculated_crc = crc16_ccitt(crc_data)
    crc_ok = (received_crc == calculated_crc)

    return {
        'version': version,
        'command': command,
        'sequence': sequence,
        'payload': payload,
        'crc_ok': crc_ok,
        'received_crc': received_crc,
        'calculated_crc': calculated_crc
    }


# ========== 矩阵 <-> 字节 转换 ==========

def pattern_to_bytes(pattern: np.ndarray, bit_order='lsb_first') -> bytes:
    """
    将 0/1 矩阵转换为字节流

    例如 16x16 矩阵 → 256个bit → 32字节

    参数:
        pattern: 0/1 矩阵 (numpy array)
        bit_order: 'lsb_first' (低位在前) 或 'msb_first' (高位在前)

    返回:
        bytes: 打包后的字节流
    """
    # 把二维矩阵展平成一维
    flat = pattern.flatten()
    total_bits = len(flat)

    # 计算需要多少字节
    num_bytes = (total_bits + 7) // 8

    result = bytearray(num_bytes)

    for i, bit in enumerate(flat):
        byte_index = i // 8
        bit_index = i % 8

        if bit_order == 'lsb_first':
            # 低位在前: bit0 在最低位
            if bit:
                result[byte_index] |= (1 << bit_index)
        else:
            # 高位在前: bit0 在最高位
            if bit:
                result[byte_index] |= (1 << (7 - bit_index))

    return bytes(result)


def bytes_to_pattern(data: bytes, rows: int, cols: int, bit_order='lsb_first') -> np.ndarray:
    """
    将字节流还原为 0/1 矩阵（pattern_to_bytes 的逆操作）
    """
    total_bits = rows * cols
    pattern = np.zeros((rows, cols), dtype=np.uint8)

    flat = np.zeros(total_bits, dtype=np.uint8)

    for i in range(total_bits):
        byte_index = i // 8
        bit_index = i % 8

        if byte_index >= len(data):
            break

        if bit_order == 'lsb_first':
            flat[i] = (data[byte_index] >> bit_index) & 1
        else:
            flat[i] = (data[byte_index] >> (7 - bit_index)) & 1

    pattern = flat.reshape((rows, cols))
    return pattern


# ========== 快捷函数：一键生成 SET_FRAME 帧 ==========

def make_set_frame(pattern: np.ndarray, sequence: int = 0) -> bytes:
    """
    一键生成"设置整帧图案"命令

    参数:
        pattern: 0/1 矩阵
        sequence: 序列号

    返回:
        完整的字节帧
    """
    payload = pattern_to_bytes(pattern)
    return encode_frame(CMD_SET_FRAME, payload, sequence)


# ========== 打印帧的十六进制表示 ==========

def hex_dump(data: bytes, title="") -> str:
    """将字节数据格式化为十六进制字符串"""
    if title:
        print(f"\n{title}")
    hex_str = ' '.join(f'{b:02X}' for b in data)
    print(f"  [{len(data)} bytes] {hex_str}")
    return hex_str


# ========== 自测 ==========

if __name__ == "__main__":
    print("=" * 50)
    print("  协议模块自测")
    print("=" * 50)

    # 测试1: PING 命令（无 payload）
    print("\n--- 测试1: PING 命令 ---")
    frame = encode_frame(CMD_PING, b'', sequence=1)
    hex_dump(frame, "编码结果:")

    decoded = decode_frame(frame)
    print(f"解码: command={decoded['command']}, seq={decoded['sequence']}, crc_ok={decoded['crc_ok']}")

    # 测试2: SET_FRAME 命令（32字节 payload）
    print("\n--- 测试2: SET_FRAME 命令 ---")
    test_pattern = np.zeros((16, 16), dtype=np.uint8)
    test_pattern[3, 5] = 1  # 点亮 (3,5)

    payload = pattern_to_bytes(test_pattern)
    print(f"图案 → {len(payload)} 字节 payload")
    hex_dump(payload, "Payload:")

    frame = make_set_frame(test_pattern, sequence=42)
    hex_dump(frame, "完整帧:")

    decoded = decode_frame(frame)
    print(f"解码: command={decoded['command']:#04x}, seq={decoded['sequence']}, crc_ok={decoded['crc_ok']}")

    # 还原图案
    recovered = bytes_to_pattern(decoded['payload'], 16, 16)
    print(f"\n还原后的矩阵 (3,5) 位置: {recovered[3, 5]}")
    print(f"还原是否一致: {np.array_equal(test_pattern, recovered)}")

    # 测试3: ALL_OFF 命令
    print("\n--- 测试3: ALL_OFF 命令 ---")
    frame = encode_frame(CMD_ALL_OFF, b'', sequence=0)
    hex_dump(frame, "编码结果:")
