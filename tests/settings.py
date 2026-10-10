SECRET_KEY = "django-bulk-save-tests"
INSTALLED_APPS = ["tests"]
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
MIGRATION_MODULES = {"tests": None}
