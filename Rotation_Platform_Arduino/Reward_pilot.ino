const int Balluff_In_analogPin = 3;  // Analog input pin that the potentiometer is attached to
const int Valve_Out_digitalPin = 10;  // Analog output pin that the LED is attached to
const long Balluf_Threshold_for_reward = 511; // Must be between 0 and 1023 (0 corresponds to 0 Volts, 1023 corresponds to 5V, therefore 511 correponds to approximately 2.5 Volts)

long Balluff_capacitance = 0;  // value read from the pot  (goes from 0 to 1023). In reality, the Balluff will send 0 or 1023, so finally, there is no need for an analog pin
int Reward_authorization = 0;
int Licking_status = 0;

String order_from_computer;

void setup() {
  pinMode(Balluff_In_analogPin, INPUT); 
  pinMode(Valve_Out_digitalPin, OUTPUT);

  Serial.begin(115200);
  Serial.setTimeout(1);
}

void  loop() {
  // Is the mouse granted a reward ? It reads meassges from computer to know
  order_from_computer = Serial.readStringUntil('.');

  if (order_from_computer == "Reward"){
    Reward_authorization = 1;
  }
  if (order_from_computer == "Stop"){
    Reward_authorization = 0;
  }
  if (order_from_computer == "Punish"){
    Reward_authorization = 0;
  }

  // Is the mouse licking ?
  Balluff_capacitance = analogRead(Balluff_In_analogPin);
  
  if (Balluff_capacitance > Balluf_Threshold_for_reward) {
    Licking_status = 1;
  } else {
    Licking_status = 0;
  }

  // Delivery of the reward
  if ((Reward_authorization == 1) && (Licking_status == 1)) {
    // Opening of the lick-port
    digitalWrite(Valve_Out_digitalPin, HIGH);
    // Sending informatioin to the computer (Not required anymore as integrated in Open-ePhys)
    // Serial.println("Licking the reward");

  } else if ((Reward_authorization == 0) && (Licking_status == 1)) {
    // Closing of the lick-port
    digitalWrite(Valve_Out_digitalPin, LOW);
    // Sending informatioin to the computer (Not required anymore as integrated in Open-ePhys)
    // Serial.println("Licking nothing");
  }

  else {
    // Closing of the lick-port
    digitalWrite(Valve_Out_digitalPin, LOW);
    // Sending informatioin to the computer (Not required anymore as integrated in Open-ePhys)
    // Serial.println("Nothing happens");
  }


  //delay(100);



}