-- Table: development.error

-- DROP TABLE IF EXISTS development.error;

CREATE TABLE IF NOT EXISTS development.error
(
    stamp timestamp without time zone NOT NULL,
    caller text COLLATE pg_catalog."default" NOT NULL,
    origin character varying(12) COLLATE pg_catalog."default" NOT NULL,
    message text COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT log_pkey PRIMARY KEY ("time")
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS development.error
    OWNER to leafyydev;
    