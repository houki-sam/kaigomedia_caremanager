import re

class Parser(object):
    def __init__(self):
        self.facility_title = "" #処分の区分の文字列
        self.dictionary = {
            "Facility" : [],
            "Article" : [],
        }#データ格納辞書の初期化
        self.overview = "" #記事の概要
    
    def controller(self,tag_list):#タグ処理のためのコントローラー
        h2_flag = False #h2(記事のセクション）中に含まれるpタグかを判断
        for tag in tag_list:
            tag_name = tag[0] #タグの属性
            tag_text = tag[1] #本文

            if tag_name == "p" and h2_flag:
                self.dictionary["Article"][-1]["article"] += tag_text
                
            elif tag_name == 'h2':
                h2_flag = True
                self.dictionary["Article"].append({
                    "title" : tag_text, 
                    "article" : ""
                }
                )
            
            elif tag_name == 'p' and self.judge_facility(tag_text):#facilityに該当するpタグかを判断
                self.dictionary["Facility"].append(self.facility_parse(tag_text))

            else:
                self.overview += tag_text
        return self.overview, self.dictionary

    def judge_facility(self,tag_text):#該当文章がfacilityに該当するかを判定
        return re.search(r"\r\n・", tag_text)

    def facility_parse(self, text):#処分対象者の情報をパースする
        text_list = text.splitlines()#入力されて文字列を改行で分割
        facility_dictionary = {
            "title" : None,
            "name" : None,
            "address" : None,
            "bussiness_form" : None,
        }#この辞書に取り出した情報を入れていく。

        #まず一行目がタイトルになっているかどうかを判定
        if re.match(r".*(施設|事業所|事業者).*", text_list[0]):
            self.facility_title = text_list.pop(0)
        facility_dictionary["title"] = self.facility_title

        #　これは必ず1番目に表在されているためindexで取り出し。
        facility_dictionary["name"] = re.sub("・","",re.sub(r"(名称|事業所名|運営法人|法人名)：","", text_list.pop(0))) 

        for x in text_list:
            #住所,所在地について
            if re.match(r"\s*・.*(所在地|住所)(：|:)", x):
                facility_dictionary["address"] = re.sub(r"・.*(:|：)","", x)

            #事業形態
            elif re.match(r"・.*(事業形態)(：|:)", x):
                facility_dictionary["bussiness_form"] = re.sub(r"・.*(:|：)","", x)
        return facility_dictionary