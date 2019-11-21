/*メインのテーブル*/
CREATE TABLE IF NOT EXISTS NEWS(
    id UUID PRIMARY Key, 
    title varchar(511),
    url VARCHAR(255) UNIQUE,
    rp_date TIMESTAMP,
    overview TEXT
    );

/*施設情報のテーブル*/
CREATE TABLE IF NOT EXISTS Facility(
    id UUID, 
    title VARCHAR(255),
    name text,
    address text,
    bussiness_form text
    );

CREATE TABLE IF NOT EXISTS Article(
    id UUID, 
    title VARCHAR(511),
    article text
    );

/*追加情報情報のテーブル*/
