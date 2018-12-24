# Sandbox area for working with images and building sliding windows

import os
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm
from skimage.transform import resize
from keras.preprocessing.image import load_img

os.chdir('/Users/wigasper/Documents/Python/English Practice')

image = load_img("./RGALI Documents/1.tif", color_mode='grayscale',
                 target_size=None)

# these fields are here for future use. They probably will need to be moved
# when everything is scaled. image_id will obviously need to be set for each
# image.
image_id = 1

# can also use imageObject.show() (non static)
# plt.imshow(image)x
# plt.show()
#
# image size in pixels
# print("Image size: " + repr(image.size) + " pixels")
#
# imageObject.crop(x1, y1, x2, y2) w/ top left at (0,0)
# cropped_image = image.crop(box=(0, 0, 1000, 1000))
#
# show cropped image
# plt.imshow(cropped_image)
# plt.show()
#
# image size in pixels
# print("Image size: " + repr(cropped_image.size) + " pixels")


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

    # tuning value for optimizing window spacing
    spacer_tuning_val = 3
    
    # window height factor
    window_height = 2
    
    # sample_data can store as follows: [ID, x_min, x max, y_min, y_max] 
    # This will eventually be needed for assigning location to positive 
    # responses from the model
    sample_data = [[]]
    
    x_offset = image.width / segments
    y_offset = x_offset * window_height
    y = 0 
    
    if (x_offset <= 30):
        return_bool = True
    else:
        for horizontal in tqdm(range(0, segments * spacer_tuning_val)):   
            x = 0
            for vertical in range(0, segments * spacer_tuning_val):
                # crop out the window
                image_out = image.crop(box=(x, y, x + x_offset, y + y_offset))
                
                # to nparray
                image_out = np.array(image_out)
                
                # increase contrast. These values may need to be optimized
                image_out[image_out < 100.0] = 1.0
                image_out[image_out > 180.0] = 255.0

                # save image if it is not all white or all black
                if image_out.mean() > 115.0 and image_out.mean() < 250.0:
                    # normalization - not necessary if saving
                    # image_out = image_out / 255.0
                    
                    # resize
                    image_out = resize(image_out, (100, 50))
                
                    window_id = "".join([str(image_id).zfill(4), 
                                         str(count).zfill(5)])
    
                    plt.imsave("./crops/{}.jpg".format(window_id), image_out)
                    
                    # data out format: [ID, x_min, x max, y_min, y_max]
                    sample_data.append([window_id, int(x), int(x + x_offset), 
                                        int(y), int(y + y_offset)])

                x += x_offset / spacer_tuning_val
                count += 1
                
            y += y_offset / spacer_tuning_val
        
        return get_windows(image, shrink_factor, count)
    
    return return_bool


get_windows(image, 20, 0)
