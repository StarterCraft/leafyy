void setup()
{
  // put your setup code here, to run once:
  Serial.begin(9600);
  Serial.println("BIG BANG");
  delay(3000);
}

void loop()
{
  // put your main code here, to run repeatedly:
  if (Serial.available() > 0)
  {
    while(Serial.available()) Serial.read();
    Serial.println("RC RECEIF");
    delay(3000);
  }

  Serial.println("EMPTY STREAM");
  delay(3000);
}
