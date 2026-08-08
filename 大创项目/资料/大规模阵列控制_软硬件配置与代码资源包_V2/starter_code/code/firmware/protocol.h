#ifndef ARRAY_PROTOCOL_H
#define ARRAY_PROTOCOL_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#define ARRAY_PROTOCOL_SOF0 0xA5u
#define ARRAY_PROTOCOL_SOF1 0x5Au
#define ARRAY_PROTOCOL_VERSION 1u
#define ARRAY_PROTOCOL_MAX_PAYLOAD 4096u

typedef enum {
    ARRAY_CMD_PING = 0x01,
    ARRAY_CMD_SET_FRAME = 0x02,
    ARRAY_CMD_SET_ONE = 0x03,
    ARRAY_CMD_ALL_OFF = 0x04,
    ARRAY_CMD_GET_STATUS = 0x05,
    ARRAY_CMD_PLAY = 0x06,
    ARRAY_CMD_STOP = 0x07,
    ARRAY_CMD_SET_RATE = 0x08,
    ARRAY_CMD_ACK = 0x80
} array_command_t;

typedef enum {
    ARRAY_STATUS_OK = 0,
    ARRAY_STATUS_BAD_CRC = 1,
    ARRAY_STATUS_BAD_LENGTH = 2,
    ARRAY_STATUS_BAD_COMMAND = 3,
    ARRAY_STATUS_BUSY = 4,
    ARRAY_STATUS_OUT_OF_RANGE = 5,
    ARRAY_STATUS_DRIVER_ERROR = 6,
    ARRAY_STATUS_TIMEOUT = 7
} array_status_t;

typedef struct {
    uint8_t version;
    uint8_t command;
    uint16_t sequence;
    uint16_t length;
    const uint8_t *payload;
} array_frame_view_t;

uint16_t array_crc16_ccitt(const uint8_t *data, size_t length);

/* Decode one already-delimited complete frame. Multi-byte fields are little-endian. */
bool array_protocol_decode(
    const uint8_t *raw,
    size_t raw_length,
    array_frame_view_t *out,
    array_status_t *error_status);

#endif
