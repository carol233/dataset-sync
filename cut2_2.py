# coding:utf-8

import os
import threadpool
import threading


# Global configuration
MOV_PATH = "data/drebin_dex/malfeature_picked"
list_PATH = "data/drebinTest/dex_testset"
NEW_PATH = "data/drebinTest/dex_70y"

"""
MOV_PATH = "data/DREBIN_Malfeature"
list_PATH = "data/drebin_dex/malfeature_picked"
NEW_PATH = "data/drebinTest/dex_repeated"
"""

def getApkList(rootDir, pick_str):
    """
    :param rootDir:  root directory of dataset
    :return: A filepath list of sample
    """
    filePath = []
    for parent, dirnames, filenames in os.walk(rootDir):
        for filename in filenames:
            if pick_str in filename: # exists .txt
                file = os.path.join(parent, filename)
                filePath.append(file)

    return filePath


class Analysis:
    def __init__(self):
        self.max_jobs = 15
        self.lock = threading.Lock()
        self.total_pick = 0
        self.opseq_md5 = {}


    def process_one(self, args):
        apk = args
        apk_sha256 = os.path.split(apk)[-1]
        try:

            if os.path.exists(os.path.join(list_PATH, apk_sha256)):
                print("exists!")
                return None

            # cp
            mov_feature = os.path.join(MOV_PATH, apk_sha256)
            os.system("cp " + mov_feature + " " + os.path.join(NEW_PATH, apk_sha256))

            self.total_pick += 1


        except Exception as e:
            print(e, apk)
            return None


    def process(self):
        apks = getApkList(MOV_PATH, ".data")
        print("all files ", len(apks))
        args = [(apk) for apk in apks]
        pool = threadpool.ThreadPool(self.max_jobs)
        requests = threadpool.makeRequests(self.process_one, args)
        [pool.putRequest(req) for req in requests]
        pool.wait()

    def start(self):
        self.process()



if __name__ == '__main__':
    if not os.path.exists(NEW_PATH):
        os.mkdir(NEW_PATH)
    analysis = Analysis()
    analysis.start()
    print(analysis.total_pick)