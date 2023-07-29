-- Table: development.log

-- DROP TABLE IF EXISTS development.log;

CREATE TABLE IF NOT EXISTS development.log
(
    stamp timestamp without time zone NOT NULL,
    logger text COLLATE pg_catalog."default" NOT NULL,
    level character varying(12) COLLATE pg_catalog."default" NOT NULL,
    message text COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT log_pkey PRIMARY KEY ("time")
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS development.log
    OWNER to leafyydev;
    