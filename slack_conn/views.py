from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import logging
import json

from slack_sdk import WebClient


logger = logging.getLogger('access.request')
client = WebClient(token=settings.SLACK_PF_BOT_TOKEN)


# Create your views here.
@csrf_exempt
def praise(request):
    data = json.loads(request.body)
    if 'challenge' in data:
        return JsonResponse({'challenge': data['challenge']})
    logger.warning(f'{data}')
    ret_info = {
        'status': 'Bad Request',
        'msg': 'request format is not appropriate.'
    }
    val_keys = ['event']
    for key in val_keys:
        if key not in data:
            return JsonResponse(ret_info)

    channel = data['event']['channel']
    user_mentions = data['event']['user']
    text = f"Hi, <@{user_mentions}! It's pf_bot>"
    client.chat_postMessage(
        channel=channel,
        text=text
    )
    return JsonResponse({'status': 'OK'})

