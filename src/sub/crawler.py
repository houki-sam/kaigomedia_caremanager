import os
import time
import uuid

import bs4
import MySQLdb
import requests

from system import *


#スクレイピングする際のベースのURL
Url = "http://www.care-mane.com/news/6/"

class Crawler(object):
    def __init__(self):
        #接続情報
        host = "db"
        user = os.environ["MYSQL_USER"]
        password = os.environ["MYSQL_PASSWORD"]
        port = os.environ["MYSQL_PORT"]
        db = os.environ["MYSQL_DATABASE"]

        self.conn = MySQLdb.connect(
            host = host,
            user = user,
            port = int(port),
            passwd = password,
            db = db
        )
        self.cur = self.conn.cursor()
    
    #　接続を切るための関数
    def close(self):
        self.cur.close()
        self.conn.close()

    # 存在しない場合テーブルを作成する
    def create_table(self, file_path):
        self.cur.execute(open(file_path, "r").read())
        self.conn.commit()

    def insert_article(self,dictionary):
        #テーブルに挿入する変数
        detail_info_list = dictionary["article_list"]
        uuid4 = dictionary["id"]
        #上記のリストにuuidを追加する
        for detail_info in detail_info_list: 
            values = tuple([uuid4] + detail_info)
            #sql文を作成
            sql = "insert into article values({})".format(",".join(["%s"]*len(values)))
            self.cur.execute(sql,values)

    def insert_facility(self,dictionary):
        #テーブルに挿入する変数
        facility_info_list = dictionary["facility_list"]
        uuid4 = dictionary["id"]
        #上記のリストにuuidを追加する
        main_key = ["title", "name", "address", "bussiness_form"]
        for facility_info in facility_info_list:
            values = [facility_info[x] for x in main_key]
            values = tuple([uuid4] + values)
            #sql文を作成
            sql = "insert into facility values({})".format(",".join(["%s"]*len(values)))
            self.cur.execute(sql,values)
    
    def insert_news(self,dictionary):
         #テーブルに挿入する変数
        main_key = ["id","title","url", "rp_date", "overview"]
        #上記のリストにuuidを追加する
        values = tuple([dictionary[x] for x in main_key])
        #sql文を作成
        sql = "insert into news values({})".format(",".join(["%s"]*len(values)))

        self.cur.execute(sql,values)
    
    def controller(self,interval):
        # ページの初期化
        page_num = 1
        while True:
            flag = False
            outline_url = OutlineHtml2URL(Url,interval,page_num)
            if len(outline_url) == 0:
                print("finish")
                break
            for url in outline_url:
                info = Detail(url)
                """ß
                if is_exists(self.cur, info["url"]):
                    flag = True
                    break
                """
                uuid4 = str(uuid.uuid4())
                info["id"] = uuid4
                self.insert_news(info)
                self.insert_facility(info)
                self.insert_article(info)
                self.conn.commit()
                time.sleep(interval)
            if flag:
                print("終了")
                break

            page_num += 1


def is_exists(cur, value):
    cur.execute(
        "SELECT EXISTS (SELECT * FROM public.news WHERE url = '%s')" % value)
    return cur.fetchone() is not None  
    
def main():
    a=Crawler()
    

main()