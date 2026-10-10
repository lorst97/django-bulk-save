from django.db import models

from django_bulk_save import BulkSaveableModel


class Item(BulkSaveableModel):
    name = models.CharField(max_length=100)
    quantity = models.IntegerField(default=0)

    def before_save(self):
        self.name = self.name.strip()
        if not self.name:
            raise ValueError("Name must not be empty.")
        self.hook_calls = getattr(self, "hook_calls", 0) + 1
