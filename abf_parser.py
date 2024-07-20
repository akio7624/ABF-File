import random

import cv2

ABF_PATH = r"font_j24x24.abf"
IMG_PATH = r"font_j24x24.png"


def randomcolor():
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

img = cv2.imread(IMG_PATH)

data: bytearray = bytearray()
with open(ABF_PATH, "rb") as f:
    data = bytearray(f.read())

pos = 0

# move to start of body
while pos < len(data):
    try:
        header_str = data[pos:pos+8].decode("utf-8")
    except:
        header_str = ""

    if header_str == "BFNTCBLK":
        pos += 16
        break
    pos += 8

u1 = set()
u2 = set()
u3 = set()
u4 = set()
u5 = set()

dd: dict = dict()

while pos < len(data):
    unicode_point = data[pos:pos+4]
    try:
        character = chr(int.from_bytes(unicode_point))
    except:
        pos += 32
        continue

    column = int.from_bytes(data[pos+4:pos+6], byteorder="big")
    row = int.from_bytes(data[pos+6:pos+8], byteorder="big")

    width = int.from_bytes(data[pos + 8:pos + 10], byteorder="big")
    height = int.from_bytes(data[pos + 10:pos + 12], byteorder="big")

    unknown01 = data[pos+12:pos+16].hex(" ")
    unknown02 = data[pos+16:pos+20].hex(" ")
    unknown03 = data[pos+20:pos+24].hex(" ")
    unknown04 = data[pos+24:pos+28].hex(" ")
    unknown05 = data[pos+28:pos+32].hex(" ")

    u1.add(unknown01)
    u2.add(unknown02)
    u3.add(unknown03)
    u4.add(unknown04)
    u5.add(unknown05)

    dd.setdefault(f"u1_{unknown01}", [])
    dd[f"u1_{unknown01}"].append(character)

    dd.setdefault(f"u2_{unknown02}", [])
    dd[f"u2_{unknown02}"].append(character)

    dd.setdefault(f"u3_{unknown03}", [])
    dd[f"u3_{unknown03}"].append(character)

    dd.setdefault(f"u4_{unknown04}", [])
    dd[f"u4_{unknown04}"].append(character)

    dd.setdefault(f"u5_{unknown05}", [])
    dd[f"u5_{unknown05}"].append(character)

    cv2.rectangle(img, (column, row), (column+width, row+height), randomcolor(), 1)

    # print(f"{character}    col: {column}, row: {row}\t    w: {width}, h: {height}\t\t{unknown01}\t    {unknown02}\t    {unknown03}\t    {unknown04}\t    {unknown05}")
    print(f"{character}    {str(column).rjust(5)}    {str(row).rjust(5)}    {str(width).rjust(5)}    {str(height).rjust(5)}         {str(unknown01).rjust(5)}    {str(unknown02).rjust(5)}    {str(unknown03).rjust(5)}    {str(unknown04).rjust(5)}    {str(unknown05).rjust(5)}")
    pos += 32

print("\n")

tmp = [u1, u2, u3, u4, u5]
for i, u in enumerate(tmp):
    print(f"Unknown0{i+1}")
    for each in u:
        print(each + "  ...includes...  ", end="")
        print(dd[f"u{i+1}_{each}"])
    print("\n")

cv2.imwrite("border_"+IMG_PATH, img)
cv2.imshow(IMG_PATH, img)
cv2.waitKey(0)
cv2.destroyWindow()
