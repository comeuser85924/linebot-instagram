
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
import configparser
import requests

import unicodedata # 幫助我們全形轉半行
app = Flask(__name__)

# LINE 聊天機器人的基本資料
config = configparser.ConfigParser()
config.read('config.ini')

line_bot_api = LineBotApi(config.get('line-bot', 'channel_access_token'))
handler = WebhookHandler(config.get('line-bot', 'channel_secret'))

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    print(body, signature)
    try:
        # print(body, signature)
        handler.handle(body, signature)

    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    
    msg = event.message.text
    print(msg)
    # print(type(msg))
    msg = msg.encode('utf-8')
    if ('帳號' in event.message.text):
        msg = unicodedata.normalize('NFKC',event.message.text)
        account = msg.split(':')[1]
        url = 'https://www.instagram.com/'+account+'/?__a=1'
        response = requests.get(url)
        if(response.status_code == 200):
            personalFile = response.json()['graphql']['user']['edge_owner_to_timeline_media']['edges']
            array = []
            for idx in range(len(personalFile)):
                array.append({
                        "type": "bubble",
                        "body": {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "image",
                                    "url": personalFile[idx]['node']['display_url'],
                                    "size": "full",
                                    "aspectMode": "cover",
                                    "aspectRatio": "2:3",
                                    "gravity": "top",
                                    "action": {
                                        "type": "message",
                                        "label": "action",
                                        "text": "顯示圖檔:"+account +'-'+ str(idx)
                                    }
                                }
                            ],
                            "paddingAll": "0px"
                        }
                    })
            flex_message = FlexSendMessage(
                alt_text='潘多拉之盒已開啟',
                contents={
                    "type": "carousel",
                    "contents": array[0:10]
                }
            )
            line_bot_api.reply_message(event.reply_token, flex_message)
        else:
            line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text='您好，您提供的帳號查無資料，請確認帳號是否輸入正確'))
    elif ('顯示圖檔' in event.message.text):
        msg = unicodedata.normalize('NFKC',event.message.text)
        account = msg.split(':')[1].split('-')[0]
        ig_url = 'https://www.instagram.com/'+account+'/?__a=1'
        index = msg.split(':')[1].split('-')[1]
        response = requests.get(ig_url)
        if(response.status_code == 200):
            personalFile = response.json()['graphql']['user']['edge_owner_to_timeline_media']['edges']
            line_bot_api.reply_message(event.reply_token, ImageSendMessage(
                original_content_url=personalFile[int(index)]['node']['display_url'], preview_image_url=personalFile[int(index)]['node']['display_url']))
        else:
            line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text='您好，您提供的帳號查無資料，請確認帳號是否輸入正確'))  
    return 'OK2'


if __name__ == "__main__":
    app.run()
