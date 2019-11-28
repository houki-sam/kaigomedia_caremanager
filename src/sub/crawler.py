import os
import time
import uuid

import bs4
import MySQLdb
import requests

from system import *


#スクレイピングする際のベースのURL
Url = "http://www.care-mane.com/news/6/"

#クローラー
class Crawler(object):
    def __init__(self):
        #接続情報
        host = "db"
        user = os.environ["MYSQL_USER"]
        password = os.environ["MYSQL_PASSWORD"]
        port = os.environ["PORT"]
        db = os.environ["MYSQL_DATABASE"]

        self.conn = MySQLdb.connect(
            host = 'db',
            user = "user",
            port = 3306,
            passwd = "password",
            db = "sample_db",
            charset="utf8"
            )
        self.cur = self.conn.cursor()
    

    #　接続を切るための関数
    def close(self):
        self.cur.close()
        self.conn.close()

   
    def insert(self,uuid4,table_name, list_dictionary):
        for dictionary in list_dictionary:
            key = [x for x in dictionary.keys()] #テーブルに挿入する変数
            value = [dictionary[x] for x in key] #代入する値
            #uuidを追加
            key.append("id")
            value.append(uuid4)
            #sql文を作成
            sql = "insert into {}({}) values({})".format(table_name, ",".join(key), ",".join(["%s"]*len(key)))
            self.cur.execute(sql, tuple(value))


    def controller(self,interval,debug = True):#新造部
        self.page_num = 1 #一覧ページの検索ページ

        while True:
            outline_url = OutlineHtml2URL(Url,interval,self.page_num)#一覧ページの対象記事のurlをとってくる

            if len(outline_url) == 0:
                print("記事がないので終了します。")
                break #最後のページまで行った時の終了条件
            
            for url in outline_url:
                u4 = str(uuid.uuid4()) #uuid4の作成
                try:
                    result = Detail(url) #記事の情報を取り出したものを持ってくる。
                    for key, values in result.items():
                        self.insert(u4,key,values)
                    self.conn.commit()
                    time.sleep(2)
                except:
                    time.sleep(10)
                    print("失敗")
            self.page_num += 1


def is_exists(cur, value):
    cur.execute(
        "SELECT EXISTS (SELECT * FROM  WHERE url = '%s')" % value)
    return cur.fetchone() is not None  
    
def main():
    a=Crawler()
    a.controller(5)


    

main()