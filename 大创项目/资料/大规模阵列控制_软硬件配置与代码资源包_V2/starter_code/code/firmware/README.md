# STM32 firmware skeleton

These files are designed to be copied into a CubeMX-generated NUCLEO-G474RE project.
They are not a complete standalone STM32CubeIDE project because pin assignments,
clock tree, DMA request, and exact SPI status flags must be generated and verified
against the chosen board and STM32CubeG4 version.

Integration order:

1. Generate a CubeMX project and verify GPIO blink/UART.
2. Configure SPI TX and DMA.
3. Add `array_driver.*` and `protocol.*`.
4. Fill an `array_driver_t` with the generated handles and GPIOs.
5. Keep OE disabled during initialization.
6. Submit a known all-off frame.
7. Verify `HAL_SPI_TxCpltCallback` changes state to `WAIT_SPI_END`.
8. Call `array_driver_poll()` in the main loop.
9. Confirm the true SPI-end flag for STM32G474/RM0440.
10. Only then enable outputs.

Do not use the fallback BSY logic blindly. The exact end-of-transfer procedure is
MCU-family and HAL-version dependent; inspect RM0440, AN5543, and generated HAL code.
