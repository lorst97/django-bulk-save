from contextlib import contextmanager
from django.db import models
from django.db import transaction


class BulkSaveContext:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.registry = []

    def register(self, instance, **kwargs):
        self.registry.append((instance, kwargs))

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
        print("logic before saving the object")
        self.register(self.pk)

    @contextmanager
    @classmethod
    def bulk_save(cls):
        with transaction.atomic():
            # context registering
            try:
                save_context = BulkSaveContext()
                yield save_context

                for instance in save_context.registry:
                    instance.before_save()

                # funzione che divide registry in create e update
                # operazioni in blocco con relative liste

            finally:
                pass


"""
idea: 

with Objects.bulk_save() as save:
    for obj in objects:
        obj.smth = "value"
        save.register(obj, update_fields=["smth"])

"""
