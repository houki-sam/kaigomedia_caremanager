import os
import re
import time
import uuid
import datetime

import requests
from bs4 import BeautifulSoup

from parse_tag import Parser

def OutlineHtml2URL(url, interval=3, page_num=True):#知覧ページから対象のURLを取り出す。
    soup = Url2Soup(url, page_num) #urlをsoupに変換
    url_list = OutlineUrl(soup) #記事urlのリストを取り出し
    time.sleep(interval) #一度スリープ
    return url_list


def Url2Soup(url, page_num= True):#urlからhtmlを取り出し、soupへ変換する
    if page_num == True:
        paramater = ""
    elif page_num>1:
        paramater="page={}".format(page_num)
    target_url = "?".join([url, paramater])#記事urlのリストを取り出し
    
    outline_html = requests.get(target_url)
    soup=BeautifulSoup(outline_html.text.encode('utf-8'), "html.parser")#htmlの取り出しとスープへの変換
    return soup


def OutlineUrl(soup):# 一覧ページから詳細ページのurlをリストで返す。
    newest = soup.find("div", attrs={"id": "newest"})
    list_article = newest.find("ul", attrs={"class": "list-article"})
    a_tag = list_article.find_all("a")
    return [x.get('href') for x in a_tag]


def Detail(url): #記事から詳細情報を取り出し辞書型で返す 
    soup = Url2Soup(url, page_num=True) #soup生成
    header = soup.find("div", attrs={"id":"content", "class":"reset"}).find("header") #header情報のsoupを取り出す。
    rp_date = [x.find("time").text for x in header.find_all("li") if x.find("time")!=None][0] #公開日を取り出す。


    tag_list, body_text = Body2Tag(soup)
    parser = Parser()#クラス呼び出し
    overview,facility_and_article_dict = parser.controller(tag_list)#データの読み込み
    news_dict = {
        "url" : url, #該当ページのurl
        "title" : header.find("h1").text, #ページタイトル
        "rp_date" : datetime.datetime.strptime(rp_date ,"%Y-%m-%d"), #公開日
        "overview" : overview
    }#newsテーブルのための情報
    if body_text is not None:
        news_dict["overview"] += body_text

    dictionary = {
        "News" : [news_dict]
    }
    dictionary.update(facility_and_article_dict)
    
    return dictionary#テーブルに対応した辞書を作成


def Body2Tag(soup): #bodyをタグごとに変換
    body = soup.find("div", attrs={"id":"content", "class":"reset"}).find("div",attrs={"class":"body"})
    body_text = body.text
    article = body.find("div",attrs={"class":"page"})
    tag_list = article.find_all(["p","h2"])#記事をタグで分解
    tag_list = Tag2List(tag_list) #[[tag,sentence]...]のリストで返却
    return tag_list, body_text


def Tag2List(tag_list): #タグのリストを２回改行されている部分で分割する
    return_list= []
    for tag in tag_list:
        tag_name = tag.name#タグの情報
        tag_split = re.split(r"(\r\n|\v|\f){2,}", tag.text)#2回改行で分割
        
        for a in tag_split:#分割されたものをリストにいれる
            return_list.append([tag_name,a])
    return return_list

if __name__ == "__main__":
    print(Detail("http://www.care-mane.com/news/10605?btn_id=category&CID=&TCD=0&CP=1"))
    