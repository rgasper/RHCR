#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from random import random, randint
import logging
from logging.handlers import RotatingFileHandler
import argparse
global log

valid_letters = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ "

def random_punctuator(word):
    ''' cus we don't allow punctuation, just add some in randomly '''
    if random() < .08:
        return "".join([word, ","])
    if random() < .066:
        return "".join([word, "."])
    if random() < .02:
        return "".join([word, "?"])
    if random() < .04:
        if random() < .51:
            if random() < .51:
                return "".join([word, '"'])
            else:
                return "".join(['"', word])
        else:
            return "".join([word, " - "])
    return word

def format_line(line, max_width=50):
    try:
        line = line.split()
        while len(line) > 0:
            out = random_punctuator(line[0])
            line = line[1:]
            while len(line) > 0 and len(out) + len(line[0]) + 1 < max_width:
                out = " ".join([out, random_punctuator(line[0])])
                line = line[1:]
            yield out
    except:
        log.exception(f'format_line failed on line: {line}')

def write_to_text(inputFile):
    identifier, out = 0, ""
    page_len = randint(0,1000)
    with open(inputFile, "r") as fp:
        for line in fp:
            if len(out) > page_len:
                page_len = randint(0,1000)
                outFile = f"generated_text/ruwiki_clean_{str(identifier).zfill(7)}.txt"
                log.debug(f"writing to output file: {outFile}")
                with open(outFile, "w") as fp:
                    for out_line in format_line(out): # NOTE(rgasper) this could be turned into a oneliner with less punctuation
                        fp.write("".join([out_line, "\n"]))
                identifier += 1
                out = ""
            line_out = ""
            for char in line:
                if char in valid_letters:
                    line_out = "".join([line_out, char])
            line_out = line_out.split()
            if random() < .007:
                line_out.append(str(randint(0, 10000)))
            line_out = " ".join(line_out)
            if line_out:        
                out = " ".join([out, line_out])
    log.info(f'generated text for {identifier} files')

def getArgs():
    ''' used to get command-line arguments when run standalone '''
    parser = argparse.ArgumentParser(description='Does some sanitization of target russian-language wikipedia archive file for ML training purposes')
    parser.add_argument('-i', '--inputFiles', nargs='+', type=str,
                        help='file(s) to process. standard bash syntax')
    parser.add_argument('-o', '--outputFile', nargs=1, type=str, default='parsed.txt',
                        help='file to output text to')
    return parser.parse_args()

def getLog():
    ''' used to initialize logger when run standalone '''
    logfile = 'log_parse_ru_wiki'
    logging.basicConfig(
            format='[%(levelname)s] - [%(module)s:%(lineno)d] %(asctime)s - %(message)s',
            level=logging.DEBUG,
            datefmt='%Y-%m-%d %H:%M:%S')
    log = logging.getLogger(logfile)
    log.addHandler(RotatingFileHandler(logfile, mode='a', backupCount=3))
    log.handlers[0].doRollover() # make a new log each time
    return log

if __name__ == '__main__':
    global log
    log = getLog()
    args = getArgs()
    for inputFile in args.inputFiles:
        log.info(f'running on input {inputFile}')
        write_to_text(inputFile)
