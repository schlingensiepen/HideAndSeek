import cv2 as cv
import numpy as np
import os
from time import time
from windowcapture import WindowCapture
from vision import Vision

# Change the working directory to the folder this script is in.
# Doing this because I'll be putting the files from each video in their own folder on GitHub
os.chdir(os.path.dirname(os.path.abspath(__file__)))


# initialize the WindowCapture class
wincap = WindowCapture('Snake++')
# initialize the Vision class
vision_snake = Vision('snake_part.png')

old_screenshot = wincap.get_screenshot()

loop_time = time()
while(True):

    
    screenshot = wincap.get_screenshot()

    
    vector = vision_snake.find(screenshot, 0.8, 'rectangles')
    print(vector)
   
    
    
    #print('FPS {}'.format(1 / (time() - loop_time)))
    loop_time = time()

    
    if cv.waitKey(1) == ord('q'):
        cv.destroyAllWindows()
        break

    old_screenshot = screenshot

print('Done.')