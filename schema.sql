PRAGMA foreign_keys = ON;

drop table if exists logs;
create table logs (
  id integer primary key autoincrement,
  timestamp integer not null,
  status integer not null,
  irrigation_seconds integer not null,
  node_id integer not null,
  foreign key(node_id) references nodes(id)
);

drop table if exists nodes;
create table nodes (
  id integer primary key autoincrement,
  name text not null,
  unique (name)
);
