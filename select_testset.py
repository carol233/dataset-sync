# coding:utf-8

# coding:utf-8
import hashlib
import os
import random
import threading
import threadpool

PATH = "data/drebin_dex/malfeature_picked"
PICKED_PATH = "data/drebinTest/dex_testset"
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
    def __init__(self, path):
        self.dir_path = path
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


    def process(self, dataset_path):
        files = getFileList(dataset_path)
        length = len(files)
        SELECT_NUMBER = int(0.3 * length)
        print("total files ", SELECT_NUMBER)
        select = random.sample(range(0, length), SELECT_NUMBER)

        args = [(files[i]) for i in select]
        pool = threadpool.ThreadPool(self.max_jobs)
        requests = threadpool.makeRequests(self.process_one, args)
        [pool.putRequest(req) for req in requests]
        pool.wait()


    def start(self):
        self.process(self.dir_path)


if __name__ == '__main__':
    if not os.path.exists(PICKED_PATH):
        os .mkdir(PICKED_PATH)
    analysis = Analysis(PATH)
    analysis.start()

