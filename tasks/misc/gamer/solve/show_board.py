#!/usr/bin/env python3
from PIL import Image

with open("board.txt") as f:
    data = f.read()

    tiles, mines = data.split("\n---\n")
    tiles, mines = ([line.split(",") for line in piece.split("\n")] for piece in (tiles, mines))

    mines = [list(map(lambda x: int(x == "T"), row)) for row in mines]
    tiles = [list(map(lambda x: int(x) == 10, row)) for row in tiles]

h, w = len(mines), len(mines[0])

img = Image.new("RGB", (w, h))
img.putdata(list(96*mines[i][j]*256**2 + 255*tiles[i][j] for i in range(h) for j in range(w)))
img = img.transpose(Image.Transpose.ROTATE_90).transpose(Image.Transpose.FLIP_TOP_BOTTOM)
img.save("./img.png")
