drop table if exists users;
create table users (
    id integer primary key autoincrement,
    uuid text unique,
    user_name integer not null,
    user_passwd text not null,
    phone_number integer not null,
    register_time integer not null,
    history_order_num integer default 0
);

drop table if exists merchants;
create table merchants (
    id integer primary key autoincrement,
    uuid text unique,
    merchant_name text not null,
    merchant_passwd text not null,
    merchant_description text,
    merchant_remark text,
    phone_number integer not null,
    register_time integer not null,
    money_number integer default 0,
    check_time integer default 0,
    merchant_number integer default 0
);

drop table if exists photoes;
create table photoes (
    id integer primary key autoincrement,
    uuid text unique,
    url text,
    user_uuid text,
    room_uuid text,
    foreign key(user_uuid) references users(uuid),
    foreign key(room_uuid) references rooms(uuid)
);

drop table if exists orders;
create table orders (
    id integer primary key autoincrement,
    uuid text unique,
    user_uuid text not null,
    room_uuid text not null,
    deal_time integer not null,
    deal_state integer default 0,
    foreign key(user_uuid) references users(uuid),
    foreign key(room_uuid) references rooms(uuid)
);

drop table if exists coupons;
create table coupons (
    id integer primary key autoincrement,
    uuid text unique,
    user_uuid text not null,
    coupon_type integer not null,
    coupon_state integer default 0,
    foreign key(user_uuid) references users(uuid)
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
    room_price text not null,
    room_remark1 text,
    room_remark2 text,
    room_type integer default 0,
    place_uuid text not null,
    room_description text not null,
    room_coordinate integer,
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
    stock integer default 0,
    foreign key(merchant_uuid) references merchants(uuid),
    foreign key(place_uuid) references places(uuid)
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
