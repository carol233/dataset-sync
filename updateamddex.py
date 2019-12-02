# coding:utf-8
import csv
import sqlite3
import os
import zipfile
import hashlib
import threadpool
import threading
DatasetPath = "/home/public/rmt/amd_apks/"
csv_path= "amddexmd5.csv"
apks = {}

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
        dataset, dataset_path, sha256 = args
        res = {
                "dex_md5": apks[sha256],
                "condition": "%" + sha256 + "%"
        }
        return res

    def save_result(self, request, res):
        # if catch exception
        if not res:
            return

        self.lock.acquire()
        self.total_insert += 1
        if self.total_insert % 10 == 0:
            print(self.total_insert)

        if self.insert_count > 400:
            row = (res['dex_md5'], res['condition'])
            self.sql_data.append(row)
            sql = """
            UPDATE DATA
            SET DEX_MD5 = ?
            WHERE PATH like ?
            """
            # sql = "INSERT INTO DATA(DATASET, PATH, APK_MD5, DEX_MD5, OPCODE, API) VALUES(?,?,?,?,?,?)"
            cursor = self.conn.cursor()
            cursor.executemany(sql, self.sql_data)
            self.conn.commit()
            self.sql_data = []
            self.insert_count = 0
        else:
            self.insert_count += 1
            row = (res['dex_md5'], res['condition'])
            self.sql_data.append(row)

        self.lock.release()

    def getpairs(self, csvfile):
        fr = open(csvfile, "r")
        reader = csv.reader(fr)
        for item in reader:
            apks[item[0]] = item[1]

    def process(self, dataset, dataset_path):
        self.getpairs(csv_path)
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
    analysis.add_database("AMD", DatasetPath)
    analysis.start()
