# -*- coding: utf-8 -*-
import os
import cv2
from PIL import Image, ImageDraw, ImageFont
import numpy as np


def get_file_name_list(dir_ame, filter):
    l = []
    # root -> 根目录; dirs -> 文件夹下子目录; files -> 文件下所有非目录文件
    for root, dirs, files in os.walk(dir_ame):
        for file in files:
            # 是否满足文件格式条件
            if os.path.splitext(file)[1] in filter:
                l.append(root + '/' + file)
    return l


def read_label_file(label_file_name, encoding='utf-16-le'):
    # 读取标签文件

    # 有的时候文件编码没处理好使得读进来的文件前面几个字符为'\ufeff',与第一条记录的第一个坐标重合,不能转换为int,导致出错
    # 如提前读取一个字节，则可以处理这种情况(但会影响正常文件)
    # 所以此处使用try尝试读取文件，如果出错，则使用提前读取一个字节的方法

    try:
        l = []
        f = open(label_file_name, 'r', encoding=encoding)
        for line in f:     #每行
            line = line.split()   #每行的单词以空格隔开
            if len(line) < 9:
                print('record length error in ', label_file_name)
                continue

            cord = [int(line[i]) for i in range(8)]
            #label = line[8]
            #cord.append(label)
            if len(line) == 9:
                label = line[8]
            else:
                label = line[9]
            cord.append(label)

            l.append(cord)
    except:
        l = []
        f = open(label_file_name, 'r', encoding=encoding)
        # 提前读取一个字节
        f.read(1)
        for line in f:
            line = line.split()
            if len(line) < 9:
                print('record length error in ', label_file_name)
                continue
            # if line[0].startswith(r'\ufe'):
                # line[0] = line[0][6:]

            cord = [int(line[i]) for i in range(8)]
            #label = line[8]
            #cord.append(label)
            if len(line) == 9:
                label = line[8]
            else:
                label = line[9]
            cord.append(label)

            l.append(cord)

    # return x1,y1,...,x4,y4, plate_name
    return l


def get_label_file_name(image_name, label_dir):
    # 获取标签文件名
    (filepath, tempfilename) = os.path.split(image_name)
    (filename, extension) = os.path.splitext(tempfilename)  #分离文件名与扩展名

    label_name = os.path.join(label_dir, filename + '.txt')

    if os.path.exists(label_name):
        return label_name
    else:
        return ''


def find_point(labels):
    l = []
    for label in labels:
        lable_name = label[8]
        x_re = [label[i] for i in range(8) if i % 2 == 0]
        y_re = [label[i] for i in range(8) if i % 2 != 0]

        p1 = (x_re[0], y_re[0])
        p2 = (x_re[1], y_re[1])
        p3 = (x_re[2], y_re[2])
        p4 = (x_re[3], y_re[3])

        l.append([p1, p2, p3, p4, lable_name])
    return l


def put_text_to_img(img, text, point):
    # 添加文本到图像中,opencv自带的putText不支持中文
    # 此处使用pillow库在图像中添加文字(因二者存储顺序不一致,需要转换编码RGB,BGR)

    # 处理边界文本
    height = point[1]
    if(height < 30):
        height = 0
    else:
        height = height - 30

    # cv2图像 -> PIL图像 -> 添加文本 -> 转换回cv2图像
    cv2_im = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    pil_im = Image.fromarray(cv2_im)

    draw = ImageDraw.Draw(pil_im)
    font = ImageFont.truetype("simhei.ttf", 30, encoding="utf-8")
    draw.text((point[0], height), text, (255, 0, 0), font=font)
    cv2_text_im = cv2.cvtColor(np.array(pil_im), cv2.COLOR_RGB2BGR)
    return cv2_text_im


def add_label_to_img(img, label):

    # 添加标签到图片中
    p1 = label[0]
    p2 = label[1]
    p3 = label[2]
    p4 = label[3]
    lable_name = label[4]

    cv2.line(img, p1, p2, (0, 0, 255), 2)
    cv2.line(img, p2, p3, (0, 0, 255), 2)
    cv2.line(img, p3, p4, (0, 0, 255), 2)
    cv2.line(img, p4, p1, (0, 0, 255), 2)

    if len(lable_name)>1:
        img = put_text_to_img(img, lable_name, p1)
    else:
        img = put_text_to_img(img, lable_name, p3)

    return img


def show_img_with_label(img_name, label_name, resize=(1200, 900)):

    # 读取文件和标签(如果有)
    img = cv2.imread(img_name)

    has_label_file = True
    if label_name != '':
        label = read_label_file(label_name)
        label = find_point(label)
        for l in label:
            img = add_label_to_img(img, l)
    else:
        return img

    (filepath, tempfilename) = os.path.split(img_name)
    cv2.imwrite("labeledimg" + "/" + tempfilename, img)


def main(img_list, label_dir):
    for i in range(len(img_list)):
        label_file_name = get_label_file_name(img_list[i], label_dir)
        print(img_list[i])
        show_img_with_label(img_list[i], label_file_name)


if __name__ == '__main__':

    img_dir = './image'
    label_dir = './label'

    img_list = get_file_name_list('./image', ['.jpg', ])

    main(img_list, label_dir)