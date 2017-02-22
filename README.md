# pto-postgres
PostgreSQL backend for Path Transparency Observatory and associated utilities

# Directory structure

* frontend: Contains the public frontend
* py/ptoweb: PAPI
* py/runit.py: (DEBUG ONLY) Can be used to launch flask. In production use uwsgi/nginx
* py/worker.py: Manages worker that execute queries in the query queues (you need this an PAPI running)
* db/sql: SQL files to create tables/databases/indexes.
* db/scripts: Python scripts to convert bson to sql.
* py/arun.py: analysis runtime. contains both observation set (for analyzers to use) as well as the runtime itself.

All of this should be refactored. See [the issue](https://github.com/mami-project/pto-postgres/issues/54) to discuss