CREATE TABLE js_respond_search (
  visit_time text, -- 访问时间
  keyword text     -- 访问参数：关键词
);;

CREATE TABLE js_respond_show (
  visit_time text, -- 访问时间
  entry_id int     -- 访问参数：entry的id
);;

CREATE TABLE js_respond_transmit (
  visit_time text, -- 访问时间
  repost_id int    -- 访问参数：转发微博的mid
);;

CREATE TABLE meta (
  key text,  -- 键
  value int  -- 值
);;

INSERT INTO meta VALUES ('search_number', 0);;
INSERT INTO meta VALUES ('show_number', 0);;
INSERT INTO meta VALUES ('repost_show_number', 0);;