from flask import Flask, request, json
from discord import Webhook, RequestsWebhookAdapter
import requests
import os
import logging

application = Flask(__name__)

gunicorn_logger = logging.getLogger('gunicorn.error')
application.logger.handlers = gunicorn_logger.handlers
application.logger.setLevel(gunicorn_logger.level)

WEBHOOK = os.environ['WEBHOOK_URL']
KEY = os.environ['APP_KEY']
MIN_SATS = int(os.environ['MIN_SATS'])
BOT_USER_NAME = os.environ['BOT_USER_NAME']

def get_sat_value(sats):
    usd_response = requests.get('https://api.coinbase.com/v2/prices/spot?currency=USD').json()
    usd_price = float(usd_response['data']['amount'])
    usd_sat_value = usd_price / 100000000
    usd_value = sats * usd_sat_value

    cad_response = requests.get('https://api.coinbase.com/v2/prices/spot?currency=CAD').json()
    cad_price = float(cad_response['data']['amount'])
    cad_sat_value = cad_price / 100000000
    cad_value = sats * cad_sat_value
    return [usd_value, cad_value]

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
        sats_value = get_sat_value(sats)
        formatted_message = f"{sender} sent a donation of {sats} sats (~${sats_value[0]:.2f} USD / ~${sats_value[1]:.2f} CAD) with the message: {text}"
        return formatted_message
    except:
        return "Somebody donated some sats, but the details were lost in transit. Sorry."

@application.route('/<path>', methods=['POST'])
def satoshi_msg(path):
    if path == KEY:
        data = json.loads(request.data)
        if data_validator(data) is False:
            return ('', 204)
        application.logger.info(data)
        message = format_message(data)
        webhook = Webhook.from_url(WEBHOOK, adapter=RequestsWebhookAdapter())
        webhook.send(message, username=BOT_USER_NAME)
        return ('', 204)
    else:
        return ('', 404)

if __name__ == '__main__':
    application.run(host="127.0.0.1", port=5000)