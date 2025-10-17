

#include "config.h"
#include "my_wifi.h"
#include "wifi_communicator.h"
#include <ESP32Servo.h>

Servo myServo;
int servoPin = 13;


#define ENABLE_DEBUG /* <-- Commenting this line will remove any trace of debug printing */
#include <MacroDebugger.h>

// Communication messages
char incoming_msg[MAX_BUFFER_LEN] = {0};
char response[MAX_BUFFER_LEN] = {0};

void setup(){
  DEBUG_BEGIN();
  
  setup_wifi();
  
  setup_wifi_communicator();

  pinMode(LED_PIN, OUTPUT);

  pinMode(Buzzer_PIN, OUTPUT);

  DEBUG_I("Done setting up!");
}

void loop(){

  // if we lost connection, we attempt to reconnect (blocking)
  if(!is_client_connected()){ connect_client(); }
  
  bool received = get_message(incoming_msg);

  if(received){
    DEBUG_I("Received: %s", incoming_msg);
    uint8_t start = 0;

  myServo.attach(servoPin);
  myServo.write(45); 
  delay(2000); //Half speed in backwards for 2 sec
  myServo.write(135);
  delay(2000); //Half speed in forward for 2 sec
  myServo.write(90); //stop

    if(incoming_msg[0] == 'A'){
      sprintf(response, "%s", ACK);
      start++;
    }

    //switch the number and do the appropriate action
    switch(incoming_msg[start]){
      case 'n':

        Serial.print("no person detected");
        digitalWrite(LED_PIN, LOW);
        break;

      case 'p':
        digitalWrite(LED_PIN, HIGH);
        Serial.print("person detected");
        break;

      case 'm':
        Serial.print("connection confirmed");
        digitalWrite(18, HIGH);
        break;
      default:
      case 'f':
      
        break;
    }

    // If start is bigger than 0, then we have to acknowledge the reception
    if(start > 0){
      send_message(response);
      // Clear the response buffer
      memset(response, 0, MAX_BUFFER_LEN);
    }
  }

 
}
