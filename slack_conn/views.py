from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.contrib.auth import get_user_model
import logging
import json

from slack_sdk import WebClient


User = get_user_model()
logger = logging.getLogger('access.request')
client = WebClient(token=settings.SLACK_PF_BOT_TOKEN)


# Create your views here.
def validate(data, val_keys):
    if 'challenge' in data:
        return JsonResponse({'challenge': data['challenge']})

    ret_info = {
        'status': 'Bad Request',
        'msg': 'request format is not appropriate.'
    }

    for key in val_keys:
        if key not in data:
            return JsonResponse(ret_info)


def regularize(text, rem_id):
    return text.replace(f'<@{rem_id}>', '').strip()


def parse_(text, mode):
    rules_mention = {'+1': praise,}
    rules_command = {'show my history': 'smh',
             'smh': 'smh',
             'show my status': 'sms',
             'sms': 'sms',
             'show my activity': 'sma',
             'sma': 'sma',}
    rules = rules_command if mode == 'command' else rules_mention  # if it is mention
    view_help = view_help_command if mode == 'command' else view_help_mention  # if it is mention
    for k, v in rules.items():
        if text.startswith(k):
            return v
    return view_help


def view_help_command(channel, user_mentions, reg_text):
    text = f"こんにちは, <@{user_mentions}>さん!\n使い方は次のとおりです。\n" \
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


def view_help_mention(channel, user_mentions, reg_text):
    text = f"こんにちは, <@{user_mentions}>さん!\n使い方は次のとおりです。\n" \
           f"- 誰かに加点したい時、\n" \
           f"  +1 @someone (内容 optional) @someone ...\n" \
           f"  ex) +1 @john wrote a great document @hanako データベースの設計\n" \
           f"  注意：自分自身には加点できません。"
    client.chat_postEphemeral(
        user=user_mentions,
        channel=channel,
        text=text
    )


def praise(channel, user_mentions, reg_text):
    text_ = reg_text[2:].strip()
    targets_raw = text_.split('<@')
    if len(targets_raw) < 2:
        view_help_mention(channel, user_mentions, reg_text)
        return
    targets_ = [{'user': tr.split('>')[0],
                'content': tr.split('>')[1].strip()}
                for tr in targets_raw[1:]]
    targets = dict()
    for t in targets_:
        if t['user'] == user_mentions:
            continue
        if t['user'] not in targets and User.objects.filter(username=t['user']).exists():
            targets[t['user']] = [t['content']]
        else:
            if t['content'] not in targets[t['user']]:
                targets[t['user']].append(t['content'])
    if not targets:
        view_help_mention(channel, user_mentions, reg_text)
        return

    send_text = f"<@{user_mentions}>さんは次の人に「ありがとう」と言っています。\n"
    for user in targets:
        send_text += f"-------------------\n<@{user}>さん。"
        reasons = [r for r in targets[user] if r != '']
        if reasons:
            send_text += f"理由：{', '.join(reasons)}"
        send_text += f"\n<@{user}>さんは現在nポイントです。\n"
    client.chat_postMessage(
        channel=channel,
        text=send_text
    )


def under_const(channel, user_mentions, function_key):
    text = f'機能: {function_key} は、開発中です。'

    client.chat_postEphemeral(
        user=user_mentions,
        channel=channel,
        text=text
    )


@csrf_exempt
def mention(request):
    data = json.loads(request.body)
    invalid_case_response = validate(data, val_keys=['event'])
    if invalid_case_response:
        logger.warning(f'{data}')
        return invalid_case_response

    self_id = data['authorizations'][0]['user_id']
    recv_text = data['event']['text']
    reg_text = regularize(recv_text, self_id)

    reaction = parse_(reg_text, 'mention')
    channel = data['event']['channel']
    user_mentions = data['event']['user']
    logger.warning(f'{reg_text}')
    if callable(reaction):
        reaction(channel, user_mentions, reg_text)
    else:
        under_const(channel, user_mentions, reaction)

    return JsonResponse({'status': 'OK'})


@csrf_exempt
def profile(request):
    data = request.POST
    # logger.warning(f'{data}')
    invalid_case_response = validate(data, val_keys=['text', 'channel_id', 'user_id'])
    if invalid_case_response:
        logger.warning(f'{data}')
        return invalid_case_response

    reg_text = data['text'].strip()
    reaction = parse_(reg_text, 'command')
    channel = data['channel_id']
    user_mentions = data['user_id']
    if callable(reaction):
        reaction(channel, user_mentions, reg_text)
    else:
        under_const(channel, user_mentions, reaction)
    return JsonResponse({'status': 'OK'})
