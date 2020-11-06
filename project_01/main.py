"""
--------------------------------------------------------------------------
Plant Water & Sunlight Text Reminder with Display
--------------------------------------------------------------------------
License:   
Copyright 2020 Fernanda Lago

Redistribution and use in source and binary forms, with or without 
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this 
list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, 
this list of conditions and the following disclaimer in the documentation 
and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its contributors 
may be used to endorse or promote products derived from this software without 
specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE 
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE 
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE 
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL 
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR 
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER 
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, 
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE 
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
--------------------------------------------------------------------------
Software API:
    
    * Adafruit Circuit Python
        * used to interface ILI9341 LCD Screen with PocketBeagle
    * Adafruit_Blinka
        * used for circuit python to then use digitalio
  
--------------------------------------------------------------------------
Background Information: 
 
    * Base code/instructions for Display:
        * https://github.com/adafruit/Adafruit_CircuitPython_Bitmap_Font/
        
    * Base code/instructions for texting:
        * https://www.digikey.com/en/articles/how-to-make-a-beaglebone-based-appliance-notification-texter
--------------------------------------------------------------------------
Outline:
    
    - Set up the PocketBeagle, LCD screen, texting interface, light sensors, humidity sensor, and WIFI adapter
    - Set your email, password, and phone number below
    - Use the functions to gather the necessary data
        - Based on data, user may receive a text to remind them to water plant or to notify them about sunlight level
        - Display will output text regarding status of plant
        
"""

#Import necessary libraries for LCD Screen

import os
import digitalio
import board
from board import SCL, SDA
import busio
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import displayio
import adafruit_ili9341
import Adafruit_BBIO.SPI as SPI
import terminalio
import adafruit_display_text
from adafruit_display_text import label
from adafruit_bitmap_font import bitmap_font

#Import necessary libraries for sending texts

import json 
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

#Import necessary libraries for light sensors

import Adafruit_BBIO.GPIO as GPIO
import Adafruit_BBIO.ADC as ADC
import Adafruit_BBIO.PWM as PWM

#Import necessary libraries for soil humidity sensor

from adafruit_seesaw.seesaw import Seesaw
i2c_bus = busio.I2C(SCL, SDA)

#Set up LCD Display SPI Bus

from Adafruit_BBIO.SPI import SPI
spi = board.SPI()

#Define the CS, DC, and Reset pins

tft_cs = board.P2_2
tft_dc = board.P2_4

# Create the display

displayio.release_displays()
display_bus = displayio.FourWire(spi, command=tft_dc, chip_select=tft_cs)

display = adafruit_ili9341.ILI9341(display_bus, width=320, height=240)

#Set up ADC

analog_in_1="P1_19"
analog_in_2="P1_21"

ADC.setup()

# ------------------------------------------------------------------------------
# Set email, password, and phone number (go to https://www.digikey.com/en/articles/how-to-make-a-beaglebone-based-appliance-notification-texter
# to look up structure for your phone number depending on your wireless provider)
# ------------------------------------------------------------------------------

email = " "

password = " "

phone_number = " "
                            
# ------------------------------------------------------------------------------
# Functions
# ------------------------------------------------------------------------------
  
def choosewords():
    """
    Designates which words to display based on status of sunlight and water in plant
    """
    water = soilcheck()
    light =  lightcheck()
    if water == "adequate" and light == "medium":
        string = "Your plant is happy :D\n\nSunlight Level: Medium\n\nWater Level: Adequate"
    elif water == "inadequate" and light == "medium":
        string = "Your plant needs water!\n\nSunlight Level: Medium\n\nWater Level: Inadequate"
    elif water == "adequate" and light == "low":
        string = "Your plant needs more sun!\n\nSunlight Level: Low\n\nWater Level: Adequate"
    elif water == "adequate" and light == "high":
        string = "Your plant needs less sun!\n\nSunlight Level: High\n\nWater Level: Adequate"
    elif water == "inadequate" and light == "low":
        string = "Your plant needs water\n       and more sun!\n\nSunlight Level: Low\n\nWater Level: Inadequate"
    elif water == "inadequate" and light == "high": 
        string = "Your plant needs water\n       and less sun!\n\nSunlight Level: High\n\nWater Level: Inadequate"
    else:
        print(water)
        print(light)
    displaywords(string)
    print(string)
        
    
