#!/usr/bin/env python3
"""Entry point."""
import argparse
import sys
import os
from skimage import io
from skimage import img_as_float
from skimage import transform as tf
import imageio
import numpy as np

__author__ = "kirilenko_bm"
LETTERS_DIR = "letters"
LETTER_SHAPE = (70, 90)
FRAMES_NUM = 30


class Grid:
    """Grid for letters."""
    def __init__(self, x_size=10, y_size=4,
                 x_char=LETTER_SHAPE[0],
                 y_char=LETTER_SHAPE[1],
                 overlap=5,
                 frames_num=FRAMES_NUM,
                 black_background=False):
        self.x_size = x_size
        self.y_size = y_size
        self.x_char = x_char
        self.y_char = y_char
        self.overlap = overlap
        self.frames_num = frames_num
        self.filler = np.zeros((y_char, x_char, 3)) if black_background else np.ones((y_char, x_char, 3))
        self.grid = [self.filler for _ in range(x_size * y_size)]
        self.append_pointer = 0
        self.frames = []

    def append(self, letter, pos=None):
        """Append the letter in the queue"""
        if not pos:
            self.grid[self.append_pointer] = letter
            self.append_pointer += 1
            self.append_pointer = 0 if self.append_pointer >= self.x_size * self.y_size else self.append_pointer
        else:
            pos = -1 if pos >= self.x_size * self.y_size else pos
            self.grid[pos] = letter

    def make_frame(self, frame_num):
        rows = []
        for row in parts(self.grid, n=self.x_size):
            row_pics = []
            for letter in row:
                frame = letter.render_state(frame_num) if isinstance(letter, Letter) else letter
                row_pics.append(frame)
            row_image = np.concatenate(row_pics, axis=1)
            rows.append(row_image)
        frame_image = np.concatenate(rows, axis=0)
        return frame_image


class Letter:
    """Class representing a letter and its position."""
    def __init__(self, char_arr, max_shift=1, black_background=False):
        self.char_arr = char_arr
        self.shifts = list(range(-max_shift, max_shift + 1))
        self.x_shift = np.random.choice(self.shifts, 1)[0]
        self.y_shift = np.random.choice(self.shifts, 1)[0]
        self.x_borders = (-5, 5)
        self.y_borders = (-5, 5)
        self.angle_borders = (-20, 20)
        self.angle = np.random.uniform(-2, 2, 1)[0]
        init_state = (self.x_shift, self.y_shift, self.angle)
        self.states_queue = [init_state]
        self.cval = 0 if black_background else 1

    def extend_queue(self, steps, plus_rev=False):
        """Extend states queue."""
        for _ in range(steps):
            self.x_shift += np.random.choice(self.shifts, 1)[0]
            self.y_shift += np.random.choice(self.shifts, 1)[0]
            self.angle += np.random.uniform(-2, 2, 1)[0]

            self.x_shift = self.x_borders[0] if self.x_shift < self.x_borders[0] else self.x_shift
            self.x_shift = self.x_borders[1] if self.x_shift > self.x_borders[1] else self.x_shift
            self.y_shift = self.y_borders[0] if self.y_shift < self.y_borders[0] else self.y_shift
            self.y_shift = self.y_borders[1] if self.y_shift > self.y_borders[1] else self.y_shift
            self.angle = self.angle_borders[0] if self.angle < self.angle_borders[0] else self.angle
            self.angle = self.angle_borders[1] if self.angle > self.angle_borders[1] else self.angle

            state = (self.x_shift, self.y_shift, self.angle)
            self.states_queue.append(state)
        if plus_rev:
            states_rev = self.states_queue[::-1]
            self.states_queue.extend(states_rev)

    def render_state(self, state_num):
        """Render image of the state requested."""
        if state_num > len(self.states_queue):
            eprint("Warning! Requested state number is out of borders.")
            state_num = 0
        state = self.states_queue[state_num]
        im = np.roll(self.char_arr, shift=state[0], axis=0)
        im = np.roll(im, shift=state[1], axis=1)
        im = tf.rotate(im, angle=state[2], mode="constant", cval=self.cval)
        return im


def eprint(line, end="\n"):
    """Like print but for stdout."""
    sys.stderr.write(line + end)


def die(msg, rc=1):
    """Die with rc and show msg."""
    eprint(msg + "\n")
    sys.exit(rc)


def parts(lst, n=25):
    """Split an iterable into a list of lists of len n."""
    return [lst[i:i + n] for i in iter(range(0, len(lst), n))]


def parse_args():
    """Parse args and check it."""
    app = argparse.ArgumentParser()
    app.add_argument("text", help="Text to draw")
    app.add_argument("output", help="Where to save")
    app.add_argument("--font", "-f", default="Helvetica", help="Font to use."
                     "There must be png files like: "
                     "letters/{FONT_NAME}_{character}.png")
    app.add_argument("--black_background", "-b", action="store_true", dest="black_background",
                     help="Make black background instead of white")
    app.add_argument("--smart", "-s", action="store_true", dest="smart",
                     help="Smart alignment of letters, then grid_x and y "
                          "options are cancelled. Recommended to use.")
    app.add_argument("--grid_x", "-x", type=int, default=7, help="Width, letters")
    app.add_argument("--grid_y", "-y", type=int, default=3, help="Height, letters")
    app.add_argument("--rgb_shift", "-r", type=int, default=2)
    if len(sys.argv) < 3:
        app.print_help()
        sys.exit(0)
    args = app.parse_args()
    return args


