TaskHandle_t thp[2];//マルチスレッドのタスクハンドル格納用
const uint8_t DIR1 = 18;
const uint8_t STEP1 = 19;
const uint8_t DIR2  = 23;
const uint8_t STEP2 = 22;
int sign1, sign2;
volatile float disp1, disp2 = 0.0;
volatile uint8_t serialin;
volatile uint8_t cmd;

void setup() {
  delay(100);
  cmd = '0';
  sign1 = 1; //起動時に時計回りと約束する。
  sign2 = 1; //起動時に時計回りと約束する。
  Serial.begin(115200);
  analogSetAttenuation(ADC_6db);
  pinMode(DIR1, OUTPUT);
  pinMode(STEP1, OUTPUT);
  pinMode(DIR2, OUTPUT);
  pinMode(STEP2, OUTPUT);
  digitalWrite(DIR1, HIGH);
  digitalWrite(STEP1, LOW);
  digitalWrite(DIR2, HIGH);
  digitalWrite(STEP2, LOW);
  pinMode(2, OUTPUT); //picoへ
  digitalWrite(2, LOW);
  xTaskCreatePinnedToCore(Core0a, "Core0a", 4096, NULL, 3, &thp[0], 0);
  xTaskCreatePinnedToCore(Core1b, "Core1b", 4096, NULL, 1, &thp[1], 1);
}

void loop() { //このループはCore1が受け持っている。モータ制御。
  if( cmd == '3' ){
    while(1) {
      digitalWrite(STEP1, HIGH);
      delayMicroseconds(2250);
      digitalWrite(STEP1, LOW);
      disp1 += 0.005 * sign1;
      delayMicroseconds(2250);
      if ( cmd == '4' ){break;}
    }
  }
  delay(1);
}

void Core1b(void *args) {
  while(1)
    if( cmd == '7' ){
    while(1) {
      digitalWrite(STEP2, HIGH);
      delayMicroseconds(2250);
      digitalWrite(STEP2, LOW);
      disp2 += 0.005 * sign2;
      delayMicroseconds(2250);
      if ( cmd == '8' ){break;}
    }
  delay(1);
  }
}

void Core0a(void *args) { //このループはCore0が受け持っている。シリアル通信を行う。ウォッチドッグ有効なのでdelayで抑えている。
  unsigned int i;
  unsigned long tm;

    while (1) {//ここで無限ループを作っておく
      serialin = Serial.read(); //プログラムが走り出したらシリアルを待つ。
      if ( serialin == '0') { // 0が来てたら内側のwhileループへ
        i = 0;
        while(1){
          delay(10);
          digitalWrite(2, HIGH);
          tm = micros();
          Serial.print(disp1);
          Serial.print(',');
          Serial.print(disp2);
          Serial.print(',');
          Serial.println(tm);
          digitalWrite(2, LOW);

          serialin = Serial.read(); //内側のwhileループの中でもう一度シリアルから値をもらう。
          if ( serialin == '1') {break;} //2が来れば，内側のwhileループを抜ける
          else if (serialin == '3') { cmd = '3'; } //計測中にモータ系へ値を送る
          else if (serialin == '4') { cmd = '4'; }
          else if (serialin == '5') {
            sign1 *= -1;
            if (digitalRead(DIR1) == HIGH) { digitalWrite(DIR1, LOW); } else if (digitalRead(DIR1) == LOW) { digitalWrite(DIR1, HIGH); }
          }
          else if (serialin == '7') { cmd = '7'; } //計測中にモータ系へ値を送る
          else if (serialin == '8') { cmd = '8'; }
          else if (serialin == '9') {
            sign2 *= -1;
            if (digitalRead(DIR2) == HIGH) { digitalWrite(DIR2, LOW); } else if (digitalRead(DIR2) == LOW) { digitalWrite(DIR2, HIGH); }
          }
        }//内側のwhileループ閉じ
      }//if閉じ。

      if (serialin == '3') { cmd = '3'; } //計測中でないときにモータ系へ値を送る
      else if (serialin == '4') { cmd = '4'; }
      else if (serialin == '5') {
        sign1 *= -1;
        if (digitalRead(DIR1) == HIGH) { digitalWrite(DIR1, LOW); } else if (digitalRead(DIR1) == LOW) { digitalWrite(DIR1, HIGH); }
      }
      else if (serialin == '7') { cmd = '7'; }
      else if (serialin == '8') { cmd = '8'; }
      else if (serialin == '9') {
        sign2 *= -1;
        if (digitalRead(DIR2) == HIGH) { digitalWrite(DIR2, LOW); } else if (digitalRead(DIR2) == LOW) { digitalWrite(DIR2, HIGH); }
      }

      delay(20);//このdelayの値はできる限り大きく。
    }//外側のwhileループ閉じ。
  }
