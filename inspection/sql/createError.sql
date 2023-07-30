-- Table: leafyyerror

-- DROP TABLE IF EXISTS leafyyerror;

CREATE TABLE IF NOT EXISTS leafyyerror
(
    stamp timestamp without time zone NOT NULL,
    caller text COLLATE pg_catalog."default" NOT NULL,
    origin character varying(64) COLLATE pg_catalog."default" NOT NULL,
    message text COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT log_pkey PRIMARY KEY ("time")
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS leafyyerror
    OWNER to leafyydev;
    