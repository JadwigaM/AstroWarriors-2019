# program written by Turtlez Team from Jaslo (Poland) for
# AstroPi competition 2018/2019
# Team Members: Dawid Domaslawski, Julia Kosiek, Kinga Moskal
# Teachers: Jadwiga Moskal

import math
import time
import picamera
import PIL
import datetime
import os
import random
from sense_hat import SenseHat
import ephem
from fractions import Fraction
from picamera import PiCamera
from PIL import Image
import shutil
from time import sleep
import reverse_geocoder as rg
import numpy as np
from matplotlib import pyplot as plt
import cv2
import logging
import logzero
from logzero import logger
from sense_hat import SenseHat
import os

sense = SenseHat()
camera=PiCamera()


sense.clear();
i=0
licznik = 0
picname = "PL_AstroWarriors_"

# LED Matrix definitions: 
b = (60, 50, 0) #brown
y = (105, 105, 5) #yellow
p = (105, 105, 105) #white
k = (0, 0, 0)
r = (50, 0, 0)
blue = (0, 0, 105)
green = (0, 50, 0)
greenf = (0, 25, 5)

# main picture
A1 = [
    r,r,r,r,r,r,r,r,
    k,k,k,k,k,k,k,k,
    k,k,k,k,k,k,k,k,
    k,k,k,k,k,k,k,k,
    k,k,k,k,k,k,k,k,
    k,k,k,k,k,k,k,k,
    k,k,k,k,k,k,k,k,
    green,greenf,greenf,greenf,greenf,greenf,greenf,green,
    ]
# taking daylight picture
A2 = [
    r,r,r,r,r,r,r,r,
    k,k,k,y,k,k,k,k,
    k,k,k,y,k,k,k,k,
    k,k,k,y,k,k,k,k,
    y,y,y,y,k,k,k,k,
    y,k,k,y,k,k,k,k,
    y,k,k,y,k,k,k,k,
    y,y,y,y,k,k,k,k,
    ]
#taking picture at night
A3 = [
   r,r,r,r,r,r,r,r,
    k,k,k,k,k,k,k,k,
    b,k,k,k,k,b,k,k,
    b,b,k,k,k,b,k,k,
    b,k,b,k,k,b,k,k,
    b,k,k,b,k,b,k,k,
    b,k,k,k,b,b,k,k,
    b,k,k,k,k,b,k,k,
    ]




def timestamp():
    """
    This function takes time and date for use in csv file (time_stamp) and in picture names (timestamp1)
    """
    global time_stamp, timestamp1
    time_stamp= ""
    time_stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    timestamp1 = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
   


def get_sense_data():
    """
    This function gets data from Sense Hat, corrected temperature is calculated using CPU temperatura, temperature from humidity, and temperature from pressure sensors
    """
    global sense_data
    sense_data=[]
   
    sense_data.append(sense.get_temperature_from_humidity())
    sense_data.append(sense.get_temperature_from_pressure())
    sense_data.append(sense.get_humidity())
    sense_data.append(sense.get_pressure())

 # temperature corrected
    t = os.popen('vcgencmd measure_temp')
    cputemp = t.readline()
    cputemp = cputemp.replace('temp=','')
    cputemp = cputemp.replace("'C\n","")
    cputemp = float(cputemp)             
    temperature = sense.get_temperature()
    tempp = sense.get_temperature_from_pressure()
    temph = sense.get_temperature_from_humidity()
    temperatc = ((temperature + tempp + temph)/3) - (cputemp/5)
    sense_data.append(temperatc)
   


    o = sense.get_orientation()
    yaw = o["yaw"]
    pitch = o["pitch"]
    roll = o["roll"]
    sense_data.extend([pitch,roll,yaw])

    mag = sense.get_compass_raw()
    mag_x = mag["x"]
    mag_y = mag["y"]
    mag_z = mag["z"]
    sense_data.extend([mag_x,mag_y,mag_z])
    
    acc = sense.get_accelerometer_raw()
    x = acc["x"]
    y = acc["y"]
    z = acc["z"]
    sense_data.extend([x,y,z])
    
    gyro = sense.get_gyroscope_raw()
    gyro_x = gyro["x"]
    gyro_y = gyro["y"]
    gyro_z = gyro["z"]

    
    sense_data.extend([gyro_x,gyro_y,gyro_z])

    
    return sense_data
    
    
    
