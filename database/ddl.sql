create table camera
(
	id varchar(10) default 'cam_01' not null
		primary key,
	location varchar(50),
	coordinate_x real,
	coordinate_y real
)
;

create table cars
(
	id int default 1000 not null
		primary key,
	color varchar(10),
	first_sighted bigint,
	license_image varchar(100),
	license_number varchar(50),
	car_image varchar(100),
	num_rules_broken int default 0,
	owner varchar(50)
)
;

create table rules
(
	id INTEGER primary key AUTO_INCREMENT,
	name varchar(50) not null,
	fine real
)
;

create unique index rules_name_uindex
	on rules (name)
;

create table violations
(
	camera int PRIMARY KEY,
    constraint violations_camera_id_fk
    FOREIGN KEY(CAMERA)
	references camera(ID)
	on update cascade on delete cascade,
	car int PRIMARY KEY,
	constraint violations_cars_id_fk
    FOREIGN KEY(CAR)
	references cars(ID)
	on update cascade on delete cascade,
	rule INTEGER PRIMARY KEY,
	constraint violations_rules_id_fk
	FOREIGN KEY(RULE)		
	references rules(ID)
	on update cascade on delete cascade,
	'time' datetime,
	constraint violations_pk
	primary key (car, rule, time)
)
;


