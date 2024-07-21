import copy
import sys

from fontTools.ttLib.ttFont import TTFont
from PIL import ImageFont, Image, ImageDraw

ATLAS_PATH = r"font_j24x24.png"
ABF_PATH = r"font_j24x24.abf"
FONT_PATH = "ChosunGu.ttf"
FONT_MAP = "font_map.txt"
TEXT_HEIGHT = 24
ATLAS_W = 4096
ATLAS_H = 2048
BBOX_PADDING = 2


ABF: bytearray = bytearray()
NEW_ABF: bytearray = bytearray()
NEW_ATLAS = Image.new("RGBA", (ATLAS_W, ATLAS_H), 0)
draw = ImageDraw.Draw(NEW_ATLAS)
editable_seg_offset = []
old_abf_index = dict()

# read abf file
with open(ABF_PATH, "rb") as f:
    ABF = bytearray(f.read())
    NEW_ABF = copy.deepcopy(ABF)

# move to start of body
pos = 0
while pos < len(ABF):
    try:
        header_str = ABF[pos:pos+8].decode("utf-8")
    except:
        header_str = ""

    if header_str == "BFNTCBLK":
        pos += 16
        break
    pos += 8

body_start_pos = pos

# find offsets of editable segment
while pos < len(ABF):
    unicode_point = ABF[pos:pos+4]
    try:
        character = chr(int.from_bytes(unicode_point))
    except:
        pos += 32
        continue

    editable_seg_offset.append(pos)
    old_abf_index[character] = pos
    pos += 32
pos = None

font = TTFont(FONT_PATH)
support_char = []  # font support characters
target_character = []  # characters what add to new afb

# get cmap of font
for ch, _ in font["cmap"].getBestCmap().items():
    support_char.append(ch)

# check if font map contain not support character
with open(FONT_MAP, "r", encoding="utf-8") as f:
    fmap = list(f.read())
    for c in fmap:
        if ord(c) not in support_char:
            print(f"font is not support character {c}")
        else:
            target_character.append(c)

if len(editable_seg_offset) < len(target_character):
    print("Too many characters")
    sys.exit()

img_y = 0
img_x = 0
current_line_max_height = 0

NEW_ABF = copy.deepcopy(ABF[:body_start_pos])  # copy header
print(target_character)

for idx, new_chr in enumerate(target_character):
    # pos = editable_seg_offset[idx]
    # NEW_ABF[pos:] = ord(new_chr).to_bytes(4)
    font = ImageFont.truetype(FONT_PATH, TEXT_HEIGHT)
    bbox = font.getbbox(new_chr)
    left, top, right, bottom = bbox
    str_width = right - left + BBOX_PADDING
    str_height = bottom - top + BBOX_PADDING

    if str_height < TEXT_HEIGHT:
        str_height = TEXT_HEIGHT

    if img_x + str_width >= ATLAS_W:
        img_x = 0
        img_y += current_line_max_height + 5

    # print(new_chr, img_x, img_y)
    draw.text(xy=(img_x-left+BBOX_PADDING, img_y), text=new_chr, fill=(255, 255, 255), font=font)

    NEW_ABF.extend(ord(new_chr).to_bytes(4))
    NEW_ABF.extend(img_x.to_bytes(2))
    NEW_ABF.extend(img_y.to_bytes(2))
    NEW_ABF.extend(str_width.to_bytes(2))
    NEW_ABF.extend(str_height.to_bytes(2))

    if new_chr == " ":
        NEW_ABF.extend(bytearray.fromhex("00000000"))
        NEW_ABF.extend(bytearray.fromhex("0000000F"))
        NEW_ABF.extend(int("0").to_bytes(4))
        NEW_ABF.extend(int("0").to_bytes(4))
        NEW_ABF.extend(int("0").to_bytes(4))
    else:
        NEW_ABF.extend(bytearray.fromhex("00010000"))  # Unknown   ?? ?? 00 00
        NEW_ABF.extend(bytearray.fromhex("00" + '{:x}'.format(str_width).zfill(2) + "000F"))  # Unknown   ?? ?? 00 0F
        NEW_ABF.extend(int("0").to_bytes(4))
        NEW_ABF.extend(int("0").to_bytes(4))
        NEW_ABF.extend(int("0").to_bytes(4))

    if img_x + str_width < ATLAS_W and img_y + str_height < ATLAS_H:
        img_x += str_width + 8
        current_line_max_height = max(str_height, current_line_max_height)
    else:
        img_x = 0
        img_y += current_line_max_height + 8
        current_line_max_height = str_height

NEW_ABF.extend(bytearray("GENEEOF\t\0\0\0\0\0\0\0\0".encode()))

NEW_ATLAS.save("test.png")

with open("TEST.abf", "wb") as f:
    f.write(NEW_ABF)
