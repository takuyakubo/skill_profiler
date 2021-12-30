from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import logging

from slack_sdk import WebClient


logger = logging.getLogger('access.request')
client = WebClient(token=settings.SLACK_BOT_TOKEN)


# Create your views here.
@csrf_exempt
def praise(request):

    data = request.POST
    if 'challenge' in data:
        return JsonResponse({'challenge': data['challenge']})
    logger.warning(f'{data}')
    ret_info = {
        'status': 'Bad Request',
        'msg': 'request format is not appropriate.'
    }
    val_keys = ['channel_name', 'channel_id', 'text']
    for key in val_keys:
        if key not in data:
            return JsonResponse(ret_info)

    channel = data['channel_id']
    text = data['text']
    client.chat_postMessage(
        channel=channel,
        text=text
    )
    return JsonResponse({'status': 'OK'})

