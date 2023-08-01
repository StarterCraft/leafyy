-- Table: leafyy.devices

-- DROP TABLE IF EXISTS leafyy.devices;

CREATE TABLE IF NOT EXISTS leafyy.devices
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

ALTER TABLE IF EXISTS leafyy.devices
    OWNER to leafyy;

