

SELECT current_database();

SELECT usename FROM pg_catalog.pg_user;

SELECT grantee, privilege_type 
FROM information_schema.usage_privileges
group by grantee, privilege_type;

SELECT datname, pg_catalog.pg_get_userbyid(datdba) AS owner 
FROM pg_catalog.pg_database;

--ALTER SCHEMA public OWNER TO rat_app;
--GRANT USAGE, CREATE ON SCHEMA public TO rat_app;