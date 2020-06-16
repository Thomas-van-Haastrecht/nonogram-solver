import imageio
import os
from PIL import Image
images = []

file_names = os.listdir("frames/sim_anl")

for filename in file_names:
    images.append(Image.open("frames/sim_anl/" + filename))
images[0].save('frames/search.gif', format='GIF', append_images=images[1:], save_all=True, duration=200, loop=0)
