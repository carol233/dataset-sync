# coding:utf-8

import os
import random
import threading
import threadpool

PATH = "data/DREBIN_Goodfeature_picked"
list_PATH = "data/goodware_drebin/dextestset"
PICKED_PATH = "data/goodware_drebin/dextrainset"
SELECT_NUMBER = 2492
RANOM_NUMBER = SELECT_NUMBER + 1000


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
        self.total_pick = 0
        self.feature_hash = {}


    def process_one(self, args):
        file = args
        try:
            self.lock.acquire()
            if self.total_pick > SELECT_NUMBER:
                self.lock.release()
                return None
            self.lock.release()

            filename = os.path.split(file)[-1]

            if os.path.exists(os.path.join(list_PATH, filename)):
                print("exists!")
                return None

            os.system("cp " + file + " " + os.path.join(PICKED_PATH, filename))

            self.lock.acquire()
            self.total_pick += 1
            self.lock.release()

        except Exception as e:
            print(e, file)
            return None


    def process(self, dataset_path):
        files = getFileList(dataset_path)
        length = len(files)
        print("total files ", length)
        select = random.sample(range(0, length), RANOM_NUMBER)

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

