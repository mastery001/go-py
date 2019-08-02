create database tmall;

use tmall;

create table product_comment (
	id int primary key auto_increment,
	search_word varchar(30) comment '搜索词',
	word_category varchar(30) comment '词类别',
	date datetime comment '评论日期',
	content text comment '评论内容',
	sku varchar(200) comment 'sku',
	source varchar(55) comment '来源'
) ENGINE=InnoDB DEFAULT CHARSET= utf8mb4;


create table product_info_comment (
	id int primary key auto_increment,
	product_id varchar(100),
	price varchar(200) ,
	title text ,
	shop varchar(200) ,
	month_buy_total varchar(200) ,
	comment_count varchar(200),
	search_word varchar(30) comment '搜索词',
	word_category varchar(30) comment '词类别',
	date datetime comment '评论日期',
	content text comment '评论内容',
	sku varchar(200) comment 'sku',
	source varchar(55) comment '来源'
) ENGINE=InnoDB DEFAULT CHARSET= utf8mb4;