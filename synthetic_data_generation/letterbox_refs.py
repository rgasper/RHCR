'''
Data related to how to draw the bounding boxes for the letters so that they do a decent job of fitting reality
'''
from collections import namedtuple
# not enough data in here for it to really matter, just using namedtuple for fun

# when we draw a box for a letter, we want to move inflate the box slightly
# this will cause boxes to overlap, but that's _okay_
inflation_factor = 1.1

# TODO jiggle is unused but I would really like to add it
# how much random noise to add to the weights when drawing box
jiggle_factor = 0.05

weights = namedtuple('Weights', ['x','y','y_off'])
# x weight is true weight for weighted average of word width
# y weight is % of word height
# y_off is an offset from the _bottom_line_??? (top line???) of the word where this letter gets drawn
default_char_weight = weights(1.,1.,0.)
valid_chars =  ",-.0123456789?ЁАБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдежзийклмнопрстуфхцчшщъыьэюяё"
char_weight_dict = {
    "," : weights(0.25, 0.25, -0.1),
    "-" : weights(0.25, 0.25, 0.25),
    "." : weights(0.25, 0.25, 0),
    "0" : weights(1., 1., 0.),
    "1" : weights(1., 1., 0.),
    "2" : weights(1., 1., 0.),
    "3" : weights(1., 1., 0.),
    "4" : weights(1., 1., 0.),
    "5" : weights(1., 1., 0.),
    "6" : weights(1., 1., 0.),
    "7" : weights(1., 1., 0.),
    "8" : weights(1., 1., 0.),
    "9" : weights(1., 1., 0.),
    "?" : weights(1., 1., 0.),
    "Ё" : weights(1., 1.1, 0.),
    "А" : weights(1.1, 1., 0.),
    "Б" : weights(1., 1., 0.),
    "В" : weights(1., 1., 0.),
    "Г" : weights(1., 1., 0.),
    "Д" : weights(1.1, 1., 0.),
    "Е" : weights(1., 1., 0.),
    "Ж" : weights(1.5, 1., 0.),
    "З" : weights(0.8, 1., 0.),
    "И" : weights(1., 1., 0.),
    "Й" : weights(1., 1.1, 0.),
    "К" : weights(1.1, 1., 0.),
    "Л" : weights(1., 1., 0.),
    "М" : weights(1.5, 1., 0.),
    "Н" : weights(1., 1., 0.),
    "О" : weights(1., 1., 0.),
    "П" : weights(1., 1., 0.),
    "Р" : weights(1., 1., 0.),
    "С" : weights(1., 1., 0.),
    "Т" : weights(1., 1., 0.),
    "У" : weights(1., 1., 0.),
    "Ф" : weights(1., 1., 0.),
    "Х" : weights(1.2, 1., 0.),
    "Ц" : weights(1., 1.1, -0.1),
    "Ч" : weights(0.8, 1., 0.),
    "Ш" : weights(1.5, 1., 0.),
    "Щ" : weights(1.5, 1.1, -0.1),
    "Ъ" : weights(0.8, 1., 0.),
    "Ы" : weights(1.5, 1., 0.),
    "Ь" : weights(0.7, 1., 0.),
    "Э" : weights(1., 1., 0.),
    "Ю" : weights(1.25, 1., 0.),
    "Я" : weights(1., 1., 0.),
    "а" : weights(0.5, 0.5, 0.),
    "б" : weights(0.5, 0.9, 0.),
    "в" : weights(0.5, 0.5, 0.),
    "г" : weights(0.5, 0.5, 0.),
    "д" : weights(0.5, 0.5, 0.),
    "е" : weights(0.5, 0.5, 0.),
    "ж" : weights(0.8, 0.5, 0.),
    "з" : weights(0.5, 0.5, 0.),
    "и" : weights(0.5, 0.5, 0.),
    "й" : weights(0.5, 0.65, 0.),
    "к" : weights(0.5, 0.5, 0.),
    "л" : weights(0.5, 0.5, 0.),
    "м" : weights(0.5, 0.5, 0.),
    "н" : weights(0.5, 0.5, 0.),
    "о" : weights(0.5, 0.5, 0.),
    "п" : weights(0.5, 0.5, 0.),
    "р" : weights(0.5, 0.8, -0.25),
    "с" : weights(0.5, 0.5, 0.),
    "т" : weights(0.5, 0.5, 0.),
    "у" : weights(0.5, 0.8, -0.25),
    "ф" : weights(0.5, 1., -0.25),
    "х" : weights(0.5, 0.5, 0.),
    "ц" : weights(0.5, 0.6, -0.1),
    "ч" : weights(0.5, 0.5, -0.1),
    "ш" : weights(1., 0.5, 0.),
    "щ" : weights(1., 0.5, -0.05),
    "ъ" : weights(0.5, 0.5, 0.),
    "ы" : weights(0.9, 0.5, 0.),
    "ь" : weights(0.5, 0.5, 0.),
    "э" : weights(0.5, 0.5, 0.),
    "ю" : weights(0.5, 0.5, 0.),
    "я" : weights(0.5, 0.5, 0.),
    "ё" : weights(0.5, 0.8, 0.),
}