# pto-postgres
PostgreSQL backend for Path Transparency Observatory and associated utilities

**NOTE** this is the `redesign` branch

# Directory structure

* mamipto: Python module toplevel for PTO backend and middleware
* mamipto/pg: PostgreSQL database connection management, data model glue, and database management
* mamipto/iql: Interesting Query Language support (and PostgreSQL transpiler)
* mamipto/query: Query runtime
* mamipto/analysis: Analysis runtime
* mamipto/api: Flask implementation of PAPI
* docs: Design, development, and administrator's documentation
* tests: Test suites

# Legacy directories and files

These files remain in this branch to receive merged changes related to the 1 March
release from other branches. They will be removed after code has been redistributed from them, before merging back to `master`.

* frontend: Contains the public frontend
* py/ptoweb: PAPI
* py/runit.py: (DEBUG ONLY) Can be used to launch flask. In production use uwsgi/nginx
* py/worker.py: Manages worker that execute queries in the query queues (you need this an PAPI running)
* db/sql: SQL files to create tables/databases/indexes.
* db/scripts: Python scripts to convert bson to sql.
* py/arun.py: analysis runtime. contains both observation set (for analyzers to use) as well as the runtime itself.
