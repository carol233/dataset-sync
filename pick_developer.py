# coding:utf-8

import os
import zipfile
import hashlib
import subprocess
import re
import threadpool
from tempfile import NamedTemporaryFile
import threading


# Global configuration
DREBIN_PATH = "../../../mnt/storage/yanjie/drebin"
MOV_PATH = "../../../mnt/storage/yanjie/DREBIN_Malfeature"
PICKED_PATH = "../../../mnt/storage/yanjie/drebin_developer/malfeature_picked"
tmp_file = "tmpfile.tmp"
debug = 1


def getApkList(rootDir):
    """
    :param rootDir:  root directory of dataset
    :return: A filepath list of sample
    """
    filePath = []
    for parent, dirnames, filenames in os.walk(rootDir):
        # 三个参数：分别返回 1.父目录 2.所有文件夹名字（不含路径） 3.所有文件名字
        for filename in filenames:  # 输出文件信息
            if ".apk" in filename: # exists .txt
                file = os.path.join(parent, filename)
                filePath.append(file)

    return filePath

class Analysis:
    def __init__(self, path, feature_path):
        self.dir = path
        self.feature_dir = feature_path
        self.max_jobs = 15
        self.lock = threading.Lock()
        self.total_pick = 0
        self.developer = {}


    def process_one(self, args):
        apk = args
        apk_sha256 = os.path.split(apk)[-1][:-4]
        try:
            z = zipfile.ZipFile(apk)

            sign_md5 = "None"
            rsa_files = filter(lambda x: x.endswith("RSA"), z.namelist())
            for rsa_file in rsa_files:
                tmpfile = NamedTemporaryFile(delete=False)
                tmpfile.write(z.open(rsa_file, 'r').read())
                tmpfile.close()
                cmd = "keytool -printcert -file " + tmpfile.name
                output = subprocess.check_output(cmd, shell=True)

                result = re.findall(r'MD5:\s+([0-9A-Z:]+)', str(output))
                if result:
                    sign_md5 = result[0].strip()
            z.close()

            if not sign_md5 == "None":
                self.lock.acquire()
                if not sign_md5 in self.developer:
                    # cp
                    mov_feature = os.path.join(self.feature_dir, apk_sha256 + ".data")
                    os.system("cp " + mov_feature + " " + os.path.join(PICKED_PATH, apk_sha256))
                    self.developer[sign_md5] = 1
                    self.total_pick += 1
                self.lock.release()

        except Exception as e:
            print(e, apk)
            return None


    def process(self, dir):
        apks = getApkList(dir)
        print("total files ", len(apks))
        args = [(apk) for apk in apks]
        pool = threadpool.ThreadPool(self.max_jobs)
        requests = threadpool.makeRequests(self.process_one, args)
        [pool.putRequest(req) for req in requests]
        pool.wait()

    def start(self):
        self.process(self.dir)



if __name__ == '__main__':
    if not os.path.exists(PICKED_PATH):
        os.mkdir(PICKED_PATH)
    analysis = Analysis(DREBIN_PATH, MOV_PATH)
    analysis.start()
    print(analysis.total_pick)