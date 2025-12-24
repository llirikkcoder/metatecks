from django import template
from suit import config

register = template.Library()


@register.filter(name='custom_suit_body_class')
def custom_suit_body_class(value, request):
    css_classes = []
    # CUSTOM
    # config_vars_to_add = ['toggle_changelist_top_actions', 'form_submit_on_right', 'layout']
    config_vars_to_add = ['toggle_changelist_top_actions', 'form_submit_on_right',]
    # /CUSTOM
    for each in config_vars_to_add:
        suit_conf_param = getattr(config.get_config(None, request), each, None)
        if suit_conf_param:
            value = each if isinstance(suit_conf_param, bool) \
                else '_'.join((each, suit_conf_param))
            css_classes.append('suit_%s' % value)
    # CUSTOM
    css_classes.append('suit_layout_horizontal')
    # /CUSTOM
    return ' '.join(css_classes)
