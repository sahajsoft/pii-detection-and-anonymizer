# dbt pii

A dbt macro which detects pii.

## Getting Started

To get started, run the following:

```
poetry install
poetry run dbt seed --profiles-dir .
poetry run dbt run --profiles-dir .
sqlite3 dbs/main.db 'select * from main.pii_info;'
```
