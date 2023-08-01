CREATE DATABASE Leafyy
    WITH
    OWNER = leafyy
    ENCODING = 'UTF8'
    CONNECTION LIMIT = 2
    IS_TEMPLATE = False;

-- SCHEMA: leafyyInternals

-- DROP SCHEMA IF EXISTS leafyy ;

CREATE SCHEMA IF NOT EXISTS leafyy
    AUTHORIZATION leafyy;
