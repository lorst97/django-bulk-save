API reference
=============

Model
-----

.. py:class:: django_bulk_save.BulkSaveableModel

   Abstract Django model providing the bulk-save entry point.

   .. py:method:: before_save()

      Prepare or validate this instance before queued writes. Override in your
      model. The default implementation does nothing. Its return value is ignored.

   .. py:method:: bulk_save()
      :classmethod:

      Return a context manager yielding a ``BulkSaveContext``. On normal exit,
      execute hooks and persist queued instances in a transaction. On exceptional
      exit, discard the queue and roll back the transaction.

Context
-------

.. py:class:: django_bulk_save.models.BulkSaveContext

   Obtain a context through your model's ``bulk_save()`` method. Constructing
   this class directly only creates a registry; it does not arrange persistence.

   .. py:method:: register(instance, update_fields)

      Queue an instance and snapshot an iterable of field names as a tuple.
      A bare string, a non-iterable, or entries that are not non-empty strings
      raise ``InvalidUpdateFieldsError`` immediately.

      On normal context exit, objects of the wrong model raise
      ``InvalidInstanceError``. For instances on the update path, an empty list,
      unknown fields, primary keys, non-concrete fields, many-to-many fields,
      and ``auto_now_add`` fields raise ``InvalidUpdateFieldsError``. Model-field
      checks are not applied to creates, where the field list is unused.

   .. py:method:: clear()

      Discard queued entries without persisting them.

   .. py:attribute:: registry

      List of ``(instance, field_names_tuple)`` entries. Available for inspection;
      use ``register()`` and ``clear()`` rather than modifying the list directly.

Exceptions
----------

All three exceptions are importable from ``django_bulk_save`` and
``django_bulk_save.exceptions``.

.. py:exception:: django_bulk_save.BulkSaveError

   Base class for errors raised by the library itself. It does not wrap errors
   from hooks or the database.

.. py:exception:: django_bulk_save.InvalidInstanceError

   A queued object does not belong to the context's model. Inherits from both
   ``BulkSaveError`` and ``TypeError``.

.. py:exception:: django_bulk_save.InvalidUpdateFieldsError

   Invalid or unsupported update fields. Inherits from both ``BulkSaveError``
   and ``ValueError``. When wrapping a non-iterable input or unknown model field,
   the original exception is available through ``__cause__``.
