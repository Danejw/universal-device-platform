/*
 * Universal Device Platform - XIAO ESP32S3 Sense USB bench prototype.
 * ESP-IDF v5.5.x NimBLE, minimal button peripheral.
 * WARNING: unsecured developmental BLE example. NO media, health data or
 * side-effect commands. Physical build and operation remain unverified.
 */
#include <stdbool.h>
#include <string.h>
#include "esp_err.h"
#include "esp_log.h"
#include "nvs_flash.h"
#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "host/ble_hs.h"
#include "host/ble_uuid.h"
#include "host/util/util.h"
#include "nimble/nimble_port.h"
#include "nimble/nimble_port_freertos.h"
#include "services/gap/ble_svc_gap.h"
#include "services/gatt/ble_svc_gatt.h"

#define BUTTON_GPIO GPIO_NUM_1
#define DEVICE_NAME "UDP-W0"
#define BLE_EVENT_BUTTON 'P'
#define BLE_EVENT_PONG '!'
#define BLE_CMD_PING '?'

static const char *TAG = "udp_watch";
static const char manifest[] = "{\"v\":1,\"id\":\"watch-v0\",\"caps\":[\"button.primary\"]}";
static uint8_t own_addr_type;
static uint16_t event_val_handle;
static bool subscribed;
static volatile char event_value = BLE_EVENT_BUTTON;

static const ble_uuid128_t service_uuid = BLE_UUID128_INIT(
    0x10,0xde,0xf2,0x3f,0xca,0xf6,0x08,0x9e,
    0x5f,0x47,0xa8,0x3f,0xe0,0xfb,0x39,0x8d);
static const ble_uuid128_t manifest_uuid = BLE_UUID128_INIT(
    0x11,0xde,0xf2,0x3f,0xca,0xf6,0x08,0x9e,
    0x5f,0x47,0xa8,0x3f,0xe0,0xfb,0x39,0x8d);
static const ble_uuid128_t event_uuid = BLE_UUID128_INIT(
    0x12,0xde,0xf2,0x3f,0xca,0xf6,0x08,0x9e,
    0x5f,0x47,0xa8,0x3f,0xe0,0xfb,0x39,0x8d);
static const ble_uuid128_t command_uuid = BLE_UUID128_INIT(
    0x13,0xde,0xf2,0x3f,0xca,0xf6,0x08,0x9e,
    0x5f,0x47,0xa8,0x3f,0xe0,0xfb,0x39,0x8d);

static int gatt_access(uint16_t conn, uint16_t attr,
                       struct ble_gatt_access_ctxt *ctxt, void *arg)
{
    (void)conn; (void)attr; (void)arg;
    const ble_uuid_t *uuid = ctxt->chr->uuid;
    if (ctxt->op == BLE_GATT_ACCESS_OP_READ_CHR) {
        if (ble_uuid_cmp(uuid, &manifest_uuid.u) == 0) {
            return os_mbuf_append(ctxt->om, manifest, strlen(manifest)) == 0
                ? 0 : BLE_ATT_ERR_INSUFFICIENT_RES;
        }
        if (ble_uuid_cmp(uuid, &event_uuid.u) == 0) {
            char value = event_value;
            return os_mbuf_append(ctxt->om, &value, 1) == 0
                ? 0 : BLE_ATT_ERR_INSUFFICIENT_RES;
        }
    }
    if (ctxt->op == BLE_GATT_ACCESS_OP_WRITE_CHR &&
        ble_uuid_cmp(uuid, &command_uuid.u) == 0) {
        char command;
        if (OS_MBUF_PKTLEN(ctxt->om) != 1 ||
            ble_hs_mbuf_to_flat(ctxt->om, &command, 1, NULL) != 0) {
            return BLE_ATT_ERR_INVALID_ATTR_VALUE_LEN;
        }
        if (command != BLE_CMD_PING) return BLE_ATT_ERR_VALUE_NOT_ALLOWED;
        event_value = BLE_EVENT_PONG;
        if (subscribed) ble_gatts_chr_updated(event_val_handle);
        return 0;
    }
    return BLE_ATT_ERR_UNLIKELY;
}

static const struct ble_gatt_svc_def services[] = {
    {
        .type = BLE_GATT_SVC_TYPE_PRIMARY,
        .uuid = &service_uuid.u,
        .characteristics = (struct ble_gatt_chr_def[]) {
            {.uuid=&manifest_uuid.u, .access_cb=gatt_access,
             .flags=BLE_GATT_CHR_F_READ},
            {.uuid=&event_uuid.u, .access_cb=gatt_access,
             .flags=BLE_GATT_CHR_F_READ | BLE_GATT_CHR_F_NOTIFY,
             .val_handle=&event_val_handle},
            {.uuid=&command_uuid.u, .access_cb=gatt_access,
             .flags=BLE_GATT_CHR_F_WRITE},
            {0}
        },
    },
    {0}
};

