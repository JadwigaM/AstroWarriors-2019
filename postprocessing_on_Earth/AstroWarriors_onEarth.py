# Code to run on Earth - AstroPi competition 2018/2019
# program written by AstroWarriors Team from Jaslo (Poland) for
# AstroPi competition 2018/2019
# Team Members: Dawid Domaslawski, Julia Kosiek, Kinga Moskal
# Teachers: Jadwiga Moskal

#==========================================================================

### Import Modules
from Stitcher import MyStitcher

##### Import libraries ####
from time import sleep
from datetime import datetime
import sys
import re
import os
import imutils
import cv2
import numpy as np
import csv
import logging
import logzero
from logzero import logger
from matplotlib import pyplot as plt


#==========================================================================

##### Settings

# PiCamera
focus=3.60  #  focal in (mm)  (v1: 3.60;  v2: 3.04)
sensx=3.76   # sensor x (mm) (v1: 3.76;  v2:3.68)
resx=1296     # image resolution 
ImageFolder = "/home/pi/AW"

scale = 1.0 

#==========================================================================
# Saving data in csv file using Logzero
def saveDataHeader():
    """
    This function saves csv file header 
    """
    logzero.logfile("AWdata03.csv")
    formatter = logging.Formatter(' %(message)s');
    logzero.formatter(formatter)
    logger.info('timestamp, ISS hight, day/night, picname, previous picname , Delta T in sec,distance in pixels, distance in km, Velocity m/s, velocity km/h, velocity ISS' )

def save_data():
    """
    This function saves measured and calculated data in csv file using logzero library
    """
    logzero.logfile("AWdata03.csv")
    formatter = logging.Formatter('%(name)s - %(asctime)-15s - %(levelname)s: %(message)s');
    logzero.formatter(formatter)
    logger.info("%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s", timestamp, isshight, Day, picname, ppicname, DeltaT, distance_px, distance, v_iss, v_iss_km, v_iss_orbit)

saveDataHeader() 
with open('AWdata01.csv', newline='') as csvfile:
     reader = csv.DictReader(csvfile)
     
     for row in reader:
        # print(row['picname'], row['previous_picname'], row['DeltaT'], row['Day'])         
        picname = row['picname']
        ppicname = row['previous_picname']
        DeltaT = row['DeltaT']
        Day = row['Day']
        isshight = row['ISShight']
        timestamp = row['timestamp']
     
        if Day == 'Day':
            print(Day, picname, ppicname, DeltaT)
        elif Day == 'Night':
                print(Day)
        imageA = cv2.imread(picname)
        imageB = cv2.imread(ppicname)
        images = (imageB, imageA)
        #print(imageA, imageB)
     
        stitcher = MyStitcher()
        (result, vis) = stitcher.stitch([imageA, imageB], showMatches=True)
        #cv2.imwrite(os.path.splitext(ppicname)[0] + "_keypoints.jpg", vis)
        cv2.imwrite(os.path.splitext(ppicname)[0] + "_stitch.jpg", result)
        M = stitcher.getHomography()
             
        print(M)
        if (M is None):
            print("No matches found")
        else:
            sx=M[0][2]
            sy=M[1][2]
            distance_px=np.sqrt(sx**2 + sy**2)
            print("Distance in pixels:", distance_px)

            print("Distances in meters:")
            #isshight = 408*1000 #
    #    
            distance = (float(sensx)*float(isshight)/float(focus))*(float(distance_px)/float(resx)) #*fattore_di_scala
            print(distance)
                        
            # we suppose velocity is about 27563 Km/h
            if DeltaT != 0:
               v_iss = float(distance)/float(DeltaT)
            else:
               v_iss = 0
            v_iss_km = v_iss*3.6
            # Distance from the Centre of the Earth to ISS
            dist_orb = (float(distance) * (float(isshight) + 6371000))/6371000
            # velocity on the orbit in km/s
            v_iss_orbit = float(dist_orb)/float(DeltaT) * 3.6
            print("Velocity: %.3f m/s (or %.3f Km/h)" % (v_iss, v_iss*3.6))
            print('Velocity in km/h', v_iss_km)
            print('Velocity on orbit in km/h', v_iss_orbit)
        save_data()
        
