
def make_banner_published(banner):
    banner.is_published = True
    banner.end_dt = None
    banner.save()
    return True


def make_banner_unpublished(banner):
    banner.is_published = False
    banner.save()
    return True
