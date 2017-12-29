from PIL import Image, ImageStat
import os
import numpy as np
import time
import scipy.signal as signal
import matplotlib.pyplot as plt


def get_pic(_pic_path):
    os.system('adb shell screencap -p /sdcard/wx.png')
    os.system('adb pull /sdcard/wx.png {}'.format(_pic_path))


def calculate_time(dis):
    return int(dis * 710 / 436.165)


def analyse_pic(_pic_path):

    while True:
        get_pic('temp.png')

        img = Image.open(_pic_path)
        img = img.crop((0,0, 1080,1050))

        # get self location
        self_x, self_y = get_self_position(img)

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
    return point_list[-1][0], point_list[-1][1]


def rgb_compare(a, b):
    for i in range(3):
        if abs(a[i] - b[i]) < 5:
            continue
        else:
            return False
    else:
        return True


def get_des_position(img):
    # 灰度图
    img = img.convert('L')
    # Laplace算子
    suanzi1 = np.array([[0, 1, 0],
                        [1, -4, 1],
                        [0, 1, 0]])
    img = signal.convolve2d(img, suanzi1, mode="same")
    img = (img / float(img.max())) * 255
    img[img > img.mean()] = 255
    img[img <= img.mean()] = 0

    _row = 0
    for index, row in enumerate(img[::-1]):
        if list(row).count(0) == 4:
            _row = index
            break
    if _row > 500:
        for index, row in enumerate(img[::-1]):
            if list(row).count(0) == 5:
                _row = index
                break
    des_y = 1050 - _row

    des_row = list(img[des_y])[1:-1]
    des_x = (des_row.index(0) + len(des_row) - des_row[::-1].index(0)) / 2

    img = Image.fromarray(img)
    img.show()

    return des_x, des_y


analyse_pic('temp.png')