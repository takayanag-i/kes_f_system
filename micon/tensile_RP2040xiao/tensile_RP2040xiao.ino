void send_data(void);

void setup() {
  pinMode(37, OUTPUT);
  Serial.begin(115200);
  analogReadResolution(12);     // ADCのフルスケールを12ビットに設定
  digitalWrite(37, HIGH);       // ノイズ対策のため電源をPWMモードに設定
  attachInterrupt(3, send_data, RISING);
  delay(500);
}

void loop() {
}

void send_data(void) {
  uint16_t d, f1, f2;
  d = analogRead(26);// ADC0の値を読む
  f1 = analogRead(28);
  f2 = analogRead(27);
  Serial.print(d);
  Serial.print(',');
  Serial.print(f1);
  Serial.print(',');
  Serial.println(f2);
}