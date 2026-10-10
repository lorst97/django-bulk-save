# django-bulk-save

An efficiency utility for Django that aims to make bulk persistence easy when models require custom save logic.

## Motivation

Django's `bulk_update()` efficiently updates multiple model instances, but it does not call each model's `save()` method. This means that custom logic in an overridden `save()` method—including required application-level validations—is skipped.

Calling `save()` on every instance runs that logic, but typically issues a separate update query for each object. When updating many objects, those individual database queries can become a significant performance cost.

The goal of this library is to make it easy to run the required custom logic for each instance first, then persist the resulting changes with `bulk_update()`. This keeps per-instance validation and preparation while reducing the number of database queries.

## Intended workflow

1. Collect the instances to save and the fields to update.
2. Run each instance's custom validation and preparation logic.
3. Persist the prepared changes in bulk.

The project explores an explicit pre-save hook and a context manager to coordinate this workflow. Its aim is to separate custom save logic from the database write, so applications can reuse that logic without issuing an individual update for every instance.

## Project status

This project is an early prototype. The bulk persistence workflow is still under development; the description above outlines the intended behavior rather than a complete, ready-to-use API.

## Contributing

Contributions are very welcome! Whether you want to report a bug, suggest an idea, improve the documentation, or contribute code, you are encouraged to get involved at any experience level.

Please keep discussions friendly, polite, and respectful. Constructive feedback and different opinions are welcome, as long as everyone treats others with consideration.

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidance on how to contribute.
