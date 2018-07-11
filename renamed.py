# -*- coding: utf-8 -*-
import os
import sys

imagelist = []
imagelist = os.listdir("F:/Python/new biaozhu chepai/img")
num = len(imagelist)

for i in range(num):
    #filename = os.path.split(imagelist[i])[1].split('_')[0]
    filename = imagelist[i].split("_")[0]
    os.rename("./img/" + imagelist[i],"img/" + filename+".jpg")