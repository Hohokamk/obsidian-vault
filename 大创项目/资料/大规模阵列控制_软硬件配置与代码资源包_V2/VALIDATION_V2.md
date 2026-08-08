# V2资源包验证记录

## 1. 验证结果

- Python验证脚本返回码：`0`
- Bash脚本语法检查返回码：`0`
- Markdown文件数：`23`
- Markdown总行数：`6349`
- URL总出现次数：`142`
- 唯一URL数：`93`
- 语法可疑URL数：`0`

## 2. 已实际执行

```text
python -m pytest code/tests -q
python -m compileall -q code
arrayctl.py --dry-run one --row 3 --col 5
generate_mapping.py array_config.yaml
simulation/demo.py
bash -n run_kicad_checks.sh
```

测试输出摘要：

```text
...........                                                              [100%]
11 passed in 0.17s
command=SET_FRAME payload_bytes=32
A5 5A 01 02 00 00 20 00 00 00 00 00 00 00 20 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 35 3A
generated mapping for 256 channels in /mnt/data/大规模阵列控制_软硬件配置与代码资源包_V2/starter_code/validation_output/mapping
continuous: first_global_max=25.00 deg, strong_peak_angles=[25.0], BW3dB=7.1000000000000085, PSLL~=-13.15 dB
one_bit: first_global_max=-24.10 deg, strong_peak_angles=[-24.099999999999994, 24.10000000000001], BW3dB=6.799999999999997, PSLL~=-0.00 dB
amplitude_mask: first_global_max=0.00 deg, strong_peak_angles=[0.0], BW3dB=6.6000000000000085, PSLL~=-12.64 dB
Note: ideal +/-1 real weights may create equal symmetric twin beams in this simple model.
saved to /mnt/data/大规模阵列控制_软硬件配置与代码资源包_V2/starter_code/validation_output/simulation/simulation_results

== pytest ==
/opt/pyvenv/bin/python -m pytest code/tests -q

== compileall ==
/opt/pyvenv/bin/python -m compileall -q code

== protocol dry-run ==
/opt/pyvenv/bin/python arrayctl.py --dry-run one --row 3 --col 5

== mapping generation ==
/opt/pyvenv/bin/python code/automation/generate_mapping.py code/config/array_config.yaml --out /mnt/data/大规模阵列控制_软硬件配置与代码资源包_V2/starter_code/validation_output/mapping

== array-factor demonstration ==
/opt/pyvenv/bin/python /mnt/data/大规模阵列控制_软硬件配置与代码资源包_V2/starter_code/code/simulation/demo.py

Validation outputs: /mnt/data/大规模阵列控制_软硬件配置与代码资源包_V2/starter_code/validation_output
```

## 3. 生成物

- `validation_artifacts/generated_mapping/`：256项映射CSV、C头文件和配置SHA；
- `validation_artifacts/simulation/`：连续相位、理想1 bit和二值幅度结果；
- `validation_artifacts/validation_stdout.txt`；
- `validation_artifacts/validation_stderr.txt`。

## 4. 尚未在本环境完成的验证

以下必须由学生在真实环境完成：

- STM32CubeIDE编译；
- NUCLEO-G474RE下载与调试；
- HAL中的`TXC/EOT/BSY`适配；
- TLC6C598 8/16/64路实物；
- KiCad 10真实工程的ERC/DRC与生产文件；
- KiBot配置；
- 逻辑分析仪和示波器波形；
- 256路、1024路、视觉和天线接口。

## 5. 重要限制

- `array_driver.c`是HAL接入骨架，不是未经修改即可烧录的完整工程；
- `run_kicad_checks.sh`语法已按KiCad 10官方CLI修正，但需要真实`.kicad_sch/.kicad_pcb`才能执行；
- 外部网址可能在未来变化，关键PDF和仓库应按`docs/14_资源下载_本地归档与许可证.md`归档；
- 第三方示例不能替代官方数据手册。
