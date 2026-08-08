#include "array_driver.h"

static void latch_pulse(array_driver_t *driver)
{
    HAL_GPIO_WritePin(driver->latch_port, driver->latch_pin, GPIO_PIN_SET);
    /* For high SCLK or strict timing, replace these NOPs with a timer-generated pulse. */
    __NOP();
    __NOP();
    HAL_GPIO_WritePin(driver->latch_port, driver->latch_pin, GPIO_PIN_RESET);
}

static bool spi_really_finished(SPI_HandleTypeDef *spi)
{
    /*
     * IMPORTANT: adapt this function to the selected STM32G4 SPI instance and
     * HAL/LL version. DMA complete means memory-to-peripheral transfer complete,
     * not necessarily that the final bit has left the shifter.
     *
     * For STM32G4, inspect RM0440 and generated HAL code for TXC/EOT/BSY and
     * FIFO status. Do not copy a flag sequence from another STM32 family.
     */
#ifdef SPI_FLAG_TXC
    return (__HAL_SPI_GET_FLAG(spi, SPI_FLAG_TXC) != RESET);
#else
    return (__HAL_SPI_GET_FLAG(spi, SPI_FLAG_BSY) == RESET);
#endif
}

void array_driver_init(array_driver_t *driver)
{
    if (driver == NULL) return;
    driver->state = ARRAY_DRIVER_IDLE;
    driver->frames_latched = 0u;
    driver->dma_errors = 0u;
    driver->spi_timeouts = 0u;
    HAL_GPIO_WritePin(driver->latch_port, driver->latch_pin, GPIO_PIN_RESET);
    array_driver_force_off(driver);
}

void array_driver_set_enabled(array_driver_t *driver, bool enabled)
{
    if (driver == NULL) return;
    GPIO_PinState level = driver->oe_disabled_level;
    if (enabled) {
        level = (driver->oe_disabled_level == GPIO_PIN_SET) ? GPIO_PIN_RESET : GPIO_PIN_SET;
    }
    HAL_GPIO_WritePin(driver->oe_port, driver->oe_pin, level);
}

void array_driver_force_off(array_driver_t *driver)
{
    array_driver_set_enabled(driver, false);
}

bool array_driver_submit(array_driver_t *driver, uint8_t *frame, size_t length)
{
    if (driver == NULL || frame == NULL || length != driver->frame_bytes) return false;
    if (driver->state != ARRAY_DRIVER_IDLE) return false;
    driver->state = ARRAY_DRIVER_DMA_BUSY;
    if (HAL_SPI_Transmit_DMA(driver->spi, frame, (uint16_t)length) != HAL_OK) {
        driver->state = ARRAY_DRIVER_ERROR;
        driver->dma_errors++;
        array_driver_force_off(driver);
        return false;
    }
    return true;
}

void array_driver_on_tx_complete(array_driver_t *driver, SPI_HandleTypeDef *spi)
{
    if (driver == NULL || spi != driver->spi) return;
    if (driver->state == ARRAY_DRIVER_DMA_BUSY) {
        driver->state = ARRAY_DRIVER_WAIT_SPI_END;
    }
}

void array_driver_on_error(array_driver_t *driver, SPI_HandleTypeDef *spi)
{
    if (driver == NULL || spi != driver->spi) return;
    driver->dma_errors++;
    driver->state = ARRAY_DRIVER_ERROR;
    array_driver_force_off(driver);
}

void array_driver_poll(array_driver_t *driver)
{
    if (driver == NULL) return;
    if (driver->state == ARRAY_DRIVER_WAIT_SPI_END && spi_really_finished(driver->spi)) {
        latch_pulse(driver);
        driver->frames_latched++;
        driver->state = ARRAY_DRIVER_IDLE;
    }
}

/*
 * In the CubeMX user callback, call:
 *
 * void HAL_SPI_TxCpltCallback(SPI_HandleTypeDef *hspi) {
 *     array_driver_on_tx_complete(&g_array_driver, hspi);
 * }
 *
 * void HAL_SPI_ErrorCallback(SPI_HandleTypeDef *hspi) {
 *     array_driver_on_error(&g_array_driver, hspi);
 * }
 */
