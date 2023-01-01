from PIL import Image
import os, sys

path = "./static/img/imagens/"
dest = "./static/img/thumbnails/"
dirs = os.listdir( path )

def resize():
    for item in dirs:
        if os.path.isfile(path+item):
            im = Image.open(path+item)
            f= os.path.splitext(path+item)
            im.thumbnail((400,300))
            im.save("./static/img/thumbnails/" + item, 'JPEG')

resize()

