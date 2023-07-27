const int a=30; 

void setup() {
  pinMode(D4, OUTPUT);
  pinMode(BUILTIN_LED, OUTPUT);
  digitalWrite(D4, HIGH); 
  digitalWrite(BUILTIN_LED, HIGH); 
  // put your setup code here, to run once:
}

void loop() {
  int sensorValue = analogRead(A0);
  Serial.begin(9600);
  Serial.println(sensorValue);
  if (sensorValue > a) {
    digitalWrite(D4, LOW);
    digitalWrite(BUILTIN_LED, LOW);
  } 
  else {
    digitalWrite(D4, HIGH);
    digitalWrite(BUILTIN_LED, HIGH);
  }
    delay(100);
  // put your main code here, to run repeatedly:

}
