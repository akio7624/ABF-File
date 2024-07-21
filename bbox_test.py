from PIL import ImageFont, Image, ImageDraw

FONT_PATH = "ChosunGu.ttf"
TEXT_HEIGHT = 24
CHAR = "_"

font = ImageFont.truetype(FONT_PATH, TEXT_HEIGHT)
offset = font.getlength(CHAR)
print(offset)
bbox = font.getbbox(CHAR)
left, top, right, bottom = bbox

width = right - left
height = bottom - top

image = Image.new('RGB', (width, height))
draw = ImageDraw.Draw(image)

draw.text(xy=(0-left, 0-top), text=CHAR, fill=(255, 255, 255), font=font)

image.show()
