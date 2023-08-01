-- Table: leafyyInternals.users

-- DROP TABLE IF EXISTS "leafyyInternals".users;

CREATE TABLE IF NOT EXISTS "leafyyInternals".users
(
    login text COLLATE pg_catalog."default" NOT NULL,
    password character(96) COLLATE pg_catalog."default" NOT NULL,
    enabled boolean NOT NULL,
    warden boolean NOT NULL,
    ruler boolean NOT NULL,
    CONSTRAINT users_pkey PRIMARY KEY (login)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS "leafyyInternals".users
    OWNER to leafyy;

