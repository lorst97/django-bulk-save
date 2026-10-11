# django-bulk-save

An efficiency utility for Django that aims to make bulk persistence easy when models require custom save logic.

## Motivation

Django's `bulk_update()` efficiently updates multiple model instances, but it does not call each model's `save()` method. This means that custom logic in an overridden `save()` method—including required application-level validations—is skipped.

Calling `save()` on every instance runs that logic, but typically issues a separate update query for each object. When updating many objects, those individual database queries can become a significant performance cost.

The library runs custom logic for each instance first, then persists updates with [`django-pgbulk`](https://django-pgbulk.readthedocs.io/en/stable/reference/#pgbulk.update) on PostgreSQL. Other database backends use Django's `bulk_update()`. New instances use Django's `bulk_create()` so generated primary keys are populated on supported backends. This keeps per-instance validation and preparation while reducing the number of database queries.

## Intended workflow

1. Collect the instances to save and the fields to update.
2. Run each instance's custom validation and preparation logic.
3. Persist the prepared changes in bulk.

The project explores an explicit pre-save hook and a context manager to coordinate this workflow. Its aim is to separate custom save logic from the database write, so applications can reuse that logic without issuing an individual update for every instance.

Override `before_save()` for the logic to run in a bulk save. The context does not call `save()` or emit save signals, and regular `save()` calls do not automatically invoke `before_save()`.

```python
with Item.bulk_save() as context:
    for item in items:
        context.register(item, update_fields=["name", "quantity"])
```

Hooks run before any queued writes. Creates and updates are committed in one transaction, with updates grouped by their `update_fields`. PostgreSQL updates use `pgbulk.update()` with its default `ignore_unchanged=False`; unchanged rows are still updated. Performance depends on the workload and database and should be measured on PostgreSQL rather than inferred from SQLite tests.

## Tests

Install the project and test dependencies with `python -m pip install -e '.[test]'`, then run `python -m pytest` for SQLite tests. To exercise the real PostgreSQL path, use a dedicated test server and a database user with permission to create test databases:

```sh
BULK_SAVE_TEST_POSTGRES=1 PGHOST=localhost PGPORT=5432 \
PGDATABASE=bulk_save PGUSER=postgres PGPASSWORD=your_password \
python -m pytest
```

## Project status

This project is an early prototype. PostgreSQL updates use `django-pgbulk`; the API is still under development.

## Contributing

Contributions are very welcome! Whether you want to report a bug, suggest an idea, improve the documentation, or contribute code, you are encouraged to get involved at any experience level.

Please keep discussions friendly, polite, and respectful. Constructive feedback and different opinions are welcome, as long as everyone treats others with consideration.

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidance on how to contribute.
