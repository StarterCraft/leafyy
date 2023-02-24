void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
}

void loop() {
  // put your main code here, to run repeatedly:
  if (Serial.available() > 0) {
    for (int i = 0; i<9; i++)
    Serial.write(0xFF);
  }

  
  Serial.write(0xA0);
}
