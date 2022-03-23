from flask import Flask, request, json
from discord import Webhook, RequestsWebhookAdapter
import requests
import os

application = Flask(__name__)

WEBHOOK = os.environ['WEBHOOK_URL']

KEY = os.environ['APP_KEY']

MIN_SATS = int(os.environ['MIN_SATS'])

def data_validator(raw_message):
    if raw_message['value_msat'] < MIN_SATS:
        return False
    return True

def format_message(raw_message):
    try:
        sender = raw_message['sender']
        text = raw_message['message_plain']
        sats = raw_message['value_msat']
        sats = int(sats) / 1000
        sats = round(sats)
        formatted_message = f"{sender} sent a donation of {sats} sats with the message: {text}"
        return formatted_message
    except:
        return "Somebody donated some sats, but the details were lost in transit. Sorry."

@application.route('/<path>', methods=['POST'])
def satoshi_msg(path):
    if path == KEY:
        data = json.loads(request.data)
        if data_validator(data) is False:
            return ('', 204)
        message = format_message(data)
        webhook = Webhook.from_url(WEBHOOK, adapter=RequestsWebhookAdapter())
        webhook.send(message, username="Hog Story Boostagram")
        return ('', 204)
    else:
        return ('', 404)

if __name__ == '__main__':
    application.run(host="127.0.0.1", port=5000)