# coding:utf-8

import sqlite3
import os
import zipfile
import hashlib
import subprocess
import re
import threadpool
import multiprocessing
from tempfile import NamedTemporaryFile
import threading

API_FEATURE = "G:/yanjie-data/amd_mal_api/"
OPCODE_FEATURE = "G:/yanjie-data/amd_mal_opcode/"

# Global configuration


def getApkList(rootDir):
    """
    :param rootDir:  root directory of dataset
    :return: A filepath list of sample
    """
    filePath = []
    for parent, dirnames, filenames in os.walk(rootDir):
        # 三个参数：分别返回 1.父目录 2.所有文件夹名字（不含路径） 3.所有文件名字
        for filename in filenames:  # 输出文件信息
            if "apidict" in filename:
                file = os.path.join(parent, filename)  # 输出文件路径信息
                filePath.append(file)

    return filePath

class Analysis:
    def __init__(self, database_db):
        self.db_name = database_db
        self.databases = {}
        self.max_jobs = 15
        self.lock = threading.Lock()
        self.total_insert = 0

    def add_database(self, name, path):
        self.databases[name] = path

    def connect_database(self):
        """
        :param database: filepath of database
        :return: sqlite connection
        """

        conn = sqlite3.connect(self.db_name)
        print("Opened database successfully")

        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS DATA
                     (ID INTEGER PRIMARY KEY AUTOINCREMENT,
                      DATASET        TEXT    NOT NULL,
                      PATH           TEXT    NOT NULL,
                      APK_MD5        TEXT    NOT NULL,
                      DEX_MD5        TEXT,
                      OPCODE         TEXT,
                      API            TEXT    
                      );""")
        print("Table created successfully")
        conn.commit()
        self.conn = conn
        self.insert_count = 0
        self.sql_data = []

    def process_one(self, args):
        dataset, dataset_path, apk = args
        apk_name = os.path.split(apk)[-1][:-8]

        try:
            # APK MD5
            apk_md5 = apk_name.split("_")[-1]

            # api MD5
            api_item = open(apk, 'rb')
            api_md5 = hashlib.md5(api_item.read()).hexdigest()
            api_item.close()

            # opcode
            opseq_md5 = "none"
            opcode_file = OPCODE_FEATURE + apk_name + ".opseq"
            if os.path.exists(opcode_file):
                opcode_item = open(opcode_file, 'rb')
                opseq_md5 = hashlib.md5(opcode_item.read()).hexdigest()
                opcode_item.close()
            else:
                print("opseq none!")



            apk_path = os.path.relpath(apk, dataset_path)
            dex_md5 = ""

            res = {
                "dataset": dataset,
                "path": apk_path,
                "apk_md5": apk_md5,
                "dex_md5": dex_md5,
                "opcode": opseq_md5,
                "api": api_md5
            }
            # print(res)
            return res
        except Exception as e:
            print(e, apk)
            return None

    def save_result(self, request, res):
        # if catch exception
        if not res:
            return

        self.lock.acquire()
        self.total_insert += 1
        if self.total_insert % 10 == 0:
            print(self.total_insert)

        if self.insert_count > 400:
            row = (res['dataset'], res['path'], res['apk_md5'],
                   res['dex_md5'], res['opcode'], res['api'])
            self.sql_data.append(row)
            sql = "INSERT INTO DATA(DATASET, PATH, APK_MD5, DEX_MD5, OPCODE, API) VALUES(?,?,?,?,?,?)"
            cursor = self.conn.cursor()
            cursor.executemany(sql, self.sql_data)
            self.conn.commit()
            self.sql_data = []
            self.insert_count = 0
        else:
            self.insert_count += 1
            row = (res['dataset'], res['path'], res['apk_md5'],
                   res['dex_md5'], res['opcode'], res['api'])
            self.sql_data.append(row)

        self.lock.release()

    def process(self, dataset, dataset_path):
        apks = getApkList(dataset_path)
        print("total files ", len(apks))
        args = [([dataset, dataset_path, apk]) for apk in apks]
        pool = threadpool.ThreadPool(self.max_jobs)
        requests = threadpool.makeRequests(self.process_one, args, self.save_result)
        [pool.putRequest(req) for req in requests]
        pool.wait()


    def start(self):
        self.connect_database()
        for name in self.databases:
            self.process(name, self.databases[name])

    def close(self):
        self.conn.close()

if __name__ == '__main__':
    analysis = Analysis('dataset.db')
    analysis.add_database("AMD", API_FEATURE)
    analysis.start()
