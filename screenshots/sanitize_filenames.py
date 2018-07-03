import glob
import os

for image in glob.glob('*.png'):
    newname = image.replace(' ','_')
    os.rename(image,newname)
    print(f'![{newname}](screenshots/{newname})','','* * *','',sep='\n')
