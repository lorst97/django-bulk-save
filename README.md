# django-bulk-save

An efficiency utility for Django that aims to make bulk persistence easy when models require custom save logic.

Read the [documentation](docs/index.rst), starting with [installation](docs/installation.rst) and the [usage guide](docs/usage.rst). The [API reference](docs/api.rst) describes the context methods and custom exceptions.

## Database support

Currently, PostgreSQL is the only supported database engine. Support for other database engines will be developed upon request. Please open an issue specifying the engine you need and your use case.

## Motivation

Django's `bulk_update()` updates multiple model instances, but it does not call each model's `save()` method. This means that custom logic in an overridden `save()` method—including required application-level validations—is skipped.

Calling `save()` on every instance runs that logic, but typically issues a separate update query for each object. When updating many objects, those individual database queries can become a significant performance cost.

The library runs custom logic for each instance first, then persists updates with [`django-pgbulk`](https://django-pgbulk.readthedocs.io/en/stable/reference/#pgbulk.update) on PostgreSQL. New instances use Django's `bulk_create()` so generated primary keys are populated. This keeps per-instance validation and preparation while reducing the number of database queries.

## Quick start

From a local checkout, install with `python -m pip install -e .` and configure your Django project's default database to use PostgreSQL. Define a model in your installed Django app, then create and apply its migrations:

```python
from django.db import models
from django_bulk_save import BulkSaveableModel


class Item(BulkSaveableModel):
    name = models.CharField(max_length=100)
    quantity = models.IntegerField(default=0)

    def before_save(self):
        self.name = self.name.strip()
        if not self.name:
            raise ValueError("Name must not be empty.")
```

1. Collect the instances to save and the fields to update.
2. Run each instance's custom validation and preparation logic.
3. Persist the prepared changes in bulk.

Use a context to collect the writes:

Override `before_save()` for the logic to run in a bulk save. The context does not call `save()` or emit save signals, and regular `save()` calls do not automatically invoke `before_save()`.

```python
items = [Item(name=" first "), Item(name=" second ")]

with Item.bulk_save() as context:
    for item in items:
        context.register(item, update_fields=["name", "quantity"])
```

Hooks run before any queued writes. Creates and updates are committed in one transaction, with updates grouped by their `update_fields`. Updates exclusively use `pgbulk.update()` with its default `ignore_unchanged=False`; unchanged rows are still updated. Performance depends on the workload and should be measured on PostgreSQL.

For existing instances, list every field you want persisted, including fields modified by the hook. For creates, the field list does not restrict inserted columns. See the [usage guide](docs/usage.rst) for update examples, transaction behavior, and current limitations, including assigned primary keys and database routing.

## Error handling

The library exports `BulkSaveError` as the base class for its own errors:

- `InvalidInstanceError`: a registered object is not an instance of the context's model.
- `InvalidUpdateFieldsError`: field names are malformed, or an update requests an empty list, an unknown field, a primary key, a non-concrete field, a many-to-many field, or an `auto_now_add` field.

Errors raised by `before_save()`, the context body, and the database propagate unchanged, including Django's `IntegrityError`. Exceptions escaping the context roll back its transaction. The library does not print errors.

`register()` snapshots the supplied field names. The registry is cleared when the context exits, whether it succeeds or fails. To deliberately discard queued operations inside the context, use `context.clear()`. This replaces the former `flush()` method, which only discarded operations and did not persist them.

## Documentation

The documentation uses reStructuredText and Sphinx. Build it from the repository root:

```sh
python -m pip install -e '.[docs]'
python -m sphinx -b html -W --keep-going docs docs/_build/html
```

Open `docs/_build/html/index.html`. No Django configuration or running database is needed to build the documentation.

## Tests

Install the project and test dependencies with `python -m pip install -e '.[test]'`. The database tests require a dedicated PostgreSQL server and a database user with permission to create test databases:

```sh
PGHOST=localhost PGPORT=5432 \
PGDATABASE=bulk_save PGUSER=postgres PGPASSWORD=your_password \
python -m pytest
```

## Project status

This project is an early prototype. PostgreSQL updates use `django-pgbulk`; the API is still under development.

## Contributing

Contributions are very welcome! Whether you want to report a bug, suggest an idea, improve the documentation, or contribute code, you are encouraged to get involved at any experience level.

Please keep discussions friendly, polite, and respectful. Constructive feedback and different opinions are welcome, as long as everyone treats others with consideration.

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidance on how to contribute.
