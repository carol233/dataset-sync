# coding:utf-8

import sqlite3
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
Min = 1
Max = 40

datasets = ["drebin", "AMD", "rmvdroid", "genome"]

class Analysis:
    def __init__(self, database_db):
        self.db_name = database_db


    def connect_database(self):
        """
        :param database: filepath of database
        :return: sqlite connection
        """
        conn = sqlite3.connect(self.db_name)
        print("Opened database successfully")
        self.conn = conn
        self.cu = self.conn.cursor()

    def select_dex(self, ds):
        """
        select * from (select count(*) as num from
        DATA where dataset = ? and dex_md5 != "none" group by dex_md5) where num > 1 order by num desc
        """
        sql = """
            select * from (select count(*) as num from
            DATA where dataset = (?) and dex_md5 != "" and dex_md5 != "none" group by dex_md5) where num > ? and num < ? order by num desc
        """
        cursor = self.conn.cursor()
        cursor.execute(sql, (ds, Min, Max))
        values = cursor.fetchall()
        # [(3), (4)]
        values = [a[0] for a in values]
        return values

    def select_opcode(self, ds):
        """
        select * from (select count(*) as num from
        DATA where dataset = ? and dex_md5 != "none" group by dex_md5) where num > 1 order by num desc
        """
        sql = """
            select * from (select count(*) as num from
            DATA where dataset = (?) and OPCODE != "" and OPCODE != "none"  group by OPCODE) where num > ? and num < ? order by num desc
        """
        cursor = self.conn.cursor()
        cursor.execute(sql, (ds, Min, Max))
        values = cursor.fetchall()
        # [(3), (4)]
        values = [a[0] for a in values]
        return values

    def select_api(self, ds):
        """
        select * from (select count(*) as num from
        DATA where dataset = ? and dex_md5 != "none" group by dex_md5) where num > 1 order by num desc
        """
        sql = """
            select * from (select count(*) as num from
            DATA where dataset = (?) and API != "" and API != "none" group by API) where num > ? and num < ? order by num desc
        """
        cursor = self.conn.cursor()
        cursor.execute(sql, (ds, Min, Max))
        values = cursor.fetchall()
        # [(3), (4)]
        values = [a[0] for a in values]
        return values


    def start(self):
        self.connect_database()

        titledrebin = "Drebin Dataset"
        titleamd = "AMD Dataset"
        titlermv = "RmvDroid Dataset"
        titlegenome = "Genome Dataset"

        plt.figure(figsize=(12, 12))  # 创建画布
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2)
        for item in datasets:
            dex_v = self.select_dex(item)
            opseq_v = self.select_opcode(item)
            api_v = self.select_api(item)
            len_dex = len(dex_v)
            len_opseq = len(opseq_v)
            len_api = len(api_v)
            max_len = max(len_dex, len_opseq, len_api)
            all_data = {
                "Dex": dex_v + [None] * (max_len - len_dex),
                "Opcode seq": opseq_v + [None] * (max_len - len_opseq),
                "API call": api_v + [None] * (max_len - len_api)
            }
            columns = ["Dex", "Opcode seq", "API call"]

            if item == "drebin":
                title = titledrebin
                df = pd.DataFrame(all_data, columns=columns)
                df.plot.box(title=title, ax=ax1)
            elif item == "AMD":
                title = titleamd
                df = pd.DataFrame(all_data, columns=columns)
                df.plot.box(title=title, ax=ax2)
            elif item == "rmvdroid":
                title = titlermv
                df = pd.DataFrame(all_data, columns=columns)
                df.plot.box(title=title, ax=ax3)
            else:
                title = titlegenome
                df = pd.DataFrame(all_data, columns=columns)
                df.plot.box(title=title, ax=ax4)

        plt.tight_layout()
        plt.savefig("boxplot.pdf")
        plt.close()


    def close(self):
        self.conn.close()

if __name__ == '__main__':
    analysis = Analysis('dataset.db')
    analysis.start()
    analysis.close()


# select PATH, API, count(*) as count from data where dataset="rmvdroid" group by API having count > 200