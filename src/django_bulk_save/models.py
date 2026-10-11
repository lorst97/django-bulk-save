from contextlib import contextmanager

import pgbulk
from django.core.exceptions import FieldDoesNotExist
from django.db import models, transaction

from .exceptions import InvalidInstanceError, InvalidUpdateFieldsError


class BulkSaveContext:
    def __init__(self):
        self.registry = []

    def register(self, instance, update_fields):
        if isinstance(update_fields, str):
            raise InvalidUpdateFieldsError("update_fields must be an iterable of field names.")
        try:
            fields = tuple(update_fields)
        except TypeError as exc:
            raise InvalidUpdateFieldsError(
                "update_fields must be an iterable of field names."
            ) from exc
        if any(not isinstance(field, str) or not field for field in fields):
            raise InvalidUpdateFieldsError("Each update field must be a non-empty string.")
        self.registry.append((instance, fields))

    def clear(self):
        """Discard queued operations without writing them to the database."""
        self.registry.clear()


class BulkSaveableModel(models.Model):
    def before_save(self):
        """
        Hook method to be called before saving the object.
        Override this method in your model to perform any actions before saving.
        """

    @classmethod
    @contextmanager
    def bulk_save(cls):
        with transaction.atomic():
            save_context = BulkSaveContext()
            try:
                yield save_context

                updates = {}
                create_list = []

                for instance, update_field in save_context.registry:
                    if not isinstance(instance, cls):
                        raise InvalidInstanceError(
                            f"Expected an instance of {cls._meta.label}, "
                            f"got {type(instance).__name__}."
                        )
                    instance.before_save()
                    if instance.pk is None:
                        create_list.append(instance)
                    else:
                        updates.setdefault(update_field, []).append(instance)

                for fields in updates:
                    cls._validate_update_fields(fields)

                cls.objects.bulk_create(create_list)

                for fields, instances in updates.items():
                    pgbulk.update(cls, instances, update_fields=list(fields))

            finally:
                save_context.clear()

    @classmethod
    def _validate_update_fields(cls, fields):
        if not fields:
            raise InvalidUpdateFieldsError("Field names must be given to bulk_save().")
        for name in fields:
            try:
                field = cls._meta.get_field(name)
            except FieldDoesNotExist as exc:
                raise InvalidUpdateFieldsError(
                    f"Unknown update field {name!r} on {cls._meta.label}."
                ) from exc
            if (
                not field.concrete
                or field.many_to_many
                or field.primary_key
                or getattr(field, "auto_now_add", False)
            ):
                raise InvalidUpdateFieldsError(f"Field {name!r} cannot be bulk updated.")

    class Meta:
        abstract = True
