from contextlib import contextmanager
from django.db import models
from django.db import transaction


class BulkSaveContext:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.registry = []

    def register(self, instance, update_fields):
        self.registry.append((instance, update_fields))

    def flush(self):
        print(self.registry)
        self.registry.clear()


class BulkSaveableModel(models.Model):
    def before_save(
        self,
    ):
        """
        Hook method to be called before saving the object.
        Override this method in your model to perform any actions before saving.
        """

    @classmethod
    @contextmanager
    def bulk_save(cls):
        with transaction.atomic():
            try:
                save_context = BulkSaveContext()
                yield save_context

                updates = {}
                create_list = []

                for instance, update_field in save_context.registry:
                    instance.before_save()
                    update_field = tuple(update_field)
                    if instance.pk is None:
                        create_list.append(instance)
                    else:
                        updates.setdefault(update_field, []).append(instance)

                cls.objects.bulk_create(create_list)

                for fields, instances in updates.items():
                    cls.objects.bulk_update(
                        instances,
                        fields=list(fields),
                    )

            except Exception as e:
                print(f"Error during bulk save: {e}")
                raise
            finally:
                pass

    class Meta:
        abstract = True
