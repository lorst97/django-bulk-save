from django_bulk_save.models import BulkSaveContext


def test_register_preserves_instances_and_update_fields():
    context = BulkSaveContext()
    first, second = object(), object()

    context.register(first, update_fields=["name"])
    context.register(second, update_fields=["quantity"])

    assert context.registry == [(first, ["name"]), (second, ["quantity"])]


def test_contexts_have_independent_registries():
    first, second = BulkSaveContext(), BulkSaveContext()

    first.register(object(), update_fields=["name"])

    assert second.registry == []


def test_flush_clears_registry():
    context = BulkSaveContext()
    context.register(object(), update_fields=["name"])

    context.flush()

    assert context.registry == []