def read_font(font_name, black_background=False):
    """Return character: image dictionary."""
    char_filenames = [x for x in os.listdir(LETTERS_DIR) if x.startswith(font_name)]
    die("Error! Pictures for {} font not found") if len(char_filenames) == 0 else None
    char_arr = {}
    for font_file in char_filenames:
        character = font_file.split("_")[1].split(".")[0]
        char_path = os.path.join(LETTERS_DIR, font_file)
        arr = img_as_float(io.imread(char_path))
        h, w, d = arr.shape
        how_left = LETTER_SHAPE[0] - w
        left_fill = np.ones((h, how_left // 2 + how_left % 2, 3)) if not black_background else \
            np.zeros((h, how_left // 2 + how_left % 2, 3))
        right_fill = np.ones((h, how_left // 2, 3)) if not black_background else \
            np.zeros((h, how_left // 2, 3))
        arr = np.concatenate((left_fill, arr, right_fill), axis=1)
        how_vert = LETTER_SHAPE[1] - h
        above_fill = np.ones((how_vert // 2 + how_vert % 2, LETTER_SHAPE[0], 3)) if not black_background else \
            np.zeros((how_vert // 2 + how_vert % 2, LETTER_SHAPE[0], 3))
        below_fill = np.ones((how_vert // 2, LETTER_SHAPE[0], 3)) if not black_background else \
            np.zeros((how_vert // 2, LETTER_SHAPE[0], 3))
        arr = np.concatenate((below_fill, arr, above_fill), axis=0)
        char_arr[character] = arr
    char_arr[" "] = np.ones((LETTER_SHAPE[1], LETTER_SHAPE[0], 3)) if not black_background else \
        np.zeros((LETTER_SHAPE[1], LETTER_SHAPE[0], 3))
    return char_arr


def rgb_shift(img, kt):
    """Apply chromatic aberration."""
    shp = img.shape
    red = img[:, :, 0]
    green = img[:, :, 1]
    blue = img[:, :, 2]
    # split channels, make shift
    red = tf.resize(red, output_shape=(shp[0], shp[1]))
    green = tf.resize(green, output_shape=(shp[0] - kt, shp[1] - kt))
    blue = tf.resize(blue, output_shape=(shp[0] - 2 * kt, shp[1] - 2 * kt))

    w, h = blue.shape
    ktd2 = int(kt / 2)
    red_n = np.reshape(red[kt: -kt, kt: -kt], (w, h, 1))
    green_n = np.reshape(green[ktd2: -1 * ktd2, ktd2: -1 * ktd2], (w, h, 1))
    blue_n = np.reshape(blue[:, :], (w, h, 1))

    new_im = np.concatenate((red_n, green_n, blue_n), axis=2)
    new_im = tf.resize(new_im, (shp[0], shp[1]))
    return new_im


def split_text(text, width):
    """Split text in lines of width width."""
    res = ""
    ctr = 0
    for word in text.split():
        ctr += len(word)
        if ctr > width:
            res += '\n'
            ctr = len(word)
        elif res != "":
            res += " "
            ctr += 1
        res += word
    return res.split("\n")

def get_lines(text, w_opt=None):
    """Return X Y for grid."""
    words = text.split()
    w_max = max(len(w) for w in words)
    w_ = w_max if not w_opt else w_opt
    # at least as long as the longest word
    w_ = w_ if w_ >= w_max else w_max
    lines_raw = split_text(text, w_)
    lines = [l.center(w_) for l in lines_raw]
    return lines


def main():
    """Main function."""
    args = parse_args()
    font = read_font(args.font, black_background=args.black_background)
    letters_available = list(font.keys())
    text = [s for s in args.text.upper() if s in letters_available]
    if args.smart:
        lines = get_lines("".join(text))
        text = "".join(lines)
        x = len(lines[0])
        y = len(lines)
    else:
        x = args.grid_x
        y = args.grid_y
    G = Grid(black_background=args.black_background,
             x_size=x,
             y_size=y)
    rgb_shift_param = args.rgb_shift if args.rgb_shift % 2 == 0 else args.rgb_shift - 1
    for sign in text:
        sign_arr = font.get(sign)
        l = Letter(sign_arr, black_background=args.black_background)
        l.extend_queue(FRAMES_NUM, plus_rev=True)
        G.append(l)
    gif_frames = []
    for frame_num in range(FRAMES_NUM * 2):
        frame = G.make_frame(frame_num)
        frame = rgb_shift(frame, rgb_shift_param)
        frame[frame < 0.2] = 0.0
        gif_frames.append(frame)
    imageio.mimsave(args.output, gif_frames)
    sys.exit(0)


if __name__ == "__main__":
    main()
