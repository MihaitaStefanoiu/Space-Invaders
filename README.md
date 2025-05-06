RGB LED Game Integration with Arduino and Python (Pygame)
Overview
This project is a fully functional game developed in Python using the Pygame library. It integrates with an Arduino board via PySerial, enabling real-time feedback using an RGB LED. The LED changes color based on the current state of the game, offering a more immersive experience.

Features
🎮 Game built entirely with Python and Pygame

🔌 Serial communication with Arduino using PySerial

🌈 RGB LED changes color depending on the game state:

Menu: Blue

Playing: Green

Game Over: Red

Requirements
Python-side:
Python 3.x

Pygame

PySerial

To install dependencies:

bash
Copy
Edit
pip install pygame pyserial
Arduino-side:
Arduino UNO or compatible board

RGB LED

Resistors (220Ω recommended)

Jumper wires

Breadboard

Arduino Circuit
You can view the complete wiring and Arduino setup using Tinkercad:
🔗 [https://www.tinkercad.com/things/hXAUeezIRJF-rgb-connection](https://www.tinkercad.com/things/hXAUeezIRJF-rgb-connection)

How It Works
The game sends signals over the serial port based on its current state.

The Arduino listens for these signals (e.g., "menu", "play", "gameover").

Depending on the received command, the Arduino sets the RGB LED to a specific color.

Setup
1. Upload the Arduino Sketch
Ensure your Arduino board is connected and upload the appropriate sketch (provided in the Tinkercad project or as a .ino file in this repository).

2. Run the Game
Ensure the correct serial port is selected in your Python code (e.g., COM5 for Windows or /dev/ttyUSB0 for Linux/macOS).
Then run the game:

bash
Copy
Edit
python game.py
