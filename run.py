from PIL import Image, ImageStat, ImageFilter, ImageDraw
import os
import numpy as np
import time
import scipy.signal as signal
import matplotlib.pyplot as plt


def get_pic(_pic_path):
    os.system('adb shell screencap -p /sdcard/wx.png')
    os.system('adb pull /sdcard/wx.png {}'.format(_pic_path))


def calculate_time(dis):
    return int(dis * 710 / 482.44792465094093)


def analyse_pic(_pic_path):

    while True:
        get_pic('temp.png')

        img = Image.open(_pic_path)


        # get self location
        self_x, self_y = get_self_position(img)

        img = img.crop((0, 0, 1080, 900))

        # get des location
        des_x, des_y = get_des_position(img)

        print(self_x, self_y)
        print(des_x, des_y)

        distance = (get_distance((self_x, self_y), (des_x, des_y)))

        print(distance)
        t = calculate_time(distance)
        print(t)

        os.system('adb shell input swipe 100 100 100 100 {}'.format(t))
        time.sleep(2)


def get_distance(point1, point2):
    return ((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)**(1/2)


def get_self_position(img):
    width = img.size[0]
    height = img.size[1]

    self_rgb = (62, 56, 79)

    point_list = list()
    for x in range(width):
        for y in range(height):
            rgb = img.getpixel((x, y))
            if rgb_compare(self_rgb, rgb):
                point_list.append((x, y))

    # return sum([each[0] for each in point_list])/len(point_list),\
    #        sum([each[1] for each in point_list])/len(point_list)
    return point_list[-1][0], point_list[-1][1]+50


def rgb_compare(a, b):
    for i in range(3):
        if abs(a[i] - b[i]) < 5:
            continue
        else:
            return False
    else:
        return True


def depoint(img):
    pixdata = img.load()
    w,h = img.size
    for y in range(1,h-1):
        for x in range(1,w-1):
            count = 0
            if pixdata[x,y-1] < 15:
                count = count + 1
            if pixdata[x,y+1] < 15:
                count = count + 1
            if pixdata[x-1,y] < 15:
                count = count + 1
            if pixdata[x+1,y] < 15:
                count = count + 1
            if count > 2:
                pixdata[x, y] = 0
    return img


def get_des_position(img):
    img = img.filter(ImageFilter.FIND_EDGES)
    # 灰度图
    img = img.convert('L')
    #
    img = depoint(img)

    img = np.array(img)
    img[img > 2] = 255
    img[img <= 2] = 0

    # img = Image.fromarray(img)
    # img.save('temp1.png')

    _row = 0
    for index, row in enumerate(img[::-1]):
        if list(row).count(255) in range(2, 8):
            _row = index
            break
    # if _row > 400:
    #     for index, row in enumerate(img[::-1]):
    #         if list(row).count(255) in range(3, 8):
    #             _row = index
    #             break
    des_y = 900 - _row

    des_row = list(img[des_y])[1:-1]
    front = des_row.index(255)
    back = len(des_row) - des_row[::-1].index(255)
    if back - front < 50:
        des_x = des_row.index(255) + 210
    else:
        des_x = (front + back) / 2
    # des_x = des_row.index(255) + 210

    img = Image.fromarray(img)
    draw = ImageDraw.Draw(img)
    draw.arc((des_x, des_y, des_x + 20, des_y + 20), 0, 360, fill=150)
    img.save('temp1.png')

    return des_x, des_y


analyse_pic('temp.png')