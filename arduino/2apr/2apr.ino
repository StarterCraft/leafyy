void setup()
{
  // put your setup code here, to run once:
  Serial.begin(9600);
  Serial.println(0XEA);
  delay(3000);
}

void loop()
{
  // put your main code here, to run repeatedly:
  if (Serial.available() > 0)
  {
    Serial.println(0XFA);
    delay(3000);

    Serial.flush();
  }

  Serial.println(0XEF);
  delay(1000);
}
