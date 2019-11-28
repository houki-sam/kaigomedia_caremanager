/*メインのテーブル*/
CREATE TABLE IF NOT EXISTS News(
    id varchar(255) PRIMARY Key, 
    title varchar(511),
    url VARCHAR(255) UNIQUE,
    rp_date TIMESTAMP,
    overview TEXT
    );

/*施設情報のテーブル*/
CREATE TABLE IF NOT EXISTS Facility(
    id varchar(255), 
    title VARCHAR(255),
    name varchar(255),
    address varchar(511),
    bussiness_form VARCHAR(511)
    );

CREATE TABLE IF NOT EXISTS Article(
    id VARCHAR(255), 
    title VARCHAR(511),
    article text
    );

/*追加情報情報のテーブル*/
