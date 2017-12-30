# -*- coding:utf-8 -*-
from PIL import Image, ImageFilter
import os
import numpy as np
import time


def get_pic(_pic_path):
    os.system('adb shell screencap -p /sdcard/wx.png')
    os.system('adb pull /sdcard/wx.png {}'.format(_pic_path))


def calculate_time(dis):
    return int(dis * 1.23)


def get_distance(point1, point2):
    return ((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2) ** 0.5


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

    return point_list[-1][0], point_list[-1][1]+50


def rgb_compare(a, b):
    for i in range(3):
        if abs(a[i] - b[i]) < 5:
            continue
        else:
            return False
    else:
        return True


def get_des_position(img):
    img = img.filter(ImageFilter.FIND_EDGES)
    img = img.filter(ImageFilter.FIND_EDGES)
    # 2 value
    img = img.convert('1')
    img.save('temp1.png')
    img = np.array(img)[300:]

    for index, each in enumerate(img):
        old_line = img[index-1]
        if (each - old_line).any():
            # black line
            if list(each).count(True) > len(each)/2 \
                    or list(old_line).count(True) > len(old_line)/2:
                continue
            else:
                des_x = get_des_x(each, old_line)
                des_y = index + 350
                break
    else:
        raise ValueError('Something error.')
    return des_x, des_y


def get_des_x(line1, line2):
    for i, a in enumerate(zip(line1, line2)):
        if a[0] != a[1]:
            return i
    else:
        raise ValueError('Nothing different.')


if __name__ == '__main__':
    while True:
        # get screen pic
        get_pic('temp.png')
        img = Image.open('temp.png')
        # get self location
        self_x, self_y = get_self_position(img)
        # get des location
        des_x, des_y = get_des_position(img)
        # get distance
        distance = get_distance((self_x, self_y), (des_x, des_y))
        # cal press time
        t = calculate_time(distance)
        # print log
        print 'self location: {}, {}'.format(self_x, self_y)
        print 'des location: {}, {}'.format(des_x, des_y)
        print 'x distance: {}'.format(distance)
        print 'press time: {}'.format(t)
        # do
        os.system('adb shell input swipe 100 100 100 100 {}'.format(t))
        time.sleep(1)
