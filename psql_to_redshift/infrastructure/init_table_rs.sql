    create table if not exists apps (
        id int  primary key,
        title varchar(256) not null,
        description text not null,
        published_timestamp timestamp not null,
        last_updated_timestamp timestamp not null
            );