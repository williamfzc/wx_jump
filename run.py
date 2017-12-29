from PIL import Image, ImageStat
import os
import numpy as np
import time


def get_pic(_pic_path):
    os.system('adb shell screencap -p /sdcard/wx.png')
    os.system('adb pull /sdcard/wx.png {}'.format(_pic_path))


def calculate_time(dis):
    return int(dis * 710 / 474.6)


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

        distance = (get_distance((self_x, self_y), (des_x, des_y+75)))

        print(distance)
        t = calculate_time(distance)
        print(t)

        # os.system('adb shell input swipe 100 100 100 100 {}'.format(t))
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
            rgb = (img.getpixel((x, y)))
            if rgb_compare(self_rgb, rgb):
                point_list.append((x, y))

    # return sum([each[0] for each in point_list])/len(point_list),\
    #        sum([each[1] for each in point_list])/len(point_list)
    return point_list[-1][0] - 20, point_list[-1][1]

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
    img = img.convert('1')
    # 计算均值
    mean = ImageStat.Stat(img).mean[0]
    # 二值化
    img = img.point(lambda x: 0 if x < mean else 255)

    img.save('temp1.png')

    data = np.array(img.getdata())
    data.resize(1050, 1080)

    # row and times
    max_num = (0, 0)
    for index, row in enumerate(data):
        temp = longest_list(row.tolist())[1]
        max_num = (index, temp) if temp > max_num[1] else max_num

    des_y = max_num[0]
    temp = longest_list(data[max_num[0]])
    des_x = (temp[1] + sum(temp))/2
    return des_x, des_y


def longest_list(_list):
    max_list = (0, 0)
    for index, each in enumerate(_list):
        if each == 0:
            count = 0
            begin_point = index
            for i in _list[index+1:]:
                if i != 0:
                    break
                else:
                    count += 1
            max_list = (begin_point, count) if count > max_list[1] else max_list
    return max_list


analyse_pic('temp.png')