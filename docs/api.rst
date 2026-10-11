API reference
=============

Model
-----

``django_bulk_save.BulkSaveableModel`` is an abstract Django model providing
the bulk-save entry point.

before_save()
~~~~~~~~~~~~~

Prepare or validate this instance before queued writes. Override in your
model. The default implementation does nothing. Its return value is ignored.

bulk_save()
~~~~~~~~~~~

Class method returning a context manager that yields a ``BulkSaveContext``.
On normal exit, execute hooks and persist queued instances in a transaction.
On exceptional exit, discard the queue and roll back the transaction.

Context
-------

Obtain a ``django_bulk_save.models.BulkSaveContext`` through your model's
``bulk_save()`` method. Constructing this class directly only creates a
registry; it does not arrange persistence.

register(instance, update_fields)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Queue an instance and snapshot an iterable of field names as a tuple.
A bare string, a non-iterable, or entries that are not non-empty strings
raise ``InvalidUpdateFieldsError`` immediately.

On normal context exit, objects of the wrong model raise
``InvalidInstanceError``. For instances on the update path, an empty list,
unknown fields, primary keys, non-concrete fields, many-to-many fields,
and ``auto_now_add`` fields raise ``InvalidUpdateFieldsError``. Model-field
checks are not applied to creates, where the field list is unused.

clear()
~~~~~~~

Discard queued entries without persisting them.

registry
~~~~~~~~

List of ``(instance, field_names_tuple)`` entries. Available for inspection;
use ``register()`` and ``clear()`` rather than modifying the list directly.

Exceptions
----------

All three exceptions are importable from ``django_bulk_save`` and
``django_bulk_save.exceptions``.

BulkSaveError
~~~~~~~~~~~~~

Base class for errors raised by the library itself. It does not wrap errors
from hooks or the database.

InvalidInstanceError
~~~~~~~~~~~~~~~~~~~~

A queued object does not belong to the context's model. Inherits from both
``BulkSaveError`` and ``TypeError``.

InvalidUpdateFieldsError
~~~~~~~~~~~~~~~~~~~~~~~~

Invalid or unsupported update fields. Inherits from both ``BulkSaveError``
and ``ValueError``. When wrapping a non-iterable input or unknown model field,
the original exception is available through ``__cause__``.
