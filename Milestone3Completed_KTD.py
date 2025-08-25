# Kenneth Dandrow / CS-350 / Module 5 - Milestone 3

from gpiozero import Button, LED
from statemachine import StateMachine, State
from time import sleep
import board
import digitalio
import adafruit_character_lcd.character_lcd as characterlcd
from threading import Thread

DEBUG = True

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
        self.lcd = characterlcd.Character_LCD_Mono(self.lcd_rs, self.lcd_en, 
                    self.lcd_d4, self.lcd_d5, self.lcd_d6, self.lcd_d7, 
                    self.lcd_columns, self.lcd_rows)
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

class CWMachine(StateMachine):
    redLight = LED(18)
    blueLight = LED(23)
    message1 = 'SOS'
    message2 = 'OK'
    activeMessage = message1
    endTransmission = False

    off = State(initial = True)
    dot = State()
    dash = State()
    dotDashPause = State()
    letterPause = State()
    wordPause = State()

    screen = ManagedDisplay()

    morseDict = {
        "A" : ".-", "B" : "-...", "C" : "-.-.", "D" : "-..",
        "E" : ".", "F" : "..-.", "G" : "--.", "H" : "....",
        "I" : "..", "J" : ".---", "K" : "-.-", "L" : ".-..",
        "M" : "--", "N" : "-.", "O" : "---", "P" : ".--.",
        "Q" : "--.-", "R" : ".-.", "S" : "...", "T" : "-",
        "U" : "..-", "V" : "...-", "W" : ".--", "X" : "-..-",
        "Y" : "-.--", "Z" : "--..", "0" : "-----", "1" : ".----",
        "2" : "..---", "3" : "...--", "4" : "....-", "5" : ".....",
        "6" : "-....", "7" : "--...", "8" : "---..", "9" : "----."
    }

    doDot = (off.to(dot) | dot.to(off))
    doDash = (off.to(dash) | dash.to(off))
    doDDP = (off.to(dotDashPause) | dotDashPause.to(off))
    doLP = (off.to(letterPause) | letterPause.to(off))
    doWP = (off.to(wordPause) | wordPause.to(off))

    def on_enter_dot(self):
        self.redLight.on()
        sleep(0.5)
        if DEBUG:
            print("* Changing state to red - dot")

    def on_exit_dot(self):
        self.redLight.off()

    def on_enter_dash(self):
        self.blueLight.on()
        sleep(1.5)
        if DEBUG:
            print("* Changing state to blue - dash")

    def on_exit_dash(self):
        self.blueLight.off()

    def on_enter_dotDashPause(self):
        sleep(0.25)
        if DEBUG:
            print("* Pausing Between Dots/Dashes - 250ms")

    def on_enter_letterPause(self):
        sleep(0.75)
        if DEBUG:
            print("* Pausing Between Letters - 750ms")

    def on_enter_wordPause(self):
        sleep(3)
        if DEBUG:
            print("* Pausing Between Words - 3000ms")

    def toggleMessage(self):
        self.activeMessage = self.message2 if self.activeMessage == self.message1 else self.message1
        if DEBUG:
            print(f"* Toggling active message to: {self.activeMessage} ")

    def processButton(self):
        print('*** processButton')
        self.toggleMessage()

    def run(self):
        myThread = Thread(target=self.transmit)
        myThread.start()

    def transmit(self):
        while not self.endTransmission:
            self.screen.updateScreen(f"Sending:\n{self.activeMessage}")
            wordList = self.activeMessage.split()
            lenWords = len(wordList)
            wordsCounter = 1
            for word in wordList:
                lenWord = len(word)
                wordCounter = 1
                for char in word:
                    morse = self.morseDict.get(char.upper(), '')
                    lenMorse = len(morse)
                    morseCounter = 1
                    for x in morse:
                        if x == '.':
                            self.doDot()
                            self.doDot()
                        elif x == '-':
                            self.doDash()
                            self.doDash()

                        if morseCounter < lenMorse:
                            self.doDDP()
                            self.doDDP()
                        morseCounter += 1

                    if wordCounter < lenWord:
                        self.doLP()
                        self.doLP()
                    wordCounter += 1

                if wordsCounter < lenWords:
                    self.doWP()
                    self.doWP()
                wordsCounter += 1

        self.screen.cleanupDisplay()

cwMachine = CWMachine()
cwMachine.run()

greenButton = Button(24)
greenButton.when_pressed = cwMachine.processButton

repeat = True
while repeat:
    try:
        if DEBUG:
            print("Killing time in a loop...")
        sleep(20)
    except KeyboardInterrupt:
        print("Cleaning up. Exiting...")
        repeat = False
        cwMachine.endTransmission = True
        sleep(1)