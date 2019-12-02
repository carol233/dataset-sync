# coding:utf-8

import os
import random
import threading
import threadpool

ALL_PATH = "data/family/drebin10family"
yPATH = "data/drebin_dex/malfeature_picked"
xPATH = "data/drebinTest/dex_repeated"
yPICKED_PATH = "data/family/drebin_dex_y"
xPICKED_PATH = "data/family/drebin_dex_x"


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

class Analysis:
    def __init__(self):
        self.max_jobs = 15
        self.lock = threading.Lock()
        self.total_insert = 0
        self.feature_hash = {}


    def process_one(self, args):
        file = args
        try:
            filename = os.path.split(file)[-1]
            if os.path.exists(os.path.join(yPATH, filename)):
                os.system("cp " + file + " " + os.path.join(yPICKED_PATH, filename))
            elif os.path.exists(os.path.join(xPATH, filename)):
                os.system("cp " + file + " " + os.path.join(xPICKED_PATH, filename))

        except Exception as e:
            print(e, file)
            return None


    def process(self):
        files = getFileList(ALL_PATH)
        length = len(files)
        print(length)

        args = [file for file in files]
        pool = threadpool.ThreadPool(self.max_jobs)
        requests = threadpool.makeRequests(self.process_one, args)
        [pool.putRequest(req) for req in requests]
        pool.wait()


    def start(self):
        self.process()


if __name__ == '__main__':
    if not os.path.exists(yPICKED_PATH):
        os .mkdir(yPICKED_PATH)
    if not os.path.exists(xPICKED_PATH):
        os .mkdir(xPICKED_PATH)
    analysis = Analysis()
    analysis.start()

