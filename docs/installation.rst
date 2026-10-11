Installation
============

Requirements
------------

* Python 3.14 or later.
* Django 6.1.2 or later, as declared by the package dependencies.
* A configured PostgreSQL database.

Install from a local checkout:

.. code-block:: console

   python -m pip install -e .

This installs ``django-pgbulk`` and the Psycopg 3 driver with its binary
distribution. These dependency requirements describe the current package;
they are not a guarantee that every future Django version has been tested.

Django configuration
--------------------

Configure your application's ``DATABASES["default"]`` to use
``django.db.backends.postgresql``. The library does not require an entry in
``INSTALLED_APPS``. Your own app containing the models must be installed normally.

After creating a model that inherits from ``BulkSaveableModel``, generate and
apply migrations for your app as usual:

.. code-block:: console

   python manage.py makemigrations
   python manage.py migrate

Building this documentation
---------------------------

Install the documentation dependencies from the checkout and build HTML:

.. code-block:: console

   python -m pip install -e '.[docs]'
   python -m sphinx -b html -W --keep-going docs docs/_build/html

Open ``docs/_build/html/index.html``. Building the documentation does not
require Django settings or a running database.
