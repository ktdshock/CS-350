### Kenneth Dandrow / CS-350 / Module 7

#!/usr/bin/env python3
#
# Thermostat - This is the Python code used to demonstrate
# the functionality of the thermostat that we have prototyped throughout
# the course.
#
# This code works with the test circuit that was built for module 7.
#
# Functionality:
# (unchanged header text)
#------------------------------------------------------------------

from time import sleep
from datetime import datetime

# State machine
from statemachine import StateMachine, State

# I2C + sensor
import board
import adafruit_ahtx0

# LCD
import digitalio
import adafruit_character_lcd.character_lcd as characterlcd

# UART
import serial

# GPIO
from gpiozero import Button, PWMLED

# Threading
from threading import Thread

# math
from math import floor

DEBUG = True

# I2C
i2c = board.I2C()

# Temp/Humidity sensor
thSensor = adafruit_ahtx0.AHTx0(i2c)

# Serial port to Pi’s mini UART (matches class template)
ser = serial.Serial(
        port='/dev/ttyS0',            # /dev/ttyAMA0 prior to Pi 3
        baudrate=115200,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=1
)

# LEDs per class materials
redLight = PWMLED(18)   # HEAT indicator
blueLight = PWMLED(23)  # COOL indicator


# ---------------- Display helper ----------------
class ManagedDisplay():
    def __init__(self):
        self.lcd_rs = digitalio.DigitalInOut(board.D17)
        self.lcd_en = digitalio.DigitalInOut(board.D27)
        self.lcd_d4 = digitalio.DigitalInOut(board.D5)
        self.lcd_d5 = digitalio.DigitalInOut(board.D6)
        self.lcd_d6 = digitalio.DigitalInOut(board.D13)
        self.lcd_d7 = digitalio.DigitalInOut(board.D26)

        self.lcd_columns = 16
        self.lcd_rows = 2

        self.lcd = characterlcd.Character_LCD_Mono(
            self.lcd_rs, self.lcd_en,
            self.lcd_d4, self.lcd_d5, self.lcd_d6, self.lcd_d7,
            self.lcd_columns, self.lcd_rows
        )
        self.lcd.clear()

    def cleanupDisplay(self):
        self.lcd.clear()
        self.lcd_rs.deinit()
        self.lcd_en.deinit()
        self.lcd_d4.deinit()
        self.lcd_d5.deinit()
        self.lcd_d6.deinit()
        self.lcd_d7.deinit()

    def clear(self):
        self.lcd.clear()

    def updateScreen(self, message):
        self.lcd.clear()
        self.lcd.message = message

# init LCD
screen = ManagedDisplay()


# ---------------- Thermostat State Machine ----------------
class TemperatureMachine(StateMachine):
    "A state machine designed to manage our thermostat"

    # States
    off = State(initial=True)
    heat = State()
    cool = State()

    # Default set point (°F)
    setPoint = 72

    # OFF -> HEAT -> COOL -> OFF
    cycle = (
        off.to(heat) |
        heat.to(cool) |
        cool.to(off)
    )

    # ---- State entry/exit actions ----
    def on_enter_heat(self):
        self.updateLights()
        if(DEBUG):
            print("* Changing state to heat")

    def on_exit_heat(self):
        # stop any red fading when leaving heat
        redLight.off()

    def on_enter_cool(self):
        self.updateLights()
        if(DEBUG):
            print("* Changing state to cool")

    def on_exit_cool(self):
        # stop any blue fading when leaving cool
        blueLight.off()

    def on_enter_off(self):
        # both off
        redLight.off()
        blueLight.off()
        if(DEBUG):
            print("* Changing state to off")

    # ---- Button handlers ----
    def processTempStateButton(self):
        if(DEBUG):
            print("Cycling Temperature State")
        self.cycle()            # advance state
        self.updateLights()     # reflect immediately

    def processTempIncButton(self):
        if(DEBUG):
            print("Increasing Set Point")
        self.setPoint += 1
        self.updateLights()

    def processTempDecButton(self):
        if(DEBUG):
            print("Decreasing Set Point")
        self.setPoint -= 1
        self.updateLights()

    # ---- LED control per rubric ----
    def updateLights(self):
        # compare integer °F for stable behavior
        temp = floor(self.getFahrenheit())

        # reset both before applying new behavior
        redLight.off()
        blueLight.off()

        if(DEBUG):
            print(f"State: {self.current_state.id}")
            print(f"SetPoint: {self.setPoint}")
            print(f"Temp: {temp}")

        # OFF: both off
        if self.current_state.id == "off":
            return

        # HEAT rules
        if self.current_state.id == "heat":
            if temp < self.setPoint:
                # fading red
                redLight.pulse()          # background fade
            else:
                # solid red
                redLight.on()
            return

        # COOL rules
        if self.current_state.id == "cool":
            if temp > self.setPoint:
                # fading blue
                blueLight.pulse()
            else:
                # solid blue
                blueLight.on()
            return

    # ---- Lifecycle ----
    def run(self):
        myThread = Thread(target=self.manageMyDisplay)
        myThread.start()

    # ---- Helpers ----
    def getFahrenheit(self):
        t = thSensor.temperature
        return (((9/5) * t) + 32)

    def setupSerialOutput(self):
        # comma-delimited: state, current_temp_F, setpoint_F
        state = self.current_state.id
        temp_f = self.getFahrenheit()
        output = f"{state},{temp_f:.2f},{self.setPoint}"
        return output

    # display loop control
    endDisplay = False

    # ---- LCD + UART management thread ----
    def manageMyDisplay(self):
        counter = 1
        altCounter = 1
        while not self.endDisplay:
            if(DEBUG):
                print("Processing Display Info...")

            current_time = datetime.now()

            # Line 1: date and time (fit 16 chars)
            lcd_line_1 = current_time.strftime("%m/%d %H:%M:%S").ljust(16) + "\n"

            # Line 2 alternates between temp and state/setpoint
            if(altCounter < 6):
                temp_f = self.getFahrenheit()
                lcd_line_2 = f"Temp:{temp_f:5.1f}F".ljust(16)
                altCounter += 1
            else:
                st = self.current_state.id
                st_str = "Off" if st == "off" else ("Heat" if st == "heat" else "Cool")
                lcd_line_2 = f"{st_str} Set:{self.setPoint:02d}F".ljust(16)
                altCounter += 1
                if(altCounter >= 11):
                    # refresh LEDs ~10s for smooth operation
                    self.updateLights()
                    altCounter = 1

            # Update LCD
            screen.updateScreen(lcd_line_1 + lcd_line_2)

            # Send to server every 30 seconds
            if(DEBUG):
                print(f"Counter: {counter}")
            if((counter % 30) == 0):
                ser.write((self.setupSerialOutput() + "\n").encode("utf-8"))
                counter = 1
            else:
                counter += 1

            sleep(1)

        # Cleanup display
        screen.cleanupDisplay()

# ----- Setup machine and buttons -----
tsm = TemperatureMachine()
tsm.run()

# Buttons (per lab guide): 24 toggles mode, 25 increases, 12 decreases
greenButton = Button(24)
greenButton.when_pressed = tsm.processTempStateButton

redButton = Button(25)
redButton.when_pressed = tsm.processTempIncButton

blueButton = Button(12)
blueButton.when_pressed = tsm.processTempDecButton  # decrease setpoint

# Main loop (idle; work happens in threads/callbacks)
repeat = True
while repeat:
    try:
        sleep(30)
    except KeyboardInterrupt:
        print("Cleaning up. Exiting...")
        repeat = False
        tsm.endDisplay = True
        sleep(1)