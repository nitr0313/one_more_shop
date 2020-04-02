import random
import string

from django.core.management.base import BaseCommand

from shop.models import Item

st = list(string.ascii_lowercase)


class Command(BaseCommand):
    def handle(self, *args, **options):
        for _ in range(10):
            Item.objects.create(
                title=''.join(random.choices(st, k=5)).capitalize(),
                price=float(random.randint(50, 500)),
                description="Some quick example text to build on the card title and make up the bulk of the card's content."

            )
