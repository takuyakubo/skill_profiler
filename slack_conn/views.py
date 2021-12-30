from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import logging
import json

from slack_sdk import WebClient


logger = logging.getLogger('access.request')
client = WebClient(token=settings.SLACK_PF_BOT_TOKEN)


# Create your views here.
def validate(data):
    if 'challenge' in data:
        return JsonResponse({'challenge': data['challenge']})

    ret_info = {
        'status': 'Bad Request',
        'msg': 'request format is not appropriate.'
    }
    val_keys = ['event']
    for key in val_keys:
        if key not in data:
            return JsonResponse(ret_info)


def parse_text(data):
    self_id = data['authorizations'][0]['user_id']
    recv_elements = []
    for block in data['event']['blocks']:
        for el in block['elements']:
            for word in el['elements']:
                if word['type'] == 'user' and word['user_id'] == self_id:
                    continue
                recv_elements.append(word)
    first_word = recv_elements[0]
    if first_word['type'] == 'text':
        first_text = first_word['text']
        if '+1' in first_text:
            return 'praise', recv_elements[1:]
        if 'show' in first_text:
            pass


def view_help(data):
    channel = data['event']['channel']
    user_mentions = data['event']['user']
    text = f"こんにちは, <@{user_mentions}>さん!\n使い方は次のとおりです。\n" \
           f"- 誰かに加点したい時、\n" \
           f"  +1 @someone (内容 optional) @someone ...\n" \
           f"  ex) +1 @john wrote a great document @hanako データベースの設計\n" \
           f"- 自分の状況を知りたい時、\n" \
           f"  show my status or sms \n" \
           f"- 自分への履歴が知りたい時、\n" \
           f"  show my history (number optional(default=10)) or smh (number)\n" \
           f"- 自分からの履歴が知りたい時、\n" \
           f"  show my activities (number optional(default=10)) or sma (number)"
    client.chat_postEphemeral(
        user=user_mentions,
        channel=channel,
        text=text
    )


@csrf_exempt
def praise(request):
    data = json.loads(request.body)
    invalid_case_response = validate(data)
    if invalid_case_response:
        logger.warning(f'{data}')
        return invalid_case_response
    logger.warning(f'{data}')
    view_help(data)
    return JsonResponse({'status': 'OK'})