def nightexp(): # night exposures (high ISO, long shutter exposures)
    """
    This function takes pictures at night. (ISO = 400, 2 seconds exposures), puts ISS coordinates into EXIF tags, names picture files
    """
    global licznik, picname, picname_previous, timestamp_prev, deltat
    if dn == 'Night':
        sense.set_pixels(A3)
        camera.resolution = (1296,972)
        
        shut = 2 * 1000 * 1000
        
        camera.framerate = 1
        camera.shutter_speed = shut       
        camera_iso=400
        time.sleep(4)
        camera.exposure_mode ="off"
        # fixing the auto white balance gains at their current values
        g = camera.awb_gains
        camera.awb_mode = "off"
        camera.awb_gains = g
        
        camera.framerate = 1
        camera.shutter_speed = 3 * 1000 * 1000
        #camera.iso = 400
        picname_previous = picname
        camera_abw_gains = (1, 1)
        gain = camera_abw_gains
       
        #camera.annotate_text = "PL_AstroWarriors_" + timestamp + " " + latlong +  " " + str(lok1) + " " + dn
        #camera.annotate_text_size = 10
        picname = "PL_AstroWarriors_" + timestamp1 + ".jpg"
        long_value = [float(i) for i in str(obslong).split(":")]
        
        if long_value[0] < 0:

            long_value[0] = abs(long_value[0])
            camera.exif_tags['GPS.GPSLongitudeRef'] = "W"
        else:
            camera.exif_tags['GPS.GPSLongitudeRef'] = "E"
            camera.exif_tags['GPS.GPSLongitude'] = '%d/1,%d/1,%d/10' % (long_value[0], long_value[1], long_value[2]*10)

        lat_value = [float(i) for i in str(obslat).split(":")]

        if lat_value[0] < 0:

            lat_value[0] = abs(lat_value[0])
            camera.exif_tags['GPS.GPSLatitudeRef'] = "S"
        else:
            camera.exif_tags['GPS.GPSLatitudeRef'] = "N"

            camera.exif_tags['GPS.GPSLatitude'] = '%d/1,%d/1,%d/10' % (lat_value[0], lat_value[1], lat_value[2]*10)
        camera.capture(picname)
        deltata = datetime.datetime.now() - timestamp_prev
        deltat = deltata.seconds + deltata.microseconds / 1000000
        
        timestamp_prev = datetime.datetime.now() 
        
def dayexp(): # daylight exposures, auto
    """
    This function takes pictures at day. (ISO = automatic, automatic exposures), puts ISS coordinates into EXIF tags, names picture files
    and calculates intervals between pictures
    """
    global picname, picname_previous, timestamp_prev, deltat
    if dn == 'Day':
        
        sense.set_pixels(A2)
        time.sleep(2)
        picname_previous = picname
        camera.resolution = (1296,972)
        camera.exposure_mode ="auto"
        camera.framerate =30       #   default
        camera.shutter_speed = 0   #   0 = auto
        camera.iso = 0             #   0 = auto 
        
        picname = "PL_AstroWarriors_" + timestamp1 + ".jpg"
        long_value = [float(i) for i in str(obslong).split(":")]
        
        if long_value[0] < 0:

            long_value[0] = abs(long_value[0])
            camera.exif_tags['GPS.GPSLongitudeRef'] = "W"
        else:
            camera.exif_tags['GPS.GPSLongitudeRef'] = "E"
            camera.exif_tags['GPS.GPSLongitude'] = '%d/1,%d/1,%d/10' % (long_value[0], long_value[1], long_value[2]*10)

        lat_value = [float(i) for i in str(obslat).split(":")]

        if lat_value[0] < 0:

            lat_value[0] = abs(lat_value[0])
            camera.exif_tags['GPS.GPSLatitudeRef'] = "S"
        else:
            camera.exif_tags['GPS.GPSLatitudeRef'] = "N"

            camera.exif_tags['GPS.GPSLatitude'] = '%d/1,%d/1,%d/10' % (lat_value[0], lat_value[1], lat_value[2]*10)
          
        camera.capture(picname)
        deltata = datetime.datetime.now() - timestamp_prev
        deltat = deltata.seconds + deltata.microseconds / 1000000
        timestamp_prev = datetime.datetime.now() 
        


