# AstroWarriors-2019
Astro Pi competition 2018/20198

Team Astro Warriors from Jaslo, Poland


Our goal is to study the speed of a space station in orbit by analyzing the images taken with the camera facing the Earth every 8 seconds and comparing our results with the actual speed of the station. We will also conduct measurements to detect possible station correction maneuvers.
As the camera will also take pictures of the unlit (night) part of the Earth, we want to check whether with long exposured times and high ISO values we will be able to see the city lights.

We will use the NoIR camera, accelerometer, gyroscope and LED matrix. Using the PyEphem module, we will get the location of the station with its height and information on whether they will find pictures
Earth's daytime and nighttime areas. The photos will be marked with timestamp, additionally the coordinates will be saved in exif. Photo descriptions, and data from the sensors used will be saved in a csv file.
In the second stage, on the Earth using the OpenCV module, we get a pixel shift between two pictures, which, given the known camera parameters and the height of the ISS, will allow us to calculate actual station speed. Data from the gyroscope and accelerometer will allow us to correct any possible maneuvers of the station.
Data from the magnetometer and the temperature, pressure and humidity will be used to check if they change with the transition into the  Earth's shadow.

We expect that we will be able to correctly determine the speed of the ISS stations. Perhaps we will be also able to detect velocity differences at apogee or perigee. We are not sure if we can detect the city lights in the night photographs, but this will be an important experiment for us, defining the possibilities of Picamera. We expect nice pictures of the Earth seen from space, which in itself will have tremendous value for us.
