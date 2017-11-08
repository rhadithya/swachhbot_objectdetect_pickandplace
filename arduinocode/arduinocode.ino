/*
 * @d!thy@
 * mqttbot3
 * this uses digitalWrite / pwm using delays
 * Connections are as follows-
 * blue: common ground for both nodemcu and motor driver
 * red : nodemcu d1 to IN2+
 * green: nodemcu d2 to in2
 * orange: nodemcu d3 to in1+
 * yellow: nodemcu d4 to in
 * left motor to motor2 slot
 * right motor to motor1 slot
 */

//pin mapping
static const uint8_t DD0   = 16;
static const uint8_t DD1   = 5;
static const uint8_t DD2   = 4;
static const uint8_t DD3   = 0;
static const uint8_t DD4   = 2;
static const uint8_t DD5   = 14;
static const uint8_t DD6   = 12;
static const uint8_t DD7   = 13;
static const uint8_t DD8   = 15;
static const uint8_t DD9   = 3;
static const uint8_t DD10  = 1;

int ton=5;        //2,10 is good 5,50 is better
int toff=25;
int state=4;

int straightton=5;
int straighttoff=20;

#include <ESP8266WiFi.h>
#include <PubSubClient.h>


//---------------MOTOR FUNCTIONS----------------//

//function to stop the robot
void motors_stop()
{

  //stop both motors
  digitalWrite(DD1, LOW);
  digitalWrite(DD2, LOW);
  digitalWrite(DD3, LOW);
  digitalWrite(DD4, LOW);
  //delay(1000);
  
}

//function for robot forward motion 
void motors_forward()
{

  //forward both motors
  digitalWrite(DD1, LOW);
  digitalWrite(DD2, HIGH);
  digitalWrite(DD3, HIGH);
  digitalWrite(DD4, LOW);
  delay(straightton);
  
  digitalWrite(DD1, LOW);
  digitalWrite(DD2, LOW);
  digitalWrite(DD3, LOW);
  digitalWrite(DD4, LOW);
  delay(straighttoff);
  
}

//function for robot backward motion
void motors_backward()
{

  //reverse both motors
  digitalWrite(DD1, HIGH);
  digitalWrite(DD2, LOW);
  digitalWrite(DD3, LOW);
  digitalWrite(DD4, HIGH);
  delay(ton);
  
  digitalWrite(DD1, LOW);
  digitalWrite(DD2, LOW);
  digitalWrite(DD3, LOW);
  digitalWrite(DD4, LOW);
  delay(toff);
  
}

//function for robot left motion
void motors_left()
{
  //left both motors
  digitalWrite(DD1, HIGH);
  digitalWrite(DD2, LOW);
  digitalWrite(DD3, HIGH);
  digitalWrite(DD4, LOW);
  delay(ton);
  
  digitalWrite(DD1, LOW);
  digitalWrite(DD2, LOW);
  digitalWrite(DD3, LOW);
  digitalWrite(DD4, LOW);
  delay(toff);
  
}

//function for robot right motion
void motors_right()
{
  //right both motors
  digitalWrite(DD1, LOW);
  digitalWrite(DD2, HIGH);
  digitalWrite(DD3, LOW);
  digitalWrite(DD4, HIGH);
  delay(ton);
  
  digitalWrite(DD1, LOW);
  digitalWrite(DD2, LOW);
  digitalWrite(DD3, LOW);
  digitalWrite(DD4, LOW);
  delay(toff);
  
}






//-----------------------------------------------------//

//-------------------------WIFI-------------------------------//
const char* ssid = "abcd";
const char* password = "abcdlmnop";    
//const char* mqtt_server = "192.168.59.138";
//const char* mqtt_server = "192.168.0.102";
const char* mqtt_server = "192.168.43.32";

WiFiClient espClient;
PubSubClient client(espClient);
long lastMsg = 0;
char msg[50];
int value = 0;

void setup_wifi() {

  delay(10);
  // We start by connecting to a WiFi network
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  randomSeed(micros());

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}


void callback(char* topic, byte* payload, unsigned int length) {
  //Serial.print("Message arrived [");
 // Serial.print(topic);
  //Serial.print("] ");
  /*
  for (int i = 0; i < length; i++) {
    Serial.print((char)payload[i]);
    //Serial.print((int)payload[0] - (int)'0');
  }
  Serial.println();
  */
  state=(int)payload[0] - (int)'0'; 
  Serial.println(state);
}



void reconnect() {
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Create a random client ID
    String clientId = "ESP8266Client-";
    clientId += String(random(0xffff), HEX);
    // Attempt to connect
    if (client.connect(clientId.c_str())) {
      Serial.println("connected");
      // Once connected, publish an announcement...
      client.publish("outTopic", "hello world");
      // ... and resubscribe
      client.subscribe("errorvals");


      Serial.println("");
      Serial.println("WiFi connected");
      Serial.println("IP address: ");
      Serial.println(WiFi.localIP());


    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      // delay(5000);
    }
  }
}

//-------------------------------------------------------------//



void setup() {
  pinMode(BUILTIN_LED, OUTPUT);     // Initialize the BUILTIN_LED pin as an output
  pinMode(DD1, OUTPUT);
  pinMode(DD2, OUTPUT);
  pinMode(DD3, OUTPUT);
  pinMode(DD4, OUTPUT);
  
  Serial.begin(115200);
  setup_wifi();
  //delay(5000);
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);

}

void loop() {
   if (!client.connected()) {
    reconnect();
  }
  
  
//  while(1)
//  {
    switch (state)
  {
    case 0:
      motors_forward();
      //Serial.println("0: motors forward");
      break;
    case 1:
      motors_left();
      //Serial.println("1: motors left");
      break;

    case 2:
      motors_right();
      //Serial.println("2: motors right");
      break;
      
    case 3:
      motors_backward();
      //Serial.println("3: motors backward");
      break;
    case 4:
      motors_stop();
      //Serial.println("4: motors stop");
      break;
   
    default:
      motors_stop();
      //Serial.println("default: motors stop");
      break;

 // }
  }
  
client.loop();
}