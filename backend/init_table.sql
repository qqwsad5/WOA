CREATE TABLE nr_lut (
  nr text primary key, -- named person
  entry_list text -- list of entry_id, split by ';'
);;
CREATE TABLE ns_lut (
  ns text primary key, -- named person
  entry_list text -- list of entry_id, split by ';'
);;
CREATE TABLE nt_lut (
  nt text primary key, -- named person
  entry_list text -- list of entry_id, split by ';'
);;

CREATE TABLE entries (
  entry_id int primary key, -- provided by meta(entry_count)
  nr_list text, -- list of named person, split by ';'
  ns_list text, -- list of named geographic, split by ';'
  nt_list text, -- list of named entities, split by ';'
  weibo_list text -- list of weibo_id, split by ';'
);;

CREATE TABLE weibo (
  mid int primary key, -- identifier for original weibo, provided by "mid"
  uid int,          -- user id
  weibo_time text, -- y-m-d-h-m-s; send time: parsed from weibo's date info
  content text, -- main content: parsed from weibo body
  dt_id_list text, -- transmit weibo: list of weibo_id, parsed from weibo body, split by ';'
  update_time text, -- y-m-d-h-m-s; last time comment-transmit zone is active
  FOREIGN KEY (uid) REFERENCES user_lut (user_id)
);;

CREATE TABLE date_transmission (
  dt_id int primary key, -- transmissions within a date's time bin
  dt_date time, -- y-m-d; timestamp of creation date
  trans_id text -- list of keys to table: transmitted, split by ';'
);;

CREATE TABLE transmitted (
  mid int primary key, -- identifier for transmission, provided by "mid"
  uid int,
  content text, -- main content: parsed from transmission body
  trans_time text -- y-m-d-h-m-s; tranmission time: parsed from weibo's date info
);;

CREATE TABLE user_lut (
  user_id int primary key, -- user id: an integer
  nickname text -- username: a string
);;

CREATE TABLE meta (
  name text primary key NOT NULL,
  value int
);;
INSERT INTO meta VALUES ('rumorwords_update_yy', 2020);;
INSERT INTO meta VALUES ('rumorwords_update_mm', 3);;
INSERT INTO meta VALUES ('rumorwords_update_dd', 20);;
INSERT INTO meta VALUES ('rumorwords_update_hh', 0);;
INSERT INTO meta VALUES ('rumorwords_update_mi', 0);;
INSERT INTO meta VALUES ('rumorwords_update_ss', 0);;
INSERT INTO meta VALUES ('entry_count',0);;
INSERT INTO meta VALUES ('dt_count',0);;
