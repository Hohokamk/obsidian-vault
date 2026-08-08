#include "protocol.h"

static uint16_t read_le16(const uint8_t *p)
{
    return (uint16_t)p[0] | ((uint16_t)p[1] << 8);
}

uint16_t array_crc16_ccitt(const uint8_t *data, size_t length)
{
    uint16_t crc = 0xFFFFu;
    for (size_t i = 0; i < length; ++i) {
        crc ^= (uint16_t)data[i] << 8;
        for (unsigned bit = 0; bit < 8; ++bit) {
            crc = (crc & 0x8000u) ? (uint16_t)((crc << 1) ^ 0x1021u)
                                  : (uint16_t)(crc << 1);
        }
    }
    return crc;
}

bool array_protocol_decode(
    const uint8_t *raw,
    size_t raw_length,
    array_frame_view_t *out,
    array_status_t *error_status)
{
    const size_t fixed = 2u + 1u + 1u + 2u + 2u + 2u;
    if (error_status != NULL) {
        *error_status = ARRAY_STATUS_OK;
    }
    if (raw == NULL || out == NULL || raw_length < fixed) {
        if (error_status != NULL) *error_status = ARRAY_STATUS_BAD_LENGTH;
        return false;
    }
    if (raw[0] != ARRAY_PROTOCOL_SOF0 || raw[1] != ARRAY_PROTOCOL_SOF1) {
        if (error_status != NULL) *error_status = ARRAY_STATUS_BAD_COMMAND;
        return false;
    }
    const uint16_t payload_length = read_le16(&raw[6]);
    if (payload_length > ARRAY_PROTOCOL_MAX_PAYLOAD || raw_length != fixed + payload_length) {
        if (error_status != NULL) *error_status = ARRAY_STATUS_BAD_LENGTH;
        return false;
    }
    const size_t body_length = 1u + 1u + 2u + 2u + payload_length;
    const uint16_t received_crc = read_le16(&raw[2u + body_length]);
    const uint16_t calculated_crc = array_crc16_ccitt(&raw[2], body_length);
    if (received_crc != calculated_crc) {
        if (error_status != NULL) *error_status = ARRAY_STATUS_BAD_CRC;
        return false;
    }
    out->version = raw[2];
    out->command = raw[3];
    out->sequence = read_le16(&raw[4]);
    out->length = payload_length;
    out->payload = &raw[8];
    return true;
}
