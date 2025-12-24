from apps.third_party.cml.models import ImportedGroup, ImportedProperty, ImportedPropertyVariant, ImportedProduct


def import_catalog(models=None):
    models = models or ['groups', 'properties', 'products']
