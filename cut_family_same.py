# coding:utf-8
import csv
import os
import random

csv_path = "/home/zcp/datatest/drebin/cluster/drebin_family.csv"
dict_path = "/home/zcp/datatest/drebin/drebin_top10.txt"
y_dataset_path = "/home/zcp/datatest/data/family/drebin_dex_y"
x_dataset_path = "/home/zcp/datatest/data/family/drebin_dex_x"
all_10_path = "/home/zcp/datatest/data/family/drebin10family"

picked_path = "/home/zcp/datatest/data/family/drebin_dex_xy"

top10family = []
family_dict = {}
count_y = {}
count_10 = {}
family_list = {}


def getApkList(rootDir, pick_str):
    """
    :param rootDir:  root directory of dataset
    :return: A filepath list of sample
    """
    filePath = []
    for parent, dirnames, filenames in os.walk(rootDir):
        for filename in filenames:
            if pick_str in filename:  # exists .data
                file = os.path.join(parent, filename)
                filePath.append(file)
    return filePath


def get_dict(dict_path, cav_path):
    with open(dict_path, 'r') as f1:
        lines = f1.readlines()
        for row in lines:
            top10family.append(row.strip())


    with open(cav_path, 'r') as csvfile:
        csv_reader = csv.reader(csvfile)  # 使用csv.reader读取csvfile中的文件
        birth_header = next(csv_reader)  # 读取第一行每一列的标题
        for row in csv_reader:
            family = row[1]
            sha256 = row[0]
            if family in top10family:
                family_dict[sha256] = family
                if family in count_10:
                    count_10[family] += 1
                else:
                    count_10[family] = 1

                if family in family_list:
                    family_list[family].append(sha256)
                else:
                    family_list[family] = [sha256]


def get_count_y():
    y_apk_list = getApkList(y_dataset_path, ".data")
    for apk in y_apk_list:
        sha256 = os.path.split(apk)[-1][:-5]
        family = family_dict[sha256]
        if family in count_y:
            count_y[family] += 1
        else:
            count_y[family] = 1


def select_xy(all_path, move_to_path):
    for family in family_list:
        one_list = family_list[family]
        SELECT_NUMBER = count_y[family]
        select = random.sample(range(0, len(one_list)), SELECT_NUMBER)
        for i in select:
            select_sample = one_list[i]
            original_path = os.path.join(all_path, select_sample + ".data")
            new_path = os.path.join(move_to_path, select_sample + ".data")
            if os.path.exists(original_path):
                os.system("cp " + original_path + " " + new_path)
            else:
                print(select_sample + " doesn't exist!")


if __name__ == '__main__':
    if not os.path.exists(picked_path):
        os.mkdir(picked_path)
    get_dict(dict_path, csv_path)
    get_count_y()
    count_all = 0
    with open("drebin_top10_count_y.txt", "w") as f2:
        for item in count_y:
            count_all += count_y[item]
            f2.write(item + " " + str(count_y[item]) + " " + str(count_10[item]) + "\n")
    print(count_all)  # 2266

    select_xy(all_10_path, picked_path)








