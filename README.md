**CS-350 Portfolio Reflection**

 - Summary of the Projects

The first artifact I selected is my Module 5: Milestone 3 project, where I programmed a Raspberry Pi to flash Morse code messages using red and blue LEDs. 
The system used a state machine to control the LED timing, incorporated a button to toggle between two messages, and displayed the active message on a 16x2 LCD. 
This project solved the problem of controlling hardware outputs in a timed sequence and demonstrated how to synchronize hardware with user inputs.

The second artifact is my Final Project: Thermostat Lab, which expanded hardware control into a more complex embedded system. 
In this project, I built a smart thermostat prototype that used a temperature sensor, LEDs to indicate heating and cooling, buttons to adjust the set point and modes, an LCD to show real-time data, and UART to simulate sending information to a server. 
This solved the problem of creating a working embedded thermostat prototype while also exploring future cloud-connected architectures.


 - What I Did Well

I did well in implementing state machines for both projects. The Morse code project showed I could design smooth state transitions for LEDs and timing, while the thermostat project highlighted my ability to manage multiple states (off, heat, cool) with button inputs. 
I also feel I did well in integrating different hardware peripherals, such as I2C sensors, GPIO interrupts, LCD displays, and UART communication.


 - Where I Could Improve

One area for improvement is writing cleaner, more modular code. In both projects, some functions could have been broken down into smaller reusable pieces to reduce duplication. 
I also could improve the documentation and inline comments so someone unfamiliar with the hardware setup could follow my work more easily.


 - Tools and Resources I Added to My Support Network

I expanded my support network with resources such as the RPi.GPIO and gpiozero libraries, the Adafruit CircuitPython libraries for sensors and LCDs, and tutorials from Raspberry Pi and Adafruit. 
I also relied on online forums and the official documentation for debugging hardware issues, which will continue to support me in future embedded projects.

 - Transferable Skills

From these projects, I gained several transferable skills:

  Designing and implementing state machines to manage hardware behavior.

  Debugging and integrating hardware/software systems, such as sensors, LEDs, and displays.

  Understanding how hardware architecture decisions affect performance, maintainability, and future scalability.

  Applying interrupt-driven programming with GPIO buttons.

These skills can be applied in embedded systems, IoT devices, robotics, and even larger-scale software engineering projects.

 - Making the Projects Maintainable, Readable, and Adaptable

I focused on readability by using clear variable names, organizing code into logical sections, and applying consistent formatting. 
I separated setup code from the main logic so the projects could be easily adapted—for example, to change Morse code messages or thermostat set points without rewriting the program. 
The use of classes for the display and state machines also makes the projects more modular and adaptable for future changes.
