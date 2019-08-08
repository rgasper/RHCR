#!/usr/bin/env python3

import os
import sys
import logging
import argparse
import traceback
from random import randint
import threading
from PIL import Image, ImageDraw, ImageFont

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
    box_tuner = 6

    responses = []

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
        responses.append([doc_id, current_x - box_tuner, current_y - box_tuner, 
                        current_x + int(text_w * prop) + box_tuner, 
                        current_y + text_h + box_tuner, letter])
        current_x = current_x + int(text_w * prop)

    return responses
    
def txt_to_cursive_img(doc, out_path, logger):
    ''' turns a document text into cursive images using the dictionary
        :params:
            doc- list of lines of text
            logger- log object
        :return:
            a PIL Image object, response data, and the font (for debugging, some fonts have issues right now)
    '''
    try:
        # line_buffer is the pixel spacing between lines
        line_buffer = 15

        # pixel value of the side margins
        side_margin = 40

        # pixel value of header and foot margins
        header_margin = 40

        # number of threads
        thread_count = 5

        # Get a random font
        fonts = os.listdir("./fonts")
        font = ImageFont.truetype(f"./fonts/{fonts[randint(0, len(fonts) - 1)]}", 120)

        # Get max line width and document height
        width, height = get_doc_dimensions(doc, font, side_margin, header_margin, line_buffer)

        img = Image.new('L', (width, height), 255)
        draw = ImageDraw.Draw(img)

        current_y = 0 + header_margin
        current_x = 0 + side_margin
        space = 25

        responses = []

        for line in doc:
            max_height = 0
            for word in line.split():
                text_w, text_h = draw.textsize(word, font=font)
                if text_h > max_height:
                    max_height = text_h
                draw.text((current_x, current_y), word, font=font, fill=0)
                responses.extend(generate_responses(word, current_x, current_y, font, 
                            text_w, out_path))
                current_x = current_x + text_w + space
            current_x = side_margin
            current_y = current_y + max_height + line_buffer

        font_out = font.path.split('/')[-1]

        return img, responses, font_out

    except Exception as e:
        traceback.print_exc()
        trace = traceback.format_exc()
        logger.error(repr(e))
        logger.critical(trace)
        raise
    
if __name__ == '__main__':
    doc = []
    
    # Get command line args
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help="input file path", type=str, nargs=1)
    parser.add_argument("-o", "--output", help="output file path", type=str, nargs=1)
    args = parser.parse_args()
    
    # Set up logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler("traindatagen.log")
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Output formats supported by matplotlib
    supported_formats = ["eps", "jpeg", "jpg", "pdf", "pgf", "png", "ps", 
                            "raw", "rgba", "svg", "svgz", "tif", "tiff"]
        
    if args.input:
        in_path = args.input[0]
        # Read in document to transform to cursive
        with open(in_path, "r") as handle:
            for line in handle:
                for frmtd_line in format_line(line):
                    doc.append(frmtd_line)
    else:
        in_path = "sys.stdin"
        # haven't tested sys.sdtin usage
        for line in sys.stdin.read():
            for frmtd_line in format_line(line):
                doc.append(frmtd_line)
    
    if args.output:
        out_path = args.output[0]
        if out_path.split(".")[-1] not in supported_formats:
            out_path = "".join([out_path, ".png"])
    else:
        out_path = in_path.split("/")[-1]
        out_path = "".join(out_path.split(".")[:-1])
        out_path = f"{out_path}.png"
    
    # Change each letter to a cursive image
    logger.info('converting string doc to cursive images')
    out, responses, font = txt_to_cursive_img(doc, out_path, logger)
    
    out.save(f"{out_path}")
    logger.info(f"Translated {in_path} to {out_path} using {font}")

    # resp format: [doc, x0, y0, x1, y1, letter]
    with open("responses.tab", "w") as out:
        for resp in responses:
            out.write("\t".join([resp[0], str(resp[1]), str(resp[2]),
                        str(resp[3]), str(resp[4]), resp[5]]))
            out.write("\n")