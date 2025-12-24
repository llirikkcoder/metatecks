from apps.catalog.models import Category
from apps.content.models import HeaderData, FooterData


def current_user(request):
    user = (
        request.user
        if request.user.is_authenticated
        else None
    )
    return {'user': user}


def header(request):
    if request.path.startswith('/admin/'):
        return {}

    header_obj = HeaderData.get_solo()
    header_content = {
        'working_days': header_obj.working_days,
        'working_time': header_obj.working_time,
        'contacts_phone': header_obj.contacts_phone,
        'contacts_email': header_obj.contacts_email,
        'links': header_obj.get_links(),
    }

    categories = Category.objects.prefetch_related('sub_categories').filter(is_shown=True)
    header_content['categories'] = categories

    content = {'header': header_content}
    return content


def footer(request):
    if request.path.startswith('/admin/'):
        return {}

    footer_obj = FooterData.get_solo()
    footer_content = {
        'columns': footer_obj.get_columns(),
        'social_links': footer_obj.get_social_links(),
        'contacts_phone': footer_obj.contacts_phone,
        'contacts_email': footer_obj.contacts_email,
    }

    content = {'footer': footer_content}
    return content
