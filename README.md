# Floating letters

A tool to create floating text looking like this:

![alt text](examples/yanny.gif "Yanny")

Supports different fonts:

![alt text](examples/cannot.gif "Cannot")

Available fonts for now are "emboss" and "BEBAS".
Actually, any fond in ttf format may be used.
But first, it should be converted to images with "font_to_letters.py"

## TODO

Write usage info.

Like what all this stuff means:

```txt
usage: draw.py [-h] [--font FONT] [--black_background] [--grid_x GRID_X]
               [--grid_y GRID_Y] [--rgb_shift RGB_SHIFT]
               text output

positional arguments:
  text
  output

optional arguments:
  -h, --help            show this help message and exit
  --font FONT           Font to use.There must be png files
                        like:letters/{FONT_NAME}_{character}.png
  --black_background, -b
                        Make black background instead of white
  --grid_x GRID_X, -x GRID_X
  --grid_y GRID_Y, -y GRID_Y
  --rgb_shift RGB_SHIFT, -r RGB_SHIFT
```
