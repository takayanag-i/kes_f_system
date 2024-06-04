// タスクハンドルとキューの定義
TaskHandle_t taskHandles[2];
QueueHandle_t motorQueue;

// ピンの定義
const uint8_t DIR1_PIN = 18;
const uint8_t STEP1_PIN = 19;
const uint8_t DIR2_PIN = 23;
const uint8_t STEP2_PIN = 22;
const uint8_t PICO_PIN = 2;

// モーター制御の状態
int motor1Direction = 1;
int motor2Direction = 1;
volatile float motor1Position = 0.0;
volatile float motor2Position = 0.0;

// シリアル入力のバッファ
volatile uint8_t serialInput;
volatile uint8_t motorCommand;

// 高精度なタイマー関数
void preciseDelayMicroseconds(unsigned int us) {
  unsigned long start = micros();
  while (micros() - start < us) {
    // Busy-wait loop
  }
}

void setup() {
  delay(100);
  motorCommand = '0';
  Serial.begin(115200);
  analogSetAttenuation(ADC_6db);

  pinMode(DIR1_PIN, OUTPUT);
  pinMode(STEP1_PIN, OUTPUT);
  pinMode(DIR2_PIN, OUTPUT);
  pinMode(STEP2_PIN, OUTPUT);
  pinMode(PICO_PIN, OUTPUT);

  digitalWrite(DIR1_PIN, HIGH);
  digitalWrite(STEP1_PIN, LOW);
  digitalWrite(DIR2_PIN, HIGH);
  digitalWrite(STEP2_PIN, LOW);
  digitalWrite(PICO_PIN, LOW);

  motorQueue = xQueueCreate(10, sizeof(char));

  xTaskCreatePinnedToCore(serialTask, "SerialTask", 4096, NULL, 3, &taskHandles[0], 0);
  xTaskCreatePinnedToCore(motorTask, "MotorTask", 4096, NULL, 1, &taskHandles[1], 1);
}

void loop() {
  // メインループは空のままにして、すべての処理をタスクに任せる
}

void serialTask(void *args) {
  while (1) {
    if (Serial.available() > 0) {
      serialInput = Serial.read();
      if (serialInput >= '0' && serialInput <= '9') {
        if (xQueueSend(motorQueue, &serialInput, portMAX_DELAY) != pdPASS) {
          Serial.println("Error: Queue full, command not sent");
        }
      }
    }
    delay(20); // ウォッチドッグタイマー対策のためのディレイ
  }
}

void motorTask(void *args) {
  char command;
  while (1) {
    if (xQueueReceive(motorQueue, &command, portMAX_DELAY) == pdPASS) {
      handleMotorCommand(command);
    }
    vTaskDelay(1 / portTICK_PERIOD_MS);
  }
}

void handleMotorCommand(char command) {
  switch (command) {
    case '0':
      sendMotorPositions();
      break;
    case '1':
      // 何もしない、終了条件
      break;
    case '3':
      motorCommand = '3';
      controlMotor1();
      break;
    case '4':
      motorCommand = '4';
      break;
    case '5':
      toggleMotorDirection1();
      break;
    case '7':
      motorCommand = '7';
      controlMotor2();
      break;
    case '8':
      motorCommand = '8';
      break;
    case '9':
      toggleMotorDirection2();
      break;
    default:
      Serial.println("Error: Invalid command received");
  }
}

void controlMotor1() {
  while (motorCommand == '3') {
    digitalWrite(STEP1_PIN, HIGH);
    preciseDelayMicroseconds(2250);
    digitalWrite(STEP1_PIN, LOW);
    motor1Position += 0.005 * motor1Direction;
    preciseDelayMicroseconds(2250);
  }
}

void controlMotor2() {
  while (motorCommand == '7') {
    digitalWrite(STEP2_PIN, HIGH);
    preciseDelayMicroseconds(2250);
    digitalWrite(STEP2_PIN, LOW);
    motor2Position += 0.005 * motor2Direction;
    preciseDelayMicroseconds(2250);
  }
}

void toggleMotorDirection1() {
  motor1Direction *= -1;
  if (digitalRead(DIR1_PIN) == HIGH) {
    digitalWrite(DIR1_PIN, LOW);
  } else {
    digitalWrite(DIR1_PIN, HIGH);
  }
}

void toggleMotorDirection2() {
  motor2Direction *= -1;
  if (digitalRead(DIR2_PIN) == HIGH) {
    digitalWrite(DIR2_PIN, LOW);
  } else {
    digitalWrite(DIR2_PIN, HIGH);
  }
}

void sendMotorPositions() {
  unsigned long timestamp = micros();
  Serial.print(motor1Position);
  Serial.print(',');
  Serial.print(motor2Position);
  Serial.print(',');
  Serial.println(timestamp);
  digitalWrite(PICO_PIN, HIGH);
  delay(10);
  digitalWrite(PICO_PIN, LOW);
}
