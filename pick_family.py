# coding:utf-8
import csv
import os
import random
import zipfile
import hashlib
import subprocess
import re
import threadpool
from tempfile import NamedTemporaryFile
import threading


# Global configuration
FAMILYFILE_PATH = "cluster/amd_family.csv"
MOV_PATH = "../data/amddata/"
PICKED_PATH = "../data/family/amd10family"

family_dict = {}
family_count = {}
total_pick = 0
families = []

def getApkList(rootDir, pick_str):
    """
    :param rootDir:  root directory of dataset
    :return: A filepath list of sample
    """
    filePath = []
    for parent, dirnames, filenames in os.walk(rootDir):
        for filename in filenames:
            if pick_str in filename:  # exists .txt
                file = os.path.join(parent, filename)
                filePath.append(file)

    return filePath


def count():
    with open(FAMILYFILE_PATH, 'r') as csvfile:
        csv_reader = csv.reader(csvfile)
        birth_header = next(csv_reader)
        for row in csv_reader:
            sha256 = row[0]
            family = row[1]
            family_dict[sha256] = family
            if family in family_count:
                family_count[family] += 1
            else:
                family_count[family] = 1

def pick_files():
    count1 = 0
    apks = getApkList(MOV_PATH, ".data")
    for apk in apks:
        sha256_num = os.path.split(apk)[-1][:-5]
        sha256 = sha256_num.split('_')[1]
        if sha256 not in family_dict:
            print("not exists!")
            continue
        family = family_dict[sha256]
        if family in families:
            mov_data = apk
            os.system("cp " + mov_data + " " + os.path.join(PICKED_PATH, sha256_num + ".data"))
            count1 += 1
    print("All samples: ", count1)



def main():
    count()
    #keys = family_dict.keys()
    #random.shuffle(keys)
    map_e_to_num_sort_list = sorted(family_count.items(), key=lambda d:d[1], reverse=True)
    sum = 0
    for e in map_e_to_num_sort_list[:10]:
        family = e[0]
        families.append(family)
        num = e[1]
        sum += num

    fam = len(family_count)
    print("sum: ", sum, fam, sum/len(family_dict))

    pick_files()
    f = open("amd_top10", "w")
    for item in families:
        f.write(item)
        f.write("\n")


if __name__ == '__main__':
    if not os.path.exists(PICKED_PATH):
        os.mkdir(PICKED_PATH)
    main()