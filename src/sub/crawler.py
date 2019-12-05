import os
import re
import time
import uuid
import itertools

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
    
    def parsing(self):
        sql = "select id, overview from News"
        self.cur.execute(sql)
        data2=self.cur.fetchall()
        #pattern = "「.*?（.*?[市|町|村|区].*?）」|「[^「」]*?」（.*?[市|町|村|区].*?）"
        pattern = "「[^「」]*」（(?=.*市|町|村|区.*)[^（）]*）"
        data = [[x[0],re.findall(pattern, x[1]) ]
            for x in data2 if len(re.findall(pattern, x[1]))!=0]
        dataset=[]
        for x in data:
            for y in x[1]:
                dataset.append([x[0],y])
        dataset = [x for x in dataset if re.search(r".*?[市|町|村|区].*?", x[1])]
        dataset2=[]
        for x in dataset:
            words1 = [y for y in re.split(r'「|」|（|）|、|,', x[1]) if y!='']
            words2 = [y for y in words1[1:] if re.search("市|町|村|区",y)]
            for z in [y for y in words2 if y!='']:
                dataset2.append([x[0],None,words1[0],words2[0],None])
            
        """  
        sql2= "delete from Facility where id in({})".format(",".join(["'"+x[0]+"'" for x in dataset2]))
        self.cur.execute(sql2)
        self.conn.commit()
        """
        arr = list(map(list, set(map(tuple, dataset2))))
        self.cur.executemany("insert into Facility values(%s,%s,%s,%s,%s)",arr)
        self.conn.commit()
        print(arr)
            

def hh(x):
    if len(x)>0:
        return True
    else:
        return False
       


def is_exists(cur, value):
    cur.execute(
        "SELECT EXISTS (SELECT * FROM  WHERE url = '%s')" % value)
    return cur.fetchone() is not None  
    
def main():
    a=Crawler()
    #a.controller(5)
    a.parsing()


    

main()