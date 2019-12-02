# coding:utf-8

import os
import random
import threading
import threadpool

PATH1 = "data/drebinTest/dex_70y"
PATH2 = "data/drebinTest/dex_repeated"
PICKED_PATH = "data/drebinTest/dex_trainset"
SELECT_NUMBER = 0


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
            os.system("cp " + file + " " + os.path.join(PICKED_PATH, filename))

        except Exception as e:
            print(e, file)
            return None


    def process(self):
        files = getFileList(PATH1)
        length = len(files)
        SELECT_NUMBER = int(0.5 * length)

        print("part files ", SELECT_NUMBER)
        select = random.sample(range(0, length), SELECT_NUMBER)

        args = [(files[i]) for i in select]
        pool = threadpool.ThreadPool(self.max_jobs)
        requests = threadpool.makeRequests(self.process_one, args)
        [pool.putRequest(req) for req in requests]
        pool.wait()

        files2 = getFileList(PATH2)
        length2 = len(files2)
        if SELECT_NUMBER < length2:
            select = random.sample(range(0, length2), SELECT_NUMBER)
        else:
            select = range(0, length2)
        args = [(files2[i]) for i in select]
        pool = threadpool.ThreadPool(self.max_jobs)
        requests = threadpool.makeRequests(self.process_one, args)
        [pool.putRequest(req) for req in requests]
        pool.wait()


    def start(self):
        self.process()


if __name__ == '__main__':
    if not os.path.exists(PICKED_PATH):
        os .mkdir(PICKED_PATH)
    analysis = Analysis()
    analysis.start()

