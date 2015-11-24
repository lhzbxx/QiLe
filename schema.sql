drop table if exists users;
create table users (
    id integer primary key autoincrement,
    uuid text unique,
    user_name integer not null,
    user_passwd text not null,
    phone_number integer not null,
    register_time integer not null,
    true_name text,
    open_id text,
    history_order_num integer default 0
);

INSERT INTO users VALUES (0, 0, 123456, 123456, 13651608916, 0, null, oDUXXtyB7F6YQGb9fjcCQY61aSjg, 0);

drop table if exists user_info;
create table user_info (
    phone_number primary key,
    user_orders text not null,
    user_coupons text not null,
    foreign key(phone_number) references users(phone_number)
);

drop table if exists user_checkin;
create table user_checkin (
    id integer primary key autoincrement,
    uuid text unique,
    user_uuid text,
    name text not null,
    type integer not null,
    identify text not null,
    foreign key(user_uuid) references users(uuid)
);

drop table if exists merchants;
create table merchants (
    id integer primary key autoincrement,
    uuid text unique,
    merchant_name text not null,
    merchant_username text not null,
    merchant_password text not null,
    merchant_description text,
    merchant_remark text,
    merchant_phone_number1 integer not null,
    merchant_phone_number2 integer,
    merchant_address text,
    merchant_img_url text,
    register_time integer not null,
    money_number integer default 0,
    check_time integer default 0,
    merchant_number integer default 0
);

INSERT INTO merchants VALUES (0, 0, 'test', 'test', 'test', 'test_description', 'test_remark', 123456, 123456, 'test_address', 'test_img_url', 0, 0, 0, 0);

drop table if exists photoes;
create table photoes (
    id integer primary key autoincrement,
    uuid text unique,
    url text,
    room_uuid text,
    foreign key(room_uuid) references rooms(uuid)
);

drop table if exists orders;
create table orders (
    id integer primary key autoincrement,
    uuid text unique,
    user_uuid text not null,
    room_uuid text not null,
    room_name text not null,
    deal_time integer not null,
    deal_state integer default 0,
    deal_price integer not null,
    deal_cost integer not null,
    date1 text not null,
    date2 text not null,
    liver_info text,
    coupon_uuid text,
    true_name text,
    foreign key(user_uuid) references users(uuid),
    foreign key(room_uuid) references rooms(uuid)
);

drop table if exists coupons;
create table coupons (
    id integer primary key autoincrement,
    uuid text not null,
    coupon_uuid text not null,
    coupon_name text not null,
    phone_number integer not null,
    coupon_discount integer not null,
    coupon_limit integer not null,
    create_time integer not null,
    limit_time integer not null,
    coupon_state integer default 1,
    coupon_remark text,
    coupon_color integer not null,
    foreign key(coupon_uuid) references coupon_template(uuid)
);

INSERT INTO coupons VALUES (0, 0, 0, 'test', 13651608916, 50, 100, 0, 1000000, 1, 'test', 1);

drop table if exists coupon_template;
create table coupon_template (
    id integer primary key autoincrement,
    uuid text unique,
    coupon_name text not null,
    coupon_discount integer not null,
    coupon_limit integer not null,
    limit_time integer not null,
    coupon_remark text,
    coupon_stock integer not null,
    coupon_color integer not null,
    create_time integer not null
);

INSERT INTO coupon_template VALUES (0, "init0", '新人券', 40, 100, 2592000, ' ', 9999999, 2, 0);
INSERT INTO coupon_template VALUES (1, "init1", '红包券', 10, 100, 604800, ' ', 9999999, 1, 0);
INSERT INTO coupon_template VALUES (2, "init2", '红包券', 10, 100, 604800, ' ', 9999999, 1, 0);
INSERT INTO coupon_template VALUES (3, "init3", '红包券', 10, 100, 604800, ' ', 9999999, 1, 0);

drop table if exists coupon_block;
create table coupon_block (
    block text not null,
    coupon_uuid text not null,
    count integer default 0,
    create_time integer not null,
    constraint pk_coupon_block primary key (block, coupon_uuid)
);

drop table if exists places;
create table places (
    id integer primary key autoincrement,
    uuid text unique,
    place_name text not null
);

drop table if exists rooms;
create table rooms (
    id integer primary key autoincrement,
    uuid text unique,
    merchant_uuid text not null,
    room_name text not null,
    room_price integer not null,
    room_cost integer not null,
    room_activity_state default 0,
    room_activity_price integer,
    room_activity_cost integer, 
    room_remark1 text,
    room_remark2 text,
    room_img_url text not null,
    room_type integer default 0,
    place_uuid text,
    room_description text not null,
    room_coordinate integer,
    room_address text,
    register_time integer not null,
    device_network integer default 0,
    device_shower integer default 0,
    device_ct integer default 0,
    device_ac integer default 0,
    device_sheet integer default 0,
    device_tv integer default 0,
    device_drink integer default 0,
    device_brush integer default 0,
    device_towel integer default 0,
    device_slipper integer default 0,
    device_toilet integer default 0,
    device_shampoo integer default 0,
    device_pc integer default 0,
    device_smoke integer default 0,
    star_average integer default 0,
    stock text default '150306725297525326584926758194517569752043683130132471725266622178061377607334940381676735896625196994043838463',
    room_switch integer default 1,
    foreign key(merchant_uuid) references merchants(uuid)
);

drop table if exists comments;
create table comments (
    id integer primary key autoincrement,
    uuid text unique,
    star integer not null,
    user_uuid text not null,
    room_uuid text not null,
    content text,
    foreign key(user_uuid) references users(uuid),
    foreign key(room_uuid) references rooms(uuid)
);

drop table if exists advice;
create table advice (
    id integer primary key autoincrement,
    uuid text unique,
    user_uuid text not null,
    content text not null,
    advice_time integer not null,
    foreign key(user_uuid) references users(uuid)
);

drop table if exists total;
create table total (
    total_order integer default 0,
    total_money integer default 0,
    total_user integer default 0,
    total_merchant integer default 0,
    total_room integer default 0,
    total_advice integer default 0,
    total_coupon integer default 0
);

drop table if exists log;
create table log (
    time integer primary key,
    log_order integer default 0,
    log_money integer default 0,
    log_user integer default 0,
    log_merchant integer default 0,
    log_room integer default 0,
    log_advice integer default 0,
    log_coupon integer default 0
);

drop table if exists admin_users;
create table admin_users (
    id integer primary key autoincrement,
    uuid text unique,
    user_name integer not null,
    user_passwd text not null,
    login_session text,
    auth integer default 1
);