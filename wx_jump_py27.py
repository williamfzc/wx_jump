# -*- coding:utf-8 -*-
from PIL import Image, ImageFilter
import os
import numpy as np
import time

# 该数值为1080x1920上的，可能需要微调
DISTANCE_ARG = 1.32
# 棋子的RGB数值，可能因为设备不同有偏差，可能需要微调
SELF_RGB = (62, 56, 79)
# 设备型号
DEVICE_SCREEN = (1080, 1920)
# 临时文件位置
TEMP_FILE_PATH = 'temp.png'
# 菱形顶端到中心点的猜测值
DIAMAND_DISTANCE = 50
# 棋子底端中心点到棋子边缘的距离
CHESS_WIDTH = 25


def get_pic(_pic_path):
    """ 从设备中获取截图 """
    os.system('adb shell screencap -p /sdcard/wx.png')
    os.system('adb pull /sdcard/wx.png {}'.format(_pic_path))


def calculate_time(dis):
    """ 根据距离计算时间 """
    return int(dis * DISTANCE_ARG)


def get_distance(point1, point2):
    """ 计算距离 """
    return ((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2) ** 0.5


def get_self_position(_img_path):
    """ 获取自身位置 """
    _img = Image.open(_img_path)

    point_list = list()
    for x in range(DEVICE_SCREEN[0]):
        for y in range(DEVICE_SCREEN[1]):
            each_point = _img.getpixel((x, y))
            if rgb_compare(SELF_RGB, each_point):
                point_list.append((x, y))

    return point_list[-1][0]-CHESS_WIDTH, point_list[-1][1]


def rgb_compare(a, b):
    """ 两个RGB点的比较 """
    for i in range(3):
        if abs(a[i] - b[i]) >= 5:
            return False
    else:
        return True


def get_des_position(_img_path):
    """ 获取目标点位置 """
    _img = Image.open(_img_path)
    # 两次边缘检测
    _img = _img.filter(ImageFilter.FIND_EDGES)
    _img = _img.filter(ImageFilter.FIND_EDGES)
    # 2 value
    _img = _img.convert('1')
    _img.save('temp1.png')
    # 排除顶端的干扰
    _img = np.array(_img)[300:]
    # 按行扫描图片
    for index, each in enumerate(_img):
        old_line = _img[index-1]
        # 如果有变化说明检测到顶端
        if (each - old_line).any():
            # black line
            if any(map(lambda x: list(x).count(True) > len(each)/2, (each, old_line))):
                continue
            else:
                des_x = _get_des_x(each, old_line)
                des_y = index + 300 + DIAMAND_DISTANCE
                break
    else:
        raise ValueError('Something error.')
    return des_x, des_y


def _get_des_x(line1, line2):
    for i, a in enumerate(zip(line1, line2)):
        if a[0] != a[1]:
            return i
    else:
        raise ValueError('Nothing different.')


def fix_distance(_self_point, _des_point, _origin_dis):
    if abs(_self_point[0] - _des_point[0]) < 100:
        # 取巧：如果头顶比菱形顶端高意味着两者距离很近，此处为一个近似值
        return 200
    else:
        return _origin_dis


def print_log(_self_point, _des_point, _distance, _t):
    """ 打印计算结果方便调试 """
    print 'self location: {}, {}'.format(_self_point[0], _self_point[1])
    print 'des location: {}, {}'.format(_des_point[0], _des_point[1])
    print 'x distance: {}'.format(_distance)
    print 'press time: {}'.format(_t)


def apply_to_adb(_t):
    """ 用adb操作手机 """
    os.system('adb shell input swipe 580 1600 580 1600 {}'.format(_t))
    time.sleep(1)


if __name__ == '__main__':
    while True:
        try:
            # get screen pic
            get_pic(TEMP_FILE_PATH)

            # get self location
            self_point = get_self_position(TEMP_FILE_PATH)

            # get des location
            des_point = get_des_position(TEMP_FILE_PATH)

            # get distance
            distance = get_distance(self_point, des_point)

            # fix distance
            distance = fix_distance(self_point, des_point, distance)

            # cal press time
            t = calculate_time(distance)

            # print log
            print_log(self_point, des_point, distance, t)

            # DO
            apply_to_adb(t)

        except IndexError:
            # 截图方便debug
            get_pic('error{}.png'.format(str(time.time()).split('.')[0]))
            # 重新开始
            apply_to_adb(200)
