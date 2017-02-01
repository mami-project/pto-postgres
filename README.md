# pto-postgres
PostgreSQL backend for Path Transparency Observatory and associated utilities

# Directory structure

* frontend: Contains the public frontend
* py/ptoweb: PAPI
* py/runit.py: (DEBUG ONLY) Can be used to launch flask. In production use uwsgi/nginx
* db/sql: SQL files to create tables/databases/indexes.
* db/scripts: Python scripts to convert bson to sql.
