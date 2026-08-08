#ifndef ARRAY_DRIVER_H
#define ARRAY_DRIVER_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

/* Replace this include with the HAL header selected by CubeMX. */
#include "stm32g4xx_hal.h"

typedef enum {
    ARRAY_DRIVER_IDLE = 0,
    ARRAY_DRIVER_DMA_BUSY,
    ARRAY_DRIVER_WAIT_SPI_END,
    ARRAY_DRIVER_ERROR
} array_driver_state_t;

typedef struct {
    SPI_HandleTypeDef *spi;
    GPIO_TypeDef *latch_port;
    uint16_t latch_pin;
    GPIO_TypeDef *oe_port;
    uint16_t oe_pin;
    GPIO_PinState oe_disabled_level;
    size_t frame_bytes;
    volatile array_driver_state_t state;
    volatile uint32_t frames_latched;
    volatile uint32_t dma_errors;
    volatile uint32_t spi_timeouts;
} array_driver_t;

void array_driver_init(array_driver_t *driver);
bool array_driver_submit(array_driver_t *driver, uint8_t *frame, size_t length);
void array_driver_poll(array_driver_t *driver);
void array_driver_force_off(array_driver_t *driver);
void array_driver_set_enabled(array_driver_t *driver, bool enabled);
void array_driver_on_tx_complete(array_driver_t *driver, SPI_HandleTypeDef *spi);
void array_driver_on_error(array_driver_t *driver, SPI_HandleTypeDef *spi);

#endif
