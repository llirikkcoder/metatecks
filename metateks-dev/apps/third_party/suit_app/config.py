from django.contrib.admin.options import ModelAdmin

from suit.apps import DjangoSuitConfig


class SuitConfig(DjangoSuitConfig):
    toggle_changelist_top_actions = True
    layout = 'horizontal'

    def setup_model_admin_defaults(self):
        """
        Override some ModelAdmin defaults
        """
        if self.toggle_changelist_top_actions:
            ModelAdmin.actions_on_top = True
            ModelAdmin.actions_on_bottom = False
        else:
            ModelAdmin.actions_on_top = False
            ModelAdmin.actions_on_bottom = True

        if self.list_per_page:
            ModelAdmin.list_per_page = self.list_per_page
