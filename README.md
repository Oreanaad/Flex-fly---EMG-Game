# 🐥 Flex & Fly: EMG Challenge
**Bionic Rehabilitation System via Electromyography (EMG)**

Flex & Fly is a gamified biofeedback tool designed for muscle strengthening and neuromuscular rehabilitation. The system translates muscle activity (EMG signals) into real-time character movement, providing patients with an engaging way to perform repetitive physical therapy exercises.

---

## 🛠 Hardware Requirements
To use the system with real biological signals, the following components are required:

* **Microcontroller:** Arduino Uno / Nano / Mega.
* **Sensor:** EMG Sensor (e.g., MyoWare, AD8232, or similar).
* **Electrodes:** 3 Surface electrodes (2 for the muscle belly, 1 for reference/ground).
* **Connection:** USB Cable to PC.

### Wiring Diagram
1.  Connect the **Signal Output** of the EMG sensor to **Analog Pin A0** on the Arduino.
2.  Connect **VCC** to 5V and **GND** to Ground.
3.  Place electrodes on the target muscle (e.g., Forearm Flexors).



---

## 💻 Software Setup

### For Developers (Running from Source)
1.  Ensure you have **Python 3.8+** installed.
2.  Install the required libraries:
    ```bash
    pip install pygame pyserial
    ```
3.  Clone this repository and run:
    ```bash
    python main.py
    ```

### For Users / Doctors (Running the Executable)
1.  Navigate to the `dist/` folder.
2.  Run `FlexAndFly_EMG.exe`.
3.  *Note:* If no Arduino is detected, the game will automatically enable **Keyboard Mode** (Use LEFT/RIGHT arrows).

---

## 🎮 How to Play

1.  **Calibration:** When the game starts, follow the on-screen instructions to calibrate your **Maximum Voluntary Contraction (MVC)**. This ensures the difficulty is tailored to your current strength.
2.  **Objective:** Move the chicken to catch the pink worms (+1 point).
3.  **Avoid Obstacles:** Watch out for falling rocks!
    * **0-25 points:** Training zone (No rocks).
    * **25-50 points:** Low difficulty (Few rocks).
    * **50+ points:** Progressive challenge.
4.  **Reward:** Reach 25 points to trigger a success celebration!

---

## 📝 Arduino Firmware
Upload this code to your Arduino before starting the game:

```cpp
void setup() {
  Serial.begin(9600);
}

void loop() {
  int sensorValue = analogRead(A0);
  Serial.println(sensorValue);
  delay(10); 
}