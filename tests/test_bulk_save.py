from unittest.mock import patch

import pytest
import pgbulk
from django.db import IntegrityError, connection
from django.test.utils import CaptureQueriesContext

from django_bulk_save import BulkSaveableModel
from tests.models import Item

pytestmark = pytest.mark.django_db


def test_base_model_is_abstract_and_hook_is_optional():
    assert BulkSaveableModel._meta.abstract
    item = Item(name="example")

    assert BulkSaveableModel.before_save(item) is None


def test_empty_context():
    with Item.bulk_save() as context:
        assert context.registry == []

    assert Item.objects.count() == 0


def test_creates_instances_after_running_custom_logic():
    items = [Item(name=" first "), Item(name=" second ")]

    with Item.bulk_save() as context:
        for item in items:
            context.register(item, update_fields=["name"])
        assert Item.objects.count() == 0

    assert list(Item.objects.order_by("pk").values_list("name", flat=True)) == [
        "first",
        "second",
    ]
    assert all(item.pk is not None and item.hook_calls == 1 for item in items)


def test_updates_are_grouped_by_fields_and_preserve_other_columns():
    first, second, third = Item.objects.bulk_create(
        [Item(name="first"), Item(name="second"), Item(name="third")]
    )
    first.name, second.name = " first updated ", " second updated "
    first.quantity = 99
    third.quantity = 3
    manager = Item.objects

    postgres = connection.vendor == "postgresql"
    update_patch = (
        patch("django_bulk_save.models.pgbulk.update", wraps=pgbulk.update)
        if postgres
        else patch.object(manager, "bulk_update", wraps=manager.bulk_update)
    )
    with update_patch as update:
        with Item.bulk_save() as context:
            context.register(first, update_fields=["name"])
            context.register(second, update_fields=["name"])
            context.register(third, update_fields=["quantity"])

    assert update.call_count == 2
    prefix = (Item,) if postgres else ()
    field_argument = "update_fields" if postgres else "fields"
    assert update.call_args_list[0].args == (*prefix, [first, second])
    assert update.call_args_list[0].kwargs == {field_argument: ["name"]}
    assert update.call_args_list[1].args == (*prefix, [third])
    assert update.call_args_list[1].kwargs == {field_argument: ["quantity"]}
    first.refresh_from_db()
    second.refresh_from_db()
    third.refresh_from_db()
    assert (first.name, first.quantity) == ("first updated", 0)
    assert second.name == "second updated"
    assert third.quantity == 3
    assert all(item.hook_calls == 1 for item in (first, second, third))


def test_creates_and_updates_in_the_same_context():
    existing = Item.objects.create(name="original")
    existing.name = " changed "
    new = Item(name=" new ")

    with Item.bulk_save() as context:
        context.register(existing, update_fields=["name"])
        context.register(new, update_fields=["name"])

    existing.refresh_from_db()
    assert existing.name == "changed"
    assert Item.objects.get(pk=new.pk).name == "new"
    assert Item.objects.count() == 2


def test_validation_error_propagates_without_persisting_changes():
    existing = Item.objects.create(name="original")
    existing.name = "changed"

    with pytest.raises(ValueError, match="Name must not be empty"):
        with Item.bulk_save() as context:
            context.register(existing, update_fields=["name"])
            context.register(Item(name="valid"), update_fields=["name"])
            context.register(Item(name="   "), update_fields=["name"])

    existing.refresh_from_db()
    assert existing.name == "original"
    assert Item.objects.count() == 1


def test_exception_in_context_body_rolls_back_writes():
    with pytest.raises(RuntimeError, match="stop"):
        with Item.bulk_save() as context:
            Item.objects.create(name="immediate write")
            context.register(Item(name="pending"), update_fields=["name"])
            raise RuntimeError("stop")

    assert Item.objects.count() == 0


def test_update_failure_rolls_back_prior_bulk_create():
    existing = Item.objects.create(name="original")
    existing.quantity = None  # Violates the database NOT NULL constraint.

    with pytest.raises(IntegrityError):
        with Item.bulk_save() as context:
            context.register(Item(name="new"), update_fields=["name"])
            context.register(existing, update_fields=["quantity"])

    existing.refresh_from_db()
    assert existing.quantity == 0
    assert Item.objects.count() == 1


@pytest.mark.skipif(connection.vendor != "postgresql", reason="Requires PostgreSQL")
def test_postgres_updates_use_values_and_persist_distinct_values():
    items = Item.objects.bulk_create([Item(name=f"item {i}") for i in range(100)])
    for i, item in enumerate(items):
        item.name = f" updated '{i}' "
        item.quantity = i

    with CaptureQueriesContext(connection) as queries:
        with Item.bulk_save() as context:
            for item in items:
                context.register(item, update_fields=["name", "quantity"])

    updates = [query["sql"] for query in queries if query["sql"].lstrip().startswith("UPDATE")]
    assert len(updates) == 1
    assert "VALUES" in updates[0]
    assert "CASE" not in updates[0]
    assert list(Item.objects.order_by("pk").values_list("name", "quantity")) == [
        (f"updated '{i}'", i) for i in range(100)
    ]
    assert all(item.hook_calls == 1 for item in items)


def test_empty_update_fields_roll_back_prior_create():
    existing = Item.objects.create(name="original")
    existing.name = "changed"

    with pytest.raises(ValueError, match="Field names must be given"):
        with Item.bulk_save() as context:
            context.register(Item(name="new"), update_fields=["name"])
            context.register(existing, update_fields=[])

    existing.refresh_from_db()
    assert existing.name == "original"
    assert Item.objects.count() == 1
