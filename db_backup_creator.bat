"C:/Program Files/PostgreSQL/15/bin/pg_dump.exe" --schema-only -U postgres vympel.one > vympel.one.sql
@REM "C:/Program Files/PostgreSQL/15/bin/psql.exe" vympel.one < vympel.one.sql