#!/usr/bin/env python3

import os
import sys
import logging
import argparse
import traceback
from random import choice, sample
from functools import partial
from multiprocessing import Pool
from PIL import Image, ImageDraw, ImageFont
import csv

import letterbox_refs

# Set up logger
logging.basicConfig(#filename='log_traindatagen',
                    filemode='w',
                    format='[%(module)s:%(lineno)d] %(asctime)s - [%(levelname)s] - %(message)s',
                    datefmt='%d-%b-%Y %H:%M:%S',
                    level=logging.DEBUG)
logger = logging.getLogger(__name__)

def format_line(line, max_width=90):
    ''' Ensures that lines of text terminate reasonably even if document has no newlines '''
    line = line.split()
    while len(line) > 0:
        out = line[0]
        line = line[1:]
        while len(line) > 0 and len(out) + len(line[0]) + 1 < max_width:
            out = " ".join([out, line[0]])
            line = line[1:]
        yield out

def get_doc_dimensions(doc, font, side_margin, header_margin, line_buffer):
    ''' determines the appropriate dimensions for the document
        :params:
            doc- list of lines of text
            font- the font being used in the document
            side_margin- pixel width of side margins
            header_margin- pixel height of header/footer margins
            line_buffer- pixel height of line separator 
        :return:
            a tuple indicating document dimensions
    '''
    # Image and Draw objects need to be instantiated because textsize() can't
    # be called statically
    img = Image.new('L', (1, 1), 255)
    draw = ImageDraw.Draw(img)
    max_width = 0
    current_y = 0
    for line in doc:
        text_w, text_h = draw.textsize(line, font=font)
        if text_w > max_width:
            max_width = text_w
        current_y = current_y + text_h + line_buffer
    
    width = max_width + (side_margin * 2)
    height = current_y + (header_margin * 2)

    return width, height

def generate_responses(word, current_x, current_y, font, 
                        connected_width, doc_id):
    ''' Generates the response data for a word
        :params:
            word- the word to have data generated for
            current_x- the x origin of the word
            current_y- the y origin of the word
            font- an ImageFont object used for the text
            connected_width- the width of the word when written as an entire word
            doc_id- the ID of the document
        :return:
            responses- a list of response data lists
    '''
    # tuning value adds pixels to every side of the box to improve
    # letter containment
    box_tuner = 8

    responses = []

    # not actually drawing anything, just using this to get texsize
    img = Image.new('L', (1, 1), 255)
    draw = ImageDraw.Draw(img)

    # Get word width if letters are written individually
    unconnected_width = 0
    for letter in word:
        text_w, text_h = draw.textsize(letter, font=font)
        unconnected_width += text_w

    # Proportion
    prop = connected_width / unconnected_width

    for letter in word:
        text_w, text_h = draw.textsize(letter, font=font)
        # resp format: [doc, x0, y0, x1, y1, letter]
        responses.append([doc_id, 
                          current_x - box_tuner, 
                          current_y - box_tuner, 
                          current_x + int(text_w * prop) + box_tuner, 
                          current_y + text_h + box_tuner, 
                          letter])
        current_x = current_x + int(text_w * prop)

    return responses
    
def get_nice_boxes(letters, origin_x, origin_y, word_w, word_h):
    ''' uses reference data to find slightly clever bounding boxes for the cursive letters 
    :params:
        letters: str - an iterable of unicode characters
        origin_x: int - the x coordinate of the origin (topleft)
        origin_y: int - the y coordinate of the origin (topleft)
        word_w: int - how wide is the word overall
        word_h: int - how tall is the word overall
    :return:
        boxes: list - an iterable containing many lists representing:
            box- (topleft[0,1], botright[0,1])
        '''
    boxes, _refs = [], []

    # change from iterable of letters to iterable of reference namedtuples
    for letter in letters:
        try:
            _refs.append(letterbox_refs.char_weight_dict[letter])
        except KeyError:
            _refs.append(letterbox_refs.default_char_weight)
    
    x_dist_unit = word_w / sum(ref.x for ref in _refs)
    y_dist_unit = word_h
    
    # use floats while in progress then convert back to ints when we're done
    topleft = [float(origin_x), float(origin_y)]
    for ref in _refs:
        box = ( 
                ( int(topleft[0]),
                  int(topleft[1] + y_dist_unit*(-1*ref.y_off)) )
            ,
                ( int(topleft[0] + x_dist_unit*ref.x), 
                  int(topleft[1] + y_dist_unit*(-1*ref.y_off+ref.y)) )
            )
        boxes.append(box)
        topleft[0] += x_dist_unit*ref.x

    return boxes

