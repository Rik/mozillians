from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import Count

import commonware.log
import cronjobs

from groups.models import AUTO_COMPLETE_COUNT, Group


log = commonware.log.getLogger('m.cron')


@cronjobs.register
def assign_autocomplete_to_groups():
    """Hourly job to assign autocomplete status to popular Mozillian groups."""
    # Only assign status to non-system groups.
    # TODO: add stats.d timer here
    for g in (Group.objects.filter(always_auto_complete=False, system=False)
                           .annotate(count=Count('userprofile'))):
        g.auto_complete = g.count > AUTO_COMPLETE_COUNT
        g.save()


@cronjobs.register
def assign_staff_to_early_users():
    """Add "staff" group to all auto-vouched users."""
    staff = Group.objects.get(name='staff')
    staff_users = []

    for d in settings.AUTO_VOUCH_DOMAINS:
        if not staff_users:
            staff_users = User.objects.filter(email__iendswith=d)
        else:
            staff_users = staff_users | staff_users.filter(email__iendswith=d)

    for u in staff_users:
        u.get_profile().groups.add(staff)
