-- Table: leafyylog

-- DROP TABLE IF EXISTS leafyylog;

CREATE TABLE IF NOT EXISTS leafyylog
(
    stamp timestamp without time zone NOT NULL,
    logger character varying(32) COLLATE pg_catalog."default" NOT NULL,
    level character varying(16) COLLATE pg_catalog."default" NOT NULL,
    message text COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT log_pkey PRIMARY KEY ("time")
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS leafyylog
    OWNER to leafyydev;
    