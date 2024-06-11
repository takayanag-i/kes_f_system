// Multi-threaded task handles
TaskHandle_t thp[2];
const uint8_t DIR1 = 18;
const uint8_t STEP1 = 19;
const uint8_t DIR2 = 23;
const uint8_t STEP2 = 22;

volatile float disp1 = 0.0;
volatile float disp2 = 0.0;
volatile uint8_t cmd;
volatile int8_t sign1 = 1; // Initial direction is clockwise.;
volatile int8_t sign2 = 1; // Initial direction is clockwise.;

void handleSerialInput(uint8_t input) {
    switch (input) {
        case '3':
            cmd = '3';
            break;
        case '4':
            cmd = '4';
            break;
        case '5':
            sign1 *= -1;
            digitalWrite(DIR1, digitalRead(DIR1) == HIGH ? LOW : HIGH);
            break;
        case '7':
            cmd = '7';
            break;
        case '8':
            cmd = '8';
            break;
        case '9':
            sign2 *= -1;
            digitalWrite(DIR2, digitalRead(DIR2) == HIGH ? LOW : HIGH);
            break;
        default:
            break;
    }
}

void sendSerialData() {
    unsigned long tm = micros();
    digitalWrite(2, HIGH);
    Serial.print(disp1);
    Serial.print(',');
    Serial.print(disp2);
    Serial.print(',');
    Serial.println(tm);
    digitalWrite(2, LOW);
}

void setup() {
    delay(100);
    cmd = '0';
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
    pinMode(2, OUTPUT); // For Pico
    digitalWrite(2, LOW);
    xTaskCreatePinnedToCore(Core0a, "Core0a", 4096, NULL, 3, &thp[0], 0);
    xTaskCreatePinnedToCore(Core1b, "Core1b", 4096, NULL, 1, &thp[1], 1);
}

void loop() {
    if (cmd == '3') {
        while (true) {
            digitalWrite(STEP1, HIGH);
            delayMicroseconds(2250);
            digitalWrite(STEP1, LOW);
            disp1 += 0.005 * sign1;
            delayMicroseconds(2250);
            if (cmd == '4') {
                break;
            }
        }
    }
    delay(1);
}

void Core1b(void *args) {
    while (true) {
        if (cmd == '7') {
            while (true) {
                digitalWrite(STEP2, HIGH);
                delayMicroseconds(2250);
                digitalWrite(STEP2, LOW);
                disp2 += 0.005 * sign2;
                delayMicroseconds(2250);
                if (cmd == '8') {
                    break;
                }
            }
        }
        delay(1);
    }
}

void Core0a(void *args) {
    while (true) {
        if (Serial.read() == '0') {
            while (true) {
                delay(10);
                sendSerialData();

                char input = Serial.read();
                if (input == '1') {
                    break;
                } else {
                    handleSerialInput(input);
                }
            }
        } else {
            handleSerialInput(Serial.read());
        }

        delay(20);
    }
}
