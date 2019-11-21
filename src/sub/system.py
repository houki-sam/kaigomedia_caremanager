import os
import re
import time
import datetime
from operator import itemgetter

import requests
from bs4 import BeautifulSoup


#知覧ページから対象のURLを取り出す。
def OutlineHtml2URL(url, interval=5, page_num=True):
    #urlをsoupに変換
    soup = Url2Soup(url, page_num)
    #休止
    time.sleep(interval)

    #記事urlのリストを取り出し
    url_list = OutlineUrl(soup)
    return url_list

#urlからhtmlを取り出し、soupへ変換する
def Url2Soup(url, page_num):
    # パラメータの作成
    if page_num == True:
        paramater = ""
    elif page_num>1:
        paramater="page={}".format(page_num)
    target_url = "?".join([url, paramater])
    
    #htmlの取り出しとスープへの変換
    outline_html = requests.get(target_url)
    soup=BeautifulSoup(outline_html.text, "html.parser")
    return soup
    
#一覧ページから詳細ページのurlをリストで返す。
def OutlineUrl(soup):
    #最新記事の一覧
    newest = soup.find("div", attrs={"id": "newest"})
    list_article = newest.find("ul", attrs={"class": "list-article"})
    a_tag = list_article.find_all("a")
    url_list = [x.get('href') for x in a_tag]
    return url_list

def DetailHtml(url):
    #データを格納するための辞書
    dictionary = {}
    #soupに変換
    soup = Url2Soup(url, page_num=True)
    
    
    #header情報のsoupを取り出す。
    header = soup.find("div", attrs={"id":"content", "class":"reset"}).find("header")

    #url
    dictionary["url"] = url
    #タイトル
    dictionary["title"] = header.find("h1").text
    #掲載日時
    rp_date = [x.find("time").text for x in header.find_all("li") if x.find("time")!=None][0]
    dictionary["rp_date"] = datetime.datetime.strptime(rp_date ,"%Y-%m-%d")

    #bodyの変換
    body = soup.find("div", attrs={"id":"content", "class":"reset"}).find("div",attrs={"class":"body"})
    body = body.find("div",attrs={"class":"page"})
    body = body.find_all(["p","h2"])
    
    dictionary = Desc2List(body,dictionary)
    return dictionary

def Desc2List(body,dictionary):#bodyは格納データのリスト、dictionaryは情報辞書

    #h2が現れる場所のインデックス
    h2_index = [x for x in range(len(body)) if body[x].name == 'h2']
    h2_index.append(len(body))#便宜上、リストの長さをリストに加える。

    
    detail_info = [] #処分の情報
    dictionary["overview"] = body[0].text #概要の情報


    #h2の情報を先に取り出す。
    for x in range(len(h2_index)-1):
        h2_list = body[h2_index[x]:h2_index[x+1]]
        section_name = h2_list[0].text
        section_body = "".join([x.text for x in h2_list[1:]])
        detail_info.append([section_name, section_body.replace("\r\n","")])
    dictionary["detail_info"] = detail_info

    #h2該当部分は全てリストから削除
    remove_h2 = body[:h2_index[0]]
    target_index = [x for x in range(len(remove_h2)) if re.search('.*・.*：.*', remove_h2[x].text)]
    if len(target_index)>0:
        target = itemgetter(*target_index)(remove_h2)
        other_dictionary = FacilityInfo(target)
        dictionary["facility_info"] = other_dictionary
    else:
        dictionary["facility_info"] = []

    return dictionary

def FacilityInfo(target):

    return_list = []

    #対象部分を上から検索
    if type(target) != tuple:
        target = (target,) 
    for col in target:
        #処分の対象部分を検索
        
        split_col = repr(col.text).replace("'","").split(r"\r\n")
        patterns =  [r".*(施設|事業所|事業者).*"]
        title_list = [split_col[0] for pattern in patterns if re.match(pattern, split_col[0])]
        if len(title_list)>0:
            other_info =Itemize(split_col[1:])
            title_stack = title_list[0]
            other_info["title"] = title_stack
            return_list.append(other_info)
        else:
            if "title_stack" in locals():
                other_info = Itemize(split_col)
                other_info["title"] = title_stack
                return_list.append(other_info)
    return return_list
        


