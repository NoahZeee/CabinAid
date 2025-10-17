
#ifndef __CONFG_H___
#define __CONFG_H___

/* Pins definitions */
#define LED_PIN                     19
#define Buzzer_PIN                  32
#define BTN_PIN                     25

/* Communication params */
#define ACK                         "A" // acknowledgment packet
#define QUEUE_LEN                   5
#define MAX_BUFFER_LEN              128

/* WiFi params */
#define WIFI_SSID                   "zztv"
#define WIFI_PASSWORD               "12345678"

/* Socket */
#define SERVER_ADDRESS              "192.168.80.177" //tis is the ip address of your wifi
#define SERVER_PORT                 11111

#endif // __CONFG_H___
