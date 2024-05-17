from PIL import Image, ImageDraw, ImageFont
import pandas as pd

WIDTH = 84
HEIGHT = 81
TOP_LEFT = (253,8)
PRODUCT_TYPES = ['ADVENTURING EQUIPMENT','ANIMALS & TRANSPORTATION','ARMS & ARMOUR','JEWELRY','MUSICAL INSTRUMENT','POTIONS & SCROLLS','SUMMONING DEVICE','TOOLS & KITS']


def draw_letter(img, position, size, color, letter):
    size = int(size)+10
    draw = ImageDraw.Draw(img)
    x, y = position
    position = (x-10,y-10)
    font = ImageFont.truetype("Starborn.ttf", size)
    draw.text(position, letter, font=font, fill=color)
    return img

def draw_circle_on_image(img, position, circle_radius, circle_color):
    draw = ImageDraw.Draw(img)
    x, y = position
    top_left = (x - circle_radius, y - circle_radius)
    bottom_right = (x + circle_radius, y + circle_radius)
    draw.ellipse([top_left, bottom_right], fill=circle_color)
    return img

# Example usage:
image_path = 'heat_map_big.png'  # Change this to the path of your original image
output_path = 'modified_image.png'     # Change this to your desired output file path
circle_radius = 25  # Radius of the circles
circle_color = 'slategray'  # Color of the circle outlines

north = pd.read_csv('co_north.csv',index_col=0)
east = pd.read_csv('co_east.csv',index_col=0)
south = pd.read_csv('co_south.csv',index_col=0)
west = pd.read_csv('co_west.csv',index_col=0)
underdark = pd.read_csv('co_underdark.csv',index_col=0)


font = ImageFont.load_default()

img = Image.open(image_path)

for i in range(0,7):
    for j in range(0,7-i):
        x = TOP_LEFT[0] + WIDTH * i + 42
        y = TOP_LEFT[1] + HEIGHT * j + HEIGHT * i + 40

        north_value = north.loc[PRODUCT_TYPES[i+1], PRODUCT_TYPES[j]]
        east_value = east.loc[PRODUCT_TYPES[i+1], PRODUCT_TYPES[j]]
        south_value = south.loc[PRODUCT_TYPES[i+1], PRODUCT_TYPES[j]]
        west_value = west.loc[PRODUCT_TYPES[i+1], PRODUCT_TYPES[j]]
        underdark_value = underdark.loc[PRODUCT_TYPES[i+1], PRODUCT_TYPES[j]]

        total = north_value + east_value + south_value + west_value + underdark_value


        # draw_circle_on_image(img, (x, y + 25), circle_radius * (north_value/total), circle_color)
        # draw_circle_on_image(img, (x, y - 25), circle_radius * (south_value/total), circle_color)
        # draw_circle_on_image(img, (x + 25, y), circle_radius * (east_value/total), circle_color)
        # draw_circle_on_image(img, (x - 25, y), circle_radius * (west_value/total), circle_color)
        # draw_circle_on_image(img, (x, y), circle_radius * (underdark_value/total), circle_color)

        draw_letter(img, (x, y + 25), circle_radius * (south_value/total), circle_color,"S")
        draw_letter(img, (x, y - 25), circle_radius * (north_value/total), circle_color,"N")
        draw_letter(img, (x + 25, y), circle_radius * (east_value/total), circle_color,"E")
        draw_letter(img, (x - 25, y), circle_radius * (west_value/total), circle_color,"W")
        draw_letter(img, (x+4, y+4), circle_radius * (underdark_value/total), circle_color,"U")


img.save(output_path)
print(f"Image saved to {output_path}")

