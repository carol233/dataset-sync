# coding:utf-8
import csv
import zipfile
import hashlib
import os
DatasetPath = "/home/public/rmt/amd_apks/"

def getApkList(rootDir):
    """
    :param rootDir:  root directory of dataset
    :return: A filepath list of sample
    """
    filePath = []
    for parent, dirnames, filenames in os.walk(rootDir):
        # 三个参数：分别返回 1.父目录 2.所有文件夹名字（不含路径） 3.所有文件名字
        for filename in filenames:  # 输出文件信息
            if ".apk" in filename:
                file = os.path.join(parent, filename)  # 输出文件路径信息
                filePath.append(file)

    return filePath

def getmd5(apk):
    sha256 = os.path.split(apk)[-1][:-4]
    try:
        # DEX MD5
        dex_md5 = "none"
        z = zipfile.ZipFile(apk)
        if "classes.dex" in z.namelist():
            dex_item = z.open("classes.dex", 'r')
            dex_md5 = hashlib.md5(dex_item.read()).hexdigest()
        z.close()

        return [sha256, dex_md5]
    except Exception as e:
        print(e, apk)
        return None

if __name__ == '__main__':
    apks = getApkList(DatasetPath)
    csv_file = open('amddexmd5.csv', 'w', newline='')
    writer = csv.writer(csv_file)
    for apk in apks:
        result = getmd5(apk)
        if result:
            writer.writerow(result)

    csv_file.close()