def isstrack(): # picture coordinates
    """
    This function calculates data of pictures (coordinates, ISS Hight above Earth surface, nearest city, country) by using pyephem and reverse-geocoder libraries
    """
    global obslat, obslong, dn, latlong, country, admin, city, lok1, hight
    # ISS TLE DATE 02 02 2019
    name = "ISS (ZARYA)";            
    line1 = "1 25544U 98067A   19033.27351531  .00001422  00000-0  29623-4 0  9998";
    line2 = "2 25544  51.6433 312.1797 0005043 343.6440 154.8135 15.53218636154298";
    #name = "ISS (ZARYA)";
    #line1 = "1 25544U 98067A   19005.61356139  .00000823  00000-0  19904-4 0  9999";
    #line2 = "2 25544  51.6413  89.9292 0002334 242.7730 266.4664 15.53733672149996";
   
    iss = ephem.readtle(name,line1,line2)
    iss.compute()
   
     
    obs = ephem.Observer()
   
    sun = ephem.Sun() # Imports ephem's sun as sun
    twilight = math.radians(-7)
    obs.lat = iss.sublat
    obs.long = iss.sublong
    hight = iss.elevation
    obslat = obs.lat
    obslong = obs.long
    obs.elevation = 0
    sun.compute(obs)
    sun_angle = math.degrees(sun.alt)
    
    # Day or Night calculating
    dn = 'Day' if sun_angle > twilight else 'Night'
   
    latlong = ("Lat %s - Long %s" % (iss.sublat, iss.sublong))
  
    
    # Searching data of site under ISS
    colat = np.rad2deg(iss.sublat)
    colong = np.rad2deg(iss.sublong)
    coordinates = (colat, colong)
     
    results = rg.search(coordinates, mode=1)
    

    country = [row['cc'] for row in results]
    city = ([row['name'] for row in results])
    admin = ([row['admin1'] for row in results])
    lokalizacja = country + city + admin
    lok1 = ' '.join(lokalizacja)
    

# Saving data in csv file using Logzero
def saveDataHeader():
    """
    This function saves csv file header 
    """
    logzero.logfile("data01.csv")
    formatter = logging.Formatter(' %(message)s');
    logzero.formatter(formatter)
    get_sense_data()
    output_string = ",".join(str(value) for value in sense_data)
    logger.info('lat-long,ISS hight, day/night, timestamp, localization , picname, previous picname , Delta T in sec, temperature_from_humidity, temperature_from_pressure, humidity, pressure, corrected temperature, yaw, pitch, roll mag_x,mag_y,mag_z, acc_x,acc_y,acc_z, gyro_x,gyro_y,gyro_z]'  )

def save_data():
    """
    This function saves measured and calculated data in csv file using logzero library
    """
    logzero.logfile("data01.csv")
    formatter = logging.Formatter('%(name)s - %(asctime)-15s - %(levelname)s: %(message)s');
    logzero.formatter(formatter)
    get_sense_data()
    output_string = ",".join(str(value) for value in sense_data)
    logger.info("%s,%s,%s,%s,%s,%s,%s,%s,%s", str(latlong),hight, dn, time_stamp, lok1 , picname, picname_previous ,deltat, output_string  )


    
#main loop
    
sense.show_message("Starting!", scroll_speed=(0.08))
start_time = datetime.datetime.now()

# create a datetime variable to store the current time
now_time = datetime.datetime.now()

# timestamp_prev for first use
timestamp_prev = datetime.datetime.now()
saveDataHeader() 

while (now_time < start_time + datetime.timedelta(minutes=170)):

    try:
        i=i+1
        sense.set_pixels(A1)
        time.sleep(3)
        isstrack()
        timestamp()
        if dn == 'Night':
            nightexp()
        else:
            dayexp()
        save_data()
        now_time = datetime.datetime.now()
    except Exception as e:
        logger.error("An error occurred: " + str(e))
sense.show_message("Ending!", scroll_speed=(0.08))
