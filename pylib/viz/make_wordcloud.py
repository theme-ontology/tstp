from os import path
from wordcloud import WordCloud
import lib.datastats
import numpy as np
from PIL import Image


def main():
    #d = path.dirname(__file__)
    width, height = 1000, 500
    themes = lib.datastats.themes_with_usage()
    data = {
        th: len(tobj.stories) ** 0.5
        for th, tobj in themes.iteritems()
    }
    #mask = np.array(Image.open(path.join(d, "ellipse1000x500.png")))
    #mask = np.array(Image.open("ellipse1000x500.png"))
    wordcloud = WordCloud(
        font_path = 'Helvetica.ttf',
        max_words = 5000,
        max_font_size = 20,
        prefer_horizontal = 1.0,
        width = width,
        height = height,
        scale = 2,
        #mask = mask,
        relative_scaling = 1.0,
    ).fit_words(data)

    for rec in wordcloud.layout_:
        print rec

    image = wordcloud.to_image()
    image.show()