def Itemize(split_col):
    #　結果を返却するための辞書型
    # 全てNoneで初期化済
    dictionary = NewDictionary()

    #　施設名を取り出す。
    #　これは必ず1番目に表在されているためindexで取り出し。
    if len(dictionary)==0:
        dictionary["name"] = re.sub("・","",re.sub(r"(名称|事業所名|運営法人|法人名)：","",split_col[0]))   
        return dictionary

    #施設名以外の要素の特定、抜き出しを行う。 
    for col in split_col[1:]:

        #住所,所在地について
        if re.match(r"\s*・.*(所在地|住所)(：|:)", col):
            dictionary["address"] = re.sub(r"・.*(:|：)","", col)

        #事業形態
        elif re.match(r"・.*(事業形態)(：|:)", col):
            dictionary["bussiness_form"] = re.sub(r"・.*(:|：)","", col)
        
        else:
            print(col)
    return dictionary


def NewDictionary():
    dictionary = {
        "title" : None,
        "name" : None,
        "address" : None,
        "bussiness_form" : None,
    }
    return dictionary
            


def Detail(url):
    #データを格納するための辞書
    dictionary = {}
    #soupに変換
    soup = Url2Soup(url, page_num=True)
    
    
    #header情報のsoupを取り出す。
    header = soup.find("div", attrs={"id":"content", "class":"reset"}).find("header")

    #url
    dictionary["url"] = url
    #タイトル
    dictionary["title"] = header.find("h1").text
    #掲載日時
    rp_date = [x.find("time").text for x in header.find_all("li") if x.find("time")!=None][0]
    dictionary["rp_date"] = datetime.datetime.strptime(rp_date ,"%Y-%m-%d")

    #bodyの変換
    body = soup.find("div", attrs={"id":"content", "class":"reset"}).find("div",attrs={"class":"body"})
    body = body.find("div",attrs={"class":"page"})
    body = body.find_all(["p","h2"])

    dictionary.update(Body2Detail(body))
    return dictionary


def find_text_start_from(keyword,text):
   search = keyword +".+"
   result = re.search(search, text)
   if result == None:
       return None
   else:
       return result.group(0).replace(keyword,"")

def CreateSmallDictionary():
    small_dictionary = {
        "overview" : "",
        "facility_list" : [],
        "article_list" : [],
    }
    return small_dictionary


#記事本文をパースしてそれぞれの情報を辞書にいれる。
def Body2Detail(body):
    # dicionaryを初期化
    small_dictionary =CreateSmallDictionary()
    

    #bodyの要素を数える。
    length = len(body)

    #見るべきタグを定義
    i = 0
    try:
        while i < length:
            #見るべきタグ情報
            tag = body[i]
            if tag.name == "p":
                #対象者の情報かどうか
                if re.match(r".*(施設|事業所|事業者).*\r\n",tag.text) and re.search(r"・",tag.text):
                    #対象者の辞書の宣言
                    facility_dict = NewDictionary()                
                    #パースした要素のリスト
                    sep = tag.text.split("\r\n")
                    t = 0

                    #対象区分の定義
                    if re.match(r".*(施設|事業所|事業者)",sep[t]):
                        title = sep[t]
                        facility_dict["title"] = title
                        t += 1
                    elif 'title' in locals():
                        facility_dict["title"] = title
                        t += 1
                    else:
                        facility_dict["title"] = None

                    #施設名の定義
                    facility_dict["name"] = sep[t]

                    t += 1

                    while t<len(sep):
                        #対象区分の定義
                        if re.match(r"\s*・.*(所在地|住所)(：|:)", sep[t]):
                            facility_dict["address"] = re.sub(r"・.*(:|：)","", sep[t])
                        #事業形態
                        elif re.match(r"・.*(事業形態)(：|:)", sep[t]):
                            facility_dict["bussiness_form"] = re.sub(r"・.*(:|：)","",sep[t])
                        else:
                            #該当しない項目についてはprint
                            print(sep[t])
                        t += 1
                    
                    small_dictionary["facility_list"].append(facility_dict)

                else:
                    small_dictionary["overview"] = small_dictionary["overview"] + tag.text

            elif tag.name == "h2":
                article_title = tag.text
                i += 1
                tag = body[i]
                article_body = ""
                while True:
                    if tag.name == "p":
                        article_body += tag.text
                        if i+1 < length:
                            i += 1
                            tag = body[i]
                        else:
                            small_dictionary["article_list"].append([article_title,article_body])
                            break
                    else:
                        small_dictionary["article_list"].append([article_title,article_body])
                        break
            i += 1
    except:
        pass
    
    return small_dictionary
    
if __name__ == "__main__":
    #OutlineHtml2URL("http://www.care-mane.com/news/6/",)
    print(Detail("http://www.care-mane.com/news/10284?btn_id=category&CID=&TCD=0&CP=1"))
