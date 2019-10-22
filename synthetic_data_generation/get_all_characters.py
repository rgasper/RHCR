#!/usr/bin/env python3
'''
I'm mostly certain this isn't actually useful
'''

import os
import sys
import argparse
import traceback
from random import choice, sample
from functools import partial
from multiprocessing import Pool
from PIL import Image, ImageDraw, ImageFont
import csv


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

def generate_russian_chars(inputFile, chars=None):
    if chars is None:
        chars = set()
    # Read in document to transform to cursive
    with open(inputFile, "r") as handle:
        for line in handle:
            for frmtd_line in format_line(line):
                for c in frmtd_line:
                    chars.add(c)
    return chars

if __name__ == '__main__':
    # Get command line args
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--inputFile", help="input file path for single file", type=str)
    parser.add_argument("-d", "--dir", help="directory of source text files, will run on all .txt files inside the directory")
    global args
    args = parser.parse_args()

    if not(args.dir) and not (args.inputFile):
        raise NotImplementedError('must provide some kind of input to work with')

    # do stuff
    if args.inputFile:
        chars = generate_russian_chars(args.inputFile)
        print(f"{''.join(chars)}")
    
    if args.dir:
        dirlist = os.listdir(args.dir)
        infiles =  (f"{args.dir}/{f}" for f in dirlist)
        chars = None
        for f in infiles:
            chars = generate_russian_chars(f, chars=chars)
        print(f"{''.join(sorted(chars))}")
        