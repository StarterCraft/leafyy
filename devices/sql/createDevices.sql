-- Table: "leafyyInternals".devices

-- DROP TABLE IF EXISTS "leafyyInternals".devices;

CREATE TABLE IF NOT EXISTS "leafyyInternals".devices
(
    address character varying(64) COLLATE pg_catalog."default" NOT NULL,
    "displayName" text COLLATE pg_catalog."default",
    description text COLLATE pg_catalog."default",
    enabled boolean NOT NULL,
    "visibleInConsole" boolean,
    "decodeMode" character varying(8) COLLATE pg_catalog."default",
    CONSTRAINT devices_pkey PRIMARY KEY (address)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS "leafyyInternals".devices
    OWNER to leafyy;