static int gap_callback(struct ble_gap_event *event, void *arg);

static void advertise(void)
{
    struct ble_hs_adv_fields fields = {0};
    struct ble_gap_adv_params params = {0};
    fields.flags = BLE_HS_ADV_F_DISC_GEN | BLE_HS_ADV_F_BREDR_UNSUP;
    fields.name = (const uint8_t *) DEVICE_NAME;
    fields.name_len = strlen(DEVICE_NAME);
    fields.name_is_complete = 1;
    fields.uuids128 = &service_uuid;
    fields.num_uuids128 = 1;
    fields.uuids128_is_complete = 1;
    int rc = ble_gap_adv_set_fields(&fields);
    if (rc != 0) { ESP_LOGE(TAG, "advertisement data rc=%d", rc); return; }
    params.conn_mode = BLE_GAP_CONN_MODE_UND;
    params.disc_mode = BLE_GAP_DISC_MODE_GEN;
    rc = ble_gap_adv_start(own_addr_type, NULL, BLE_HS_FOREVER,
                           &params, gap_callback, NULL);
    if (rc != 0) ESP_LOGE(TAG, "advertisement start rc=%d", rc);
}

static int gap_callback(struct ble_gap_event *event, void *arg)
{
    (void)arg;
    switch (event->type) {
    case BLE_GAP_EVENT_CONNECT:
        if (event->connect.status == 0) {
            subscribed = false;
            ESP_LOGI(TAG, "connected");
        } else {
            advertise();
        }
        break;
    case BLE_GAP_EVENT_DISCONNECT:
        subscribed = false;
        ESP_LOGI(TAG, "disconnected");
        advertise();
        break;
    case BLE_GAP_EVENT_SUBSCRIBE:
        if (event->subscribe.attr_handle == event_val_handle) {
            subscribed = event->subscribe.cur_notify != 0;
            ESP_LOGI(TAG, "notifications=%d", (int)subscribed);
        }
        break;
    case BLE_GAP_EVENT_ADV_COMPLETE:
        advertise();
        break;
    default:
        break;
    }
    return 0;
}

static void on_reset(int reason)
{
    ESP_LOGW(TAG, "NimBLE reset reason=%d", reason);
}

static void on_sync(void)
{
    int rc = ble_hs_util_ensure_addr(0);
    if (rc == 0) rc = ble_hs_id_infer_auto(0, &own_addr_type);
    if (rc == 0) advertise();
    else ESP_LOGE(TAG, "no BLE address rc=%d", rc);
}

static void host_task(void *arg)
{
    (void)arg;
    nimble_port_run();
    nimble_port_freertos_deinit();
}

static void button_task(void *arg)
{
    (void)arg;
    int last_sample = 1, stable = 1, count = 0;
    for (;;) {
        int sample = gpio_get_level(BUTTON_GPIO);
        if (sample == last_sample) {
            if (count < 3) count++;
        } else {
            last_sample = sample;
            count = 0;
        }
        if (count >= 2 && sample != stable) {
            stable = sample;
            if (stable == 0) {
                ESP_LOGI(TAG, "button.primary.pressed");
                event_value = BLE_EVENT_BUTTON;
                if (subscribed) ble_gatts_chr_updated(event_val_handle);
            }
        }
        vTaskDelay(pdMS_TO_TICKS(20));
    }
}

void app_main(void)
{
    esp_err_t err = nvs_flash_init();
    if (err == ESP_ERR_NVS_NO_FREE_PAGES ||
        err == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        ESP_ERROR_CHECK(nvs_flash_erase());
        err = nvs_flash_init();
    }
    ESP_ERROR_CHECK(err);

    gpio_config_t button = {
        .pin_bit_mask = (1ULL << BUTTON_GPIO),
        .mode = GPIO_MODE_INPUT,
        .pull_up_en = GPIO_PULLUP_ENABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE
    };
    ESP_ERROR_CHECK(gpio_config(&button));
    ESP_ERROR_CHECK(nimble_port_init());
    ble_svc_gap_init();
    ble_svc_gatt_init();
    ESP_ERROR_CHECK(ble_svc_gap_device_name_set(DEVICE_NAME));
    int rc = ble_gatts_count_cfg(services);
    if (rc == 0) rc = ble_gatts_add_svcs(services);
    if (rc != 0) { ESP_LOGE(TAG, "GATT setup failed rc=%d", rc); return; }
    ble_hs_cfg.sync_cb = on_sync;
    ble_hs_cfg.reset_cb = on_reset;
    nimble_port_freertos_init(host_task);
    xTaskCreate(button_task, "watch_button", 3072, NULL, 5, NULL);
    ESP_LOGW(TAG, "BENCH ONLY: BLE link has no application authorization");
}
