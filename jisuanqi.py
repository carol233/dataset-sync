# coding:utf-8

DICT = {
    "diliao":5,
    "yezhi":2.99,
    "xiebang":2.89,
    "doufu":2.79,
    "yangjuan":5.79,
    "niujuan":10.98,
    "wudongmian":1.69,
    "yubing":3.89,
    "mianjin":1.49,
    "niurou":3
}

chufangzhi = 2.49

shange = 127 - 5 - 2.99 - 0.5 * (DICT["yubing"] + DICT["mianjin"] + DICT["niurou"])

xiaomei = -1.5



if __name__ == '__main__':
    sanren = 0.0
    for item in DICT:
        sanren += DICT[item]

    pingjun = sanren / 3.0
    print("pingjun:", pingjun)

    shange2me = pingjun + shange + chufangzhi * 0.5
    print("shange:", shange2me)

    xiaomei2me = pingjun + xiaomei
    print("xiaomei:", xiaomei2me)
