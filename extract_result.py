# coding:utf-8
import csv
import re
import os

result_path = "results"

def getFileList(rootDir):
    """
    :param rootDir:  root directory of dataset
    :return: A filepath list of sample
    """
    filePath = []
    for parent, dirnames, filenames in os.walk(rootDir):
        for filename in filenames:
            file = os.path.join(parent, filename)
            filePath.append(file)
    return filePath


def solve(file):
    line = []
    names = os.path.split(file)[-1]
    columns = names.split("_")
    # amd_api_5_SVM
    dataset = columns[0]
    level = columns[1]
    number = columns[2]
    algorithm = columns[3]
    line.append(dataset)
    line.append(level)
    line.append(algorithm)
    line.append(number)

    f = open(file, 'r')
    content = f.read()
    preci = recall = f1 = ""
    precig = recallg = f1g = ""
    good = "none"
    mal1 = re.findall(r'Malware\s+([0-9.]+)\s+([0-9.]+)\s+([0-9.]+)\s+', content)
    if mal1:
        preci = mal1[0][0]
        recall = mal1[0][1]
        f1 = mal1[0][2]
    good1 = re.findall(r'Goodware\s+([0-9.]+)\s+([0-9.]+)\s+([0-9.]+)\s+', content)
    if good1:
        precig = good1[0][0]
        recallg = good1[0][1]
        f1g = good1[0][2]
    line.append(preci)
    line.append(recall)
    line.append(f1)
    line.append(precig)
    line.append(recallg)
    line.append(f1g)
    f.close()
    return line



if __name__ == '__main__':
    files = getFileList(result_path)
    csv_file = open('results_withgood.csv', 'w', newline='')
    headline = ["dataset", "level", "algorithm", "number", "mal_pre", "mal_recall", "mal_f1",
                "good_pre", "good_recall", "good_f1"]
    writer = csv.writer(csv_file)
    writer.writerow(headline)

    for file in files:
        line = solve(file)
        if line[2] in ["SVM", "DT", "RF"]:
            writer.writerow(line)

    csv_file.close()

