# coding:utf-8
import os
import csv

AMD_PATH = "/home/public/rmt/amd_apks"
csv_PATH = "amd_family.csv"

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


if __name__ == '__main__':
    files = getApkList(AMD_PATH, ".apk")
    with open(csv_PATH, 'w', newline='') as csvfile:
        spamwriter = csv.writer(csvfile)
        spamwriter.writerow(["sha256", "family"])

    for file in files:
        paths = os.path.split(file)
        family = paths[4]
        sha256 = paths[-1][:-4]
        spamwriter.writerow([sha256, family])

