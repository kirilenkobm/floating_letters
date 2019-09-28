#!/usr/bin/env python3
"""Convert font to images of letters."""
import sys
import os
from PIL import Image, ImageFont, ImageDraw

LETTER_SIZE = 60

try:
    font_file = sys.argv[1]
    output_folder = sys.argv[2]
except IndexError:
    sys.stderr.write("Usage: {} [ttf file] [output folder]\n".format(sys.argv[0]))
    sys.exit(0)

# use a truetype font
font_name = os.path.basename(font_file).split(".")[0]
font = ImageFont.truetype(font_file, LETTER_SIZE - 2)
im = Image.new("RGB", (LETTER_SIZE, LETTER_SIZE))
draw = ImageDraw.Draw(im)
symbols = [ord(c) for c in "!?.,'[]()"]
up_letters_cyr = list(range(ord("А"), ord("Я") + 1))
lo_letters_cyr = list(range(ord("а"), ord("я") + 1))
up_letters_lat = list(range(ord("A"), ord("Z") + 1))
lo_letters_lat = list(range(ord("a"), ord("z") + 1))
numbers = list(range(ord("0"), ord("9") + 1))
characters = up_letters_lat + lo_letters_lat \
             + up_letters_cyr + lo_letters_cyr \
             + numbers

for code in characters:
    w, h = draw.textsize(chr(code), font=font)
    im = Image.new("RGB", (w, h), color="#FFFFFF")
    draw = ImageDraw.Draw(im)
    char = chr(code)
    draw.text((0, 0), char, font=font, fill="#000000")
    if char.islower():
        char += "_lo"
    im.save(f"letters/{font_name}_{char}.png")
