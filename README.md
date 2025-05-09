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
Python 3.13.2
Pygame
PySerial

To install dependencies:
pip install pygame
pip install pyserial
Arduino-side:
Arduino UNO or compatible board

RGB LED

Resistors (220Ω recommended)

Jumper wires

Breadboard

Arduino Circuit
You can view the complete wiring and Arduino setup using Tinkercad:
🔗 [https://www.tinkercad.com/things/hXAUeezIRJF-rgb-connection](https://www.tinkercad.com/things/hXAUeezIRJF-rgb-connection)

![image](https://github.com/user-attachments/assets/d1918112-5569-448e-9de1-208691c9772b)


How It Works
The game sends signals over the serial port based on its current state.

The Arduino listens for these signals (e.g., "menu", "play", "gameover").

Depending on the received command, the Arduino sets the RGB LED to a specific color.

Setup
1. Upload the Arduino Sketch
Ensure your Arduino board is connected and upload the appropriate sketch (provided in the Tinkercad project or as a .ino file in this repository).

2. Run the Game
Ensure the correct serial port is selected in your Python code (e.g., COM5 for Windows or /dev/ttyUSB0 for Linux/macOS).
Then run the game

Disclaimer
This project is the result of the "Algorithm Design" laboratory, part of the Faculty of Automation, Computers, and Electronics at the University of Craiova. For more information about the faculty, visit:
🔗 http://ace.ucv.ro/
