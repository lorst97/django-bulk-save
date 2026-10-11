django-bulk-save
================

Run custom logic for each Django model instance, then persist changes in bulk
inside a transaction. Updates use ``pgbulk.update()``; new instances use
Django's ``bulk_create()``.

PostgreSQL is the only currently supported database engine. Support for other
engines will be developed upon request. Open an issue describing the engine
and your use case.

The project is an early prototype and its API is still under development.

Documentation
-------------

* `Installation <installation.rst>`_
* `Usage guide <usage.rst>`_
* `API reference <api.rst>`_
