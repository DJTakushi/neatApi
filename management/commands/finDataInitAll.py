from django.core.management.base import BaseCommand, CommandError
from neatApi.models import finData
class Command(BaseCommand):
    help = 'Deletes all finData instances'

    def handle(self, *args, **kwargs):
        try:
            # put startup code here
            finData.init()
        except:
            raise CommandError('finDataDeleteAll failed.')
