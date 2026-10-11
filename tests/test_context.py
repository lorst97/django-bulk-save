import pytest

from django_bulk_save import InvalidUpdateFieldsError
from django_bulk_save.models import BulkSaveContext


def test_register_preserves_instances_and_update_fields():
    context = BulkSaveContext()
    first, second = object(), object()

    context.register(first, update_fields=["name"])
    context.register(second, update_fields=["quantity"])

    assert context.registry == [(first, ("name",)), (second, ("quantity",))]


def test_contexts_have_independent_registries():
    first, second = BulkSaveContext(), BulkSaveContext()

    first.register(object(), update_fields=["name"])

    assert second.registry == []


def test_clear_discards_registry():
    context = BulkSaveContext()
    context.register(object(), update_fields=["name"])

    context.clear()

    assert context.registry == []


def test_register_snapshots_update_fields():
    context = BulkSaveContext()
    fields = ["name"]
    instance = object()
    context.register(instance, fields)
    fields.append("quantity")
    assert context.registry == [(instance, ("name",))]


@pytest.mark.parametrize("fields", [None, "name", [None], [""], 42])
def test_invalid_update_fields_are_not_registered(fields):
    context = BulkSaveContext()
    with pytest.raises(InvalidUpdateFieldsError):
        context.register(object(), fields)
    assert context.registry == []
