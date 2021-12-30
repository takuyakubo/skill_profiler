from django.core.management.base import BaseCommand

from django.contrib.auth import get_user_model
from django.conf import settings

from slack_sdk import WebClient

from user_profile.models import UProfile

from time import sleep
client = WebClient(token=settings.SLACK_BOT_TOKEN)
User = get_user_model()


class Command(BaseCommand):
    help = 'sync slack users'

    def handle(self, *args, **options):
        api_response = client.users_list()
        members = api_response['members']
        next_cursor = api_response['response_metadata']['next_cursor']
        while next_cursor != '':
            api_response = client.users_list(cursor=next_cursor)
            members += api_response['members']
            next_cursor = api_response['response_metadata']['next_cursor']
            sleep(5)
        for member in members:
            if not member['deleted'] and member['is_email_confirmed'] and not member['is_restricted']:
                user, created = User.objects.update_or_create(
                    username=member['id'],
                    first_name=member['name'].split('.')[0],
                    last_name=member['name'].split('.')[1],
                    email=member['profile']['email']
                )
                UProfile.objects.update_or_create(user=user)


        self.stdout.write('success')
