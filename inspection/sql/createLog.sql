-- Table: leafyy.log

-- DROP TABLE IF EXISTS leafyy.log;

CREATE TABLE IF NOT EXISTS leafyy.log
(
    id bigint NOT NULL,
    stamp timestamp without time zone NOT NULL,
    logger character varying(32) COLLATE pg_catalog."default" NOT NULL,
    level character varying(16) COLLATE pg_catalog."default" NOT NULL,
    message text COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT log_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS leafyy.log
    OWNER to leafyy;
