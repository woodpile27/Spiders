import os
import jieba.analyse
from PIL import Image, ImageSequence
import numpy as np
import matplotlib.pyplot as plt
from wordcloud import WordCloud, ImageColorGenerator

def read_content(content_path):
    content = ''
    for f in os.listdir(content_path):
        f_fullpath = os.path.join(content_path, f)
        for txt in os.listdir(f_fullpath):
            txt_fullpath = os.path.join(f_fullpath, txt)
            if os.path.isfile(txt_fullpath):
                with open(txt_fullpath, 'r') as t:
                    content += t.read()
    return content

lyric = read_content('./jay_chou')
result = jieba.analyse.textrank(lyric, topK=1000, withWeight=True)
keywords = dict()
for i in result:
    keywords[i[0]] = i[1]

image = Image.open('./jay.png')
graph = np.array(image)
wc = WordCloud(font_path='./fonts/bb4171/SourceHanSans-Medium.otf',     background_color='white', max_words=1000, mask=graph)
wc.generate_from_frequencies(keywords)
image_color = ImageColorGenerator(graph)

plt.imshow(wc)
plt.imshow(wc.recolor(color_func=image_color))
plt.axis("off")
plt.show()
