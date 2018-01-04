from PIL import Image, ImageFilter, ImageDraw
import os
import numpy as np
import time
import random

# 该数值为1080x1920上的，可能需要微调
# 调整方法：
# 先把下方的DEVICE_SCREEN参数改成你手机的分辨率
# 用adb命令 ‘adb shell input swipe 580 1600 580 1600 XXX’ 尝试跳第一个点，记录准确的XXX
# DISTANCE_ARG 为 XXX 除以 跳第一个点算出来的距离
# 例如，我运行第一遍算出来的distance为562.5，记录到的XXX为720
# 那么此处的DISTANCE_ARG 为 720/562.5 = 1.28
# 还没在很多机型上试过，后期会将该过程封装起来，目前大概是这么调整
DISTANCE_ARG = 1.3915
# 设备型号
DEVICE_SCREEN = (1080, 1920)
# 每次跳的停等时间，如果前期纪录较低建议设为2以防止“超越”字样的影响
WAIT_TIME = 2

# ----------------------------------------------------------

# 临时文件位置
TEMP_FILE_PATH = 'temp.png'
# 棋子底端中心点到棋子边缘的距离
CHESS_WIDTH = int(DEVICE_SCREEN[0] * 0.032407)
# 屏蔽区域厚度
IGNORE_HEIGHT = (int(DEVICE_SCREEN[1] / 4), int(DEVICE_SCREEN[1] / 2))
# 棋子的RGB数值，可能因为设备不同有偏差，可能需要微调
SELF_RGB = (62, 56, 79)


def get_pic(_pic_path: '临时图片路径'):
    """ 从设备中获取截图 """
    os.system('adb shell screencap -p /sdcard/wx.png')
    os.system('adb pull /sdcard/wx.png {}'.format(_pic_path))


def calculate_time(dis: '距离'):
    """ 根据距离计算时间 """
    return int(dis * DISTANCE_ARG)


def get_distance(point1, point2):
    """ 计算两点间距离 """
    draw = ImageDraw.Draw(Image.open('temp.png'))
    draw.arc((point2[0], point2[1], point2[0] + 20, point2[1] + 20), 0, 360, fill=150)

    return ((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2) ** 0.5


def get_self_position(_img_path: '临时图片路径'):
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


def get_des_position(_img_path: '临时图片路径', _self_point: '起始点坐标'):
    """ 获取目标点位置 """
    _img = Image.open(_img_path)
    # 两次边缘检测
    _img = _img.filter(ImageFilter.FIND_EDGES)
    _img = _img.filter(ImageFilter.FIND_EDGES)
    # 2 value
    _img = _img.convert('1')
    _img.save('temp1.png')
    # 排除顶端的干扰
    _img = np.array(_img)[IGNORE_HEIGHT[0]:]
    # 按行扫描图片
    for index, each in enumerate(_img):
        old_line = _img[index-1]
        # 如果有变化说明检测到顶端
        if (each[1:-1] - old_line[1:-1]).any():
            # black line
            if any(map(lambda x: list(x).count(True) > int(len(each)/2), (each, old_line))):
                continue
            else:
                des_x = _get_des_x(each, old_line)
                des_y = _get_des_y(index, des_x, _img)
                if abs(des_x - self_point[0]) < CHESS_WIDTH * 2:
                    continue
                else:
                    break
    else:
        raise ValueError('Something error.')
    return des_x, des_y


def _get_des_x(line1, line2):
    """ 获取目标点横坐标，通过前后行的差异匹配 """
    for i, a in enumerate(zip(line1[1:-1], line2[1:-1])):
        if a[0] != a[1]:
            return i + 1
    else:
        raise ValueError('Nothing different.')


def _get_des_y(_cur_row: '目标顶端所在行', _des_x: '目标点横坐标', _img: '图片矩阵'):
    """ 目标顶端从上往下扫描，如果右侧边缘不继续递增说明到达边界 """
    _rows = _img[_cur_row:]
    _des_x += list(_rows[0][_des_x::]).index(False)
    for row_num, each_row in enumerate(_rows[1:]):
        _next = list(_rows[row_num+1][_des_x:]).index(True) if True in list(_rows[row_num+1][_des_x:]) else 0
        if _next > 30:
            _next = list(_rows[row_num+2][_des_x:]).index(True)
            if _next > 30:
                return row_num + IGNORE_HEIGHT[0] + _cur_row + 1
            else:
                _des_x += _next
        elif _next == 0:
            _des_x += 1
        else:
            _des_x += _next
        if _des_x >= DEVICE_SCREEN[0]:
            return row_num + IGNORE_HEIGHT[0] + _cur_row + 1
    else:
        raise ValueError('NO DES POINT FOUND.')


def print_log(_self_point, _des_point, _distance, _t):
    """ 打印计算结果方便调试 """
    print('self location: {}, {}'.format(_self_point[0], _self_point[1]))
    print('des location: {}, {}'.format(_des_point[0], _des_point[1]))
    print('x distance: {}'.format(_distance))
    print('press time: {}'.format(_t))


def apply_to_adb(_t: '长按时间'):
    """ 用adb操作手机 """
    r_x, r_y = random.uniform(DEVICE_SCREEN[0]/2, DEVICE_SCREEN[0]/2 + 100), \
               random.uniform(DEVICE_SCREEN[1]/6, DEVICE_SCREEN[1]/6 - 100)
    os.system('adb shell input swipe {} {} {} {} {}'.format(r_x, r_y, r_x, r_y, _t))
    time.sleep(WAIT_TIME + random.random())


if __name__ == '__main__':
    while True:
        # get screen pic
        get_pic(TEMP_FILE_PATH)

        # get self location
        self_point = get_self_position(TEMP_FILE_PATH)

        # get des location
        des_point = get_des_position(TEMP_FILE_PATH, self_point)

        # get distance
        distance = get_distance(self_point, des_point)

        # cal press time
        t = calculate_time(distance)

        # print log
        print_log(self_point, des_point, distance, t)

        # DO
        apply_to_adb(t)
