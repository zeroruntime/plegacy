from accounts.models import CustomUser
from admissions.choices import ALUMNI_YEAR_GROUPS


YEAR_GROUP_VALIDATION_ROUTES = {
    year_group: {
        'role': 'president',
        'year_group': year_group,
    }
    for year_group in ALUMNI_YEAR_GROUPS
}


def get_validation_route(year_group):
    return YEAR_GROUP_VALIDATION_ROUTES.get(year_group)


def get_validation_recipient(year_group):
    route = get_validation_route(year_group)
    if not route:
        return None

    return CustomUser.objects.filter(
        role=route['role'],
        year_group=route['year_group'],
        is_active=True,
    ).first()