def soilcheck():
    """
    Uses soil humidity sensor to get reading of 
    humidity and designates whether humidity is at adequate or inadequate level
    """
    i2c_bus = busio.I2C(SCL, SDA)

    ss = Seesaw(i2c_bus, addr=0x36)
        # read moisture level through capacitive touch pad
    touch = ss.moisture_read()
    if touch < 580:
        water = "inadequate"
    else:
        water = "adequate"
    print("  moisture: " + str(water))
    sendtextwater(water)
    
    return(water)
    

def lightcheck():
    """
    Uses both light sensors to get voltage reading, then averages them to categorize light level as 
    low, medium, or high
    """
    analog_in_1="P1_19"
    analog_in_2="P1_21"
    ADC.setup()
    value1 = ADC.read_raw(analog_in_1)
    value2 = ADC.read_raw(analog_in_2)
    avgvalue = (value1 + value2)/2
    if avgvalue > 2000:
        light = "high"
    elif avgvalue <= 2000 and avgvalue >= 1000:
        light = "medium"
    else:
        light = "low"
    print(avgvalue)
    print("  light: " + str(light))
    sendtextlight(light)
    
    return(light)


def sendtextwater(moisture):
    """
    Sends text to user if plant needs water
    """
    email = 'ferlago507@gmail.com' # Your email
    password = 'FerLake507!' # Your email account password
    #send_to_email = "6303379642@txt.att.net" # Who you are sending the message to
    send_to_email = "9544392352@txt.att.net"
    message = 'Your plant needs water!' # The message in the email
    if moisture == "inadequate":
        server = smtplib.SMTP('smtp.gmail.com', 587) # Connect to the server
        server.starttls() # Use TLS
        server.login(email, password) # Login to the email server
        server.sendmail(email, send_to_email , message) # Send the email
        server.quit() 
        print(message)
    elif moisture == "adequate":
        print("water level adequate")
    else:
        print(moisture)
        
        
def sendtextlight(level, email, password, phone_number):
    """
    Sends text to user if plant is getting too little or too much sun
    """
    email1 = email # Your email
    password1 = password # Your email account password
    #send_to_email = # Who you are sending the message to
    send_to_email = phone_number
    message1 = 'Your plant is receiving too much sunlight!' # The message in the email
    message2 = 'Your plant is not receiving enough sunlight!'
    if level == "high":
        server = smtplib.SMTP('smtp.gmail.com', 587) # Connect to the server
        server.starttls() # Use TLS
        server.login(email, password) # Login to the email server
        server.sendmail(email, send_to_email , message1) # Send the email
        server.quit() 
        print(message1)
    elif level == "medium":
        print('medium level light')
    elif level == "low":
        server = smtplib.SMTP('smtp.gmail.com', 587) # Connect to the server
        server.starttls() # Use TLS
        server.login(email, password) # Login to the email server
        server.sendmail(email, send_to_email ,message2) # Send the email
        server.quit() # Logout of the email server
        print(message2)
    else:
        print("level")
        

def displaywords(words):
    """
    Displays words on LCD Screen based on sunlight and water status of the plant
    """
    spi = board.SPI()
    tft_cs = board.P2_2
    # Create the display
    displayio.release_displays()
    display_bus = displayio.FourWire(spi, command=tft_dc, chip_select=tft_cs)
    
    display = adafruit_ili9341.ILI9341(display_bus, width=320, height=240)
    splash = displayio.Group(max_size=10)
    display.show(splash)
    
    color_bitmap = displayio.Bitmap(320, 240, 1)
    color_palette = displayio.Palette(1)
    color_palette[0] = 0x339933
    bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
    splash.append(bg_sprite)
    font = bitmap_font.load_font("Helvetica-Bold-16.bdf")
    color = 0xFFFFFF
    text_area = label.Label(font, text=words, color=color)
    text_area.x = 75
    text_area.y = 70
    splash.append(text_area)
    while True:
        pass
        

#-------------------------------------------------------------------------------
# Main Script
#-------------------------------------------------------------------------------

if __name__ == '__main__':

    try:
        choosewords()
    except Exception as e:
        if type(e) is KeyboardInterrupt:
            pass
        else:
        #catches error if not connected to wifi or not able to log in to email, output red screen
            spi = board.SPI()
            tft_cs = board.P2_2
            # Create the display
            displayio.release_displays()
            display_bus = displayio.FourWire(spi, command=tft_dc, chip_select=tft_cs)
            
            display = adafruit_ili9341.ILI9341(display_bus, width=320, height=240)
            splash = displayio.Group(max_size=10)
            display.show(splash)
            
            color_bitmap = displayio.Bitmap(320, 240, 1)
            color_palette = displayio.Palette(1)
            color_palette[0] = 0xFF0000
            bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
            splash.append(bg_sprite)
