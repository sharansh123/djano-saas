from django.core.management import BaseCommand
from subscriptions.models import Subscription

class Command(BaseCommand):

    def handle(self, *args, **options):
        print("hello world")
        qs = Subscription.objects.all()
        for obj in qs:
            sub_perms = obj.permissions.all()
            for grp in obj.groups.all():
                grp.permissions.set(sub_perms)