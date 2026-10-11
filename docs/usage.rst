Usage guide
===========

Define a model and its hook
---------------------------

In your app's ``models.py``, inherit from ``BulkSaveableModel`` and override
``before_save()`` for preparation and validation:

.. code-block:: python

   from django.db import models
   from django_bulk_save import BulkSaveableModel


   class Item(BulkSaveableModel):
       name = models.CharField(max_length=100)
       quantity = models.IntegerField(default=0)

       def before_save(self):
           self.name = self.name.strip()
           if not self.name:
               raise ValueError("Name must not be empty.")

The base model is abstract. The hook is optional and does nothing by default.
It runs when the bulk context exits normally, once for each registered entry,
before any queued writes. Register each instance only once.

Regular ``save()`` calls do not invoke this hook automatically. Bulk operations
do not call ``save()`` or emit model save signals. ``full_clean()`` is not called
automatically; call it in your hook if your application needs it.

Create instances
----------------

.. code-block:: python

   items = [Item(name=" first "), Item(name=" second ", quantity=2)]

   with Item.bulk_save() as context:
       for item in items:
           context.register(item, update_fields=[])
       # The registered instances have not been written yet.

   # The hook has stripped the names and PostgreSQL has assigned primary keys.
   assert items[0].name == "first"
   assert items[0].pk is not None

``update_fields`` is required when registering. For new instances it does not
restrict inserted columns, so an empty list is sufficient. New instances are
inserted together using Django's ``bulk_create()``.

Update existing instances
-------------------------

.. code-block:: python

   items = list(Item.objects.order_by("pk")[:100])
   for item in items:
       item.name = f" {item.name.upper()} "
       item.quantity += 1

   with Item.bulk_save() as context:
       for item in items:
           context.register(item, update_fields=["name", "quantity"])

Only the listed columns are updated. Include any fields changed by the hook
that you want persisted. For example, if ``before_save()`` changes ``name``
but you register only ``quantity``, the modified name remains in memory and
is not written to the database.

Updates use ``pgbulk.update()`` exclusively. Instances are grouped by their
field tuples; use consistent field ordering to keep equivalent updates in
the same group. Unchanged values are still written because
``ignore_unchanged`` remains ``False``.

Mix creates and updates
-----------------------

.. code-block:: python

   existing = Item.objects.order_by("pk").first()
   if existing is not None:
       existing.quantity += 1
       new = Item(name=" another ")

       with Item.bulk_save() as context:
           context.register(existing, update_fields=["name", "quantity"])
           context.register(new, update_fields=[])

All hooks run first, followed by creates, then the grouped updates. Registered
writes share one transaction. If an exception escapes the context, its
transaction is rolled back. Within an outer transaction, successful completion
of the context still depends on the outer transaction committing.

Handle errors
-------------

Catch errors outside the ``with`` block so transaction handling can finish:

.. code-block:: python

   import logging

   from django.db import IntegrityError
   from django_bulk_save import BulkSaveError

   logger = logging.getLogger(__name__)

   try:
       with Item.bulk_save() as context:
           context.register(Item(name="example"), update_fields=[])
   except BulkSaveError:
       logger.exception("Invalid bulk-save operation")
       raise
   except IntegrityError:
       logger.exception("Database constraint violation")
       raise

``BulkSaveError`` covers the library's own validation errors, described in
:doc:`api`. Exceptions raised by hooks, the context body, and PostgreSQL retain
their original types. In the example model, an empty name raises ``ValueError``.

Rollback affects database writes, not Python attributes or external side
effects performed by hooks. After a failure, reload existing instances before
reusing their state; a newly inserted instance may retain an assigned primary
key even though its insertion was rolled back.

Discard queued operations
-------------------------

.. code-block:: python

   with Item.bulk_save() as context:
       context.register(Item(name="discarded"), update_fields=[])
       context.clear()
       context.register(Item(name="kept"), update_fields=[])

``clear()`` discards all entries currently queued. It does not save them or
undo database writes made directly inside the block. The registry is also
cleared automatically on successful or exceptional exit. The former
``flush()`` method has been replaced by ``clear()``.

Current limitations
-------------------

* An instance is considered new only when ``pk is None``. Creating objects with
  manually assigned primary keys or automatically assigned UUID primary keys
  through this context is not supported. An instance with a primary key follows
  the update path, even if the corresponding database row does not exist.
* Use the default database without routing these models to another database.
  The context opens its transaction on the default connection and does not
  expose a ``using`` option.
* Duplicate registrations of an instance or primary key are not rejected;
  register each object once to avoid repeated hooks and ambiguous updates.
* Field-name lists are copied on registration, but instances are stored by
  reference. Hooks see their state at context exit.
* There is no configurable batch size. The context retains registered instances
  until exit; choose context sizes suitable for your workload.
