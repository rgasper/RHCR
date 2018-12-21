#!/usr/bin/env python
# coding: utf-8


import os
import matplotlib.pyplot as plt
import numpy as np
#import pandas as pd

#from PIL import Image
from keras.preprocessing.image import load_img

os.getcwd()
os.chdir('/Users/wigasper/Documents/Python/English Practice')

image = load_img("./RGALI Documents/1.tif", color_mode = 'grayscale', 
                 target_size = None)

# can also use imageObject.show() (non static)
plt.imshow(image)
plt.show()

# image size in pixels
print("Image size: " + repr(image.size) + " pixels")

# imageObject.crop(x1, y1, x2, y2) w/ top left at (0,0)
cropped_image = image.crop(box=(0, 0, 1000, 1000))

# show cropped image
plt.imshow(cropped_image)
plt.show()

# image size in pixels
print("Image size: " + repr(cropped_image.size) + " pixels")

  
def get_windows(image_in, segments_in, count_in):
    
    # Arguments
    #    image_in: The original image to be successively cropped
    #        into smaller and smaller pieces.
    #    segments_in: The number of segments each side will be 
    #        divided into. Specified initially and then reduced
    #        with each recursive call.
    #    count_in: The accumulator for image file labels. Should
    #        initially be zero, increased with every crop and passed
    #        with each recursive call.

    return_bool = False
    segments = segments_in
    image = image_in
    count = count_in
    shrink_factor = int(segments * 1.25)
    
    x_offset = image.width / segments
    y_offset = x_offset * 2
    y = 0 
    
    if (x_offset <= 30):
        return_bool = True
    else:
        for horizontal in range(0, segments * 3):   
            x = 0
            for vertical in range(0, segments * 3):
                # crop out the window
                image_out = image.crop(box=(x, y, x + x_offset, y + y_offset))
                
                # to nparray
                image_out = np.array(image_out)
                
                # normalization
                image_out = image_out / 255.0
                
                # increase contrast. These values may need to be optimized
                image_out[image_out < .4] = .01
                image_out[image_out > .7] = .99
                
                # save image if it is mostly light colored
                # if (image_out.mean() > .45):
                
                # save image if it is not all white or all black
                if (image_out.mean() > .45 and image_out.mean() < .98):
                    plt.imsave("./crops/{}_x_{}-{}_y_{}-{}.jpg".format(count, 
                               int(x), int(x + x_offset), int(y), 
                               int(y + y_offset)), image_out)
                x += x_offset / 3
                count += 1
            y += y_offset / 3
        
        return get_windows(image, shrink_factor, count)
    
    return return_bool

get_windows(image, 20, 0)