def txt_to_cursive_img(doc, out_path):
    ''' turns a document text into cursive images
        :params:
            doc- list of lines of text
            out- path to a file to put the image
        :return:
            a PIL Image object, response data, and the font (for debugging, some fonts have issues right now)
    '''
    logger.debug(f'generating cursive text image to {out_path}')
    # line_buffer is the pixel spacing between lines
    line_buffer = 15

    # pixel value of the side margins
    side_margin = 40

    # pixel value of header and foot margins
    header_margin = 40

    # Get a random font
    fonts = os.listdir("./fonts")
    font = ImageFont.truetype(f"./fonts/{choice(fonts)}", 120)

    # Get max line width and document height
    width, height = get_doc_dimensions(doc, font, side_margin, header_margin, line_buffer)

    img = Image.new('L', (width, height), 255)
    artist = ImageDraw.Draw(img)

    current_y = 0 + header_margin
    current_x = 0 + side_margin
    space = 25

    responses = []

    for line in doc:
        # logger.debug('converting line')
        max_height = 0
        for word in line.split():
            text_w, text_h = artist.textsize(word, font=font)
            if text_h > max_height:
                max_height = text_h
            artist.text((current_x, current_y), word, font=font, fill=0)
            # box format: [doc, x0, y0, x1, y1, letter]
            boxes = generate_responses(word, current_x, current_y, font, 
                        text_w, out_path)
            if args.viz:
                for box in boxes:
                    artist.rectangle(((box[1], box[2]),(box[3],box[4])), width=0, outline=0)
            current_x = current_x + text_w + space
        current_x = side_margin
        current_y = current_y + max_height + line_buffer

    font_out = font.path.split('/')[-1]

    return img, responses, font_out
    
# NOTE(rgasper) the targetFile API is kinda dumb I'm sure there's a better way to do this 
def generate_file(inputFile, outputFile, targetFile=None):
    if targetFile is None:
        targetFile = outputFile.split('.')[0] + '_targets.csv'
    # Output formats supported by matplotlib NOTE(rgasper) I bet we can import this somehow instead of having it manually here
    supported_formats = ["eps", "jpeg", "jpg", "pdf", "pgf", "png", "ps", 
                            "raw", "rgba", "svg", "svgz", "tif", "tiff"]
    if args.outputFile.split(".")[1] not in supported_formats:
        args.outputFile = "".join([args.outputFile, ".png"])
        logger.warn(f'invalid outputFile format, using png instead. please use one of the following formats: {supported_formats}')
    doc = []
    # Read in document to transform to cursive
    with open(inputFile, "r") as handle:
        for line in handle:
            for frmtd_line in format_line(line):
                doc.append(frmtd_line)
    # Change each letter to a cursive image
    logger.debug(f'converting string doc to cursive images for {inputFile}')
    try:
        out, responses, font = txt_to_cursive_img(doc, outputFile)
        out.save(outputFile)
        # resp format: [doc, x0, y0, x1, y1, letter]
        with open(targetFile, "w") as tf:
            writer = csv.writer(tf)
            writer.writerows(responses)
    except:
        logger.exception(f'failed to generate a cursive image into file {outputFile}')
        raise

    return True

if __name__ == '__main__':
    # Get command line args
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--inputFile", help="input file path for single file", type=str)
    parser.add_argument("-o", "--outputFile", default="test.png", help="output file path", type=str)
    parser.add_argument("-d", "--dir", help="directory of source text files, will run on all .txt files inside the directory")
    parser.add_argument("-v", "--viz", help="visualize the bounding boxes in the resulting image pages", action='store_true')
    parser.add_argument("-c", "--count", help="only produce this many output files", type=int)
    parser.add_argument("-f", "--force", help='overwrite any output directories without user prompt', action='store_true')
    global args
    args = parser.parse_args()

    if not(args.dir) and not (args.inputFile):
        raise NotImplementedError('must provide some kind of input to work with')

    # do stuff
    if args.inputFile:
        logger.info(f'processing {args.inputFile}')
        generate_file(args.inputFile, args.outputFile)
    
    if args.dir:
        outDir = "images_output"
        logger.info(f'processing all .txt files in {args.dir}, placing results in {outDir}')
        try:
            os.mkdir(outDir)
        except FileExistsError:
            response = False
            if not args.force:
                response = input(f'Delete all files in directory {outDir} [y/n]?       ')
                response = response.lower().strip()[0] == 'y'
            if response or args.force:
                logger.info(f'cleared all files in {outDir}')
                for f in os.listdir(outDir):
                    os.remove(f"{outDir}/{f}")

        dirlist = os.listdir(args.dir)
        if args.count:
            dirlist = sample(dirlist, args.count)
        
        infiles =  (f"{args.dir}/{f}" for f in dirlist)

        def to_png(filename):
            splits = filename.split('.')
            return f"{splits[0]}.png"
        outfiles =  (f"{outDir}/{to_png(f)}" for f in dirlist)        
        
        logger.info=(f'starting multiprocess pool iterating over files in {args.dir}')
        pool = Pool(4)
        results = pool.starmap(generate_file, zip(infiles, outfiles))