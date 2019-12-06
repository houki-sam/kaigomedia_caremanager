import os
import re
import MySQLdb
import pandas as pd

if __name__ == "__main__":
    #接続情報
    host = "db"
    user = os.environ["MYSQL_USER"]
    password = os.environ["MYSQL_PASSWORD"]
    port = os.environ["PORT"]
    db = os.environ["MYSQL_DATABASE"]
    #接続
    conn = MySQLdb.connect(
        host = 'db',
        user = "user",
        port = 3306,
        passwd = "password",
        db = "sample_db",
        charset="utf8"
        )
    cur = conn.cursor()

    #データベースが作ってあったら先に削除
    drop_table_sql = "drop table if exists NewFacility"
    cur.execute(drop_table_sql)
    conn.commit()

    fetch_sql = "select * from Facility"
    cur.execute(fetch_sql)
    dataset = cur.fetchall()

    df = pd.read_csv("city.csv").values.tolist()
    city_dict = {}
    for x in df:
        city_dict[x[1]] = x[0]

    dataset = [list(x) for x in dataset]

    
    for x in range(len(dataset)):
        address = dataset[x][3]
        if re.match(r'.{1,4}県|東京都|京都府|大阪府|北海道', address):
            pass
        else:
            name = re.match(r'.*?(市|町|村|区)', address).group()
            
            if name in city_dict:
                prefect = city_dict[name]
                dataset[x][3] = prefect + dataset[x][3]
            else:
                print(dataset[x])
    
    dataset = (tuple(x) for x in dataset)
    
    create_sql ="CREATE TABLE IF NOT EXISTS NewFacility(id varchar(255), title VARCHAR(255), name varchar(255), address varchar(511), bussiness_form VARCHAR(511));"
    cur.execute(create_sql)
    conn.commit()

    cur.executemany("insert into NewFacility values(%s,%s,%s,%s,%s)", dataset)
    conn.commit()