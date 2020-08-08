
from flask import Flask, request, abort, render_template
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
import configparser
import requests
import json
import unicodedata # 幫助我們全形轉半行
app = Flask(__name__)

# LINE 聊天機器人的基本資料
config = configparser.ConfigParser()
config.read('config.ini')

line_bot_api = LineBotApi(config.get('line-bot', 'channel_access_token'))
handler = WebhookHandler(config.get('line-bot', 'channel_secret'))

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    try:
        print('確認進到callback')
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    
    msg = event.message.text
    # print(type(msg))
    msg = msg.encode('utf-8')
    if ('帳號' in event.message.text):
        
        msg = unicodedata.normalize('NFKC',event.message.text)
        account = msg.split(':')[1]
        url = "https://www.instagram.com/"+account+"/"
        querystring = {"__a":"1"}
        payload = ""
        headers = {'cookie': 'ig_did=AA7BB833-E8ED-4B57-94A7-6F54995F6613; mid=Xy5jkQALAAENDAoMv4SJhALi6s0C; fbm_124024574287414=base_domain=.instagram.com; fbsr_124024574287414=Pik34X2Ds4COWu9V7Z9Z2gKw9ieLQmjFII3NBkf75_g.eyJ1c2VyX2lkIjoiMTAwMDAwMzM1ODgxMDM2IiwiY29kZSI6IkFRQm5WaUJFTmQ3QTNFQW5WS0ZPUnZ2aGd2ZzV3MXNBdWd2RWxrTXJjMWZNbVNmOEZKcE5oM1ViQmVBdkZucktJR3lMOWt0eXJPTVgyWWlJSG4wVnlwT0RmZnRWNDA4QmRaVGJfWXVjX1ZDXzl2dTZEWnN4bDF1bmxYZ1pEbnUycjd5NHBqX1djYmc4OVNfYzJDNmpwdkNybVNBcmlQY3N4ZFhVTW1oaldMUVk5TU5KRHUxOFlDRnpFODlLWWlyYjZmTzk1TnBmNVcxX3dJRDREbm5BQnhjdFRpVk5jaGMxMjNQUGQwLWxCRTM5b2ZsVFB6ZlJZZGpubElFc1FZVkxrNk1ZREppejdwNmR4U1dxZFJEMDhfbnZtZ2hoaWpxS3ZWeW5BcUZJcFhvUlV6M3NVNjROZ0tTQ1RISUtfTURRRWdxdXh6NUJweDVhZU1XZ3NBWXdzbGpOIiwib2F1dGhfdG9rZW4iOiJFQUFCd3pMaXhuallCQUxrZ2xwQWJsWkNFdGlMUlRqS24zUTNMQzM4Zkw3dGRaQWtGbWk2V0JaQkxEQ1Jxb2hwNGFsQ3hGOXhBbEo3UmNkRzRzR0dueGRqWVpBMmxaQjlsVFpBbGdSRnJxWWJua1RTWkJqQmZOU3Y5cVRuMzNJN1lTZ280bGpFZVh5NTY3c1E4WkJDRmhRb3FwN2t1eWNMNlpBOUhLMWJnbFZUWkJHYmRET0hrMWFEOXZnIiwiYWxnb3JpdGhtIjoiSE1BQy1TSEEyNTYiLCJpc3N1ZWRfYXQiOjE1OTY4NzU2ODJ9; csrftoken=fxjaPYfL12MdeHJE0Hxp97sqH2InqCwa; ds_user_id=1698926261; sessionid=1698926261%3AdsGUDhGrIRqHOl%3A20; shbid=15998; shbts=1596875684.2646637; rur=VLL; urlgen="{\"150.116.182.98\": 131627}:1k4LU8:WLU9Hz1_Sd7u40hAAixjKqQRxmM"'}
        response = requests.request("GET", url, data=payload, headers=headers, params=querystring)

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
            # print(array[0:10])
            flex_message = FlexSendMessage(
                alt_text='潘多拉之盒已開啟',
                contents={
                    "type": "carousel",
                    "contents": array[0:10]
                }
            )
            # print(flex_message)
            line_bot_api.reply_message(event.reply_token, flex_message)
        else:
            line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text='您好，您提供的帳號查無資料，請確認帳號是否輸入正確'))
    elif ('顯示圖檔' in event.message.text):
        msg = unicodedata.normalize('NFKC',event.message.text)
        account = msg.split(':')[1].split('-')[0]
        index = msg.split(':')[1].split('-')[1]
        url = "https://www.instagram.com/"+account+"/"
        querystring = {"__a":"1"}
        payload = ""
        headers = {'cookie': 'ig_did=AA7BB833-E8ED-4B57-94A7-6F54995F6613; mid=Xy5jkQALAAENDAoMv4SJhALi6s0C; fbm_124024574287414=base_domain=.instagram.com; fbsr_124024574287414=Pik34X2Ds4COWu9V7Z9Z2gKw9ieLQmjFII3NBkf75_g.eyJ1c2VyX2lkIjoiMTAwMDAwMzM1ODgxMDM2IiwiY29kZSI6IkFRQm5WaUJFTmQ3QTNFQW5WS0ZPUnZ2aGd2ZzV3MXNBdWd2RWxrTXJjMWZNbVNmOEZKcE5oM1ViQmVBdkZucktJR3lMOWt0eXJPTVgyWWlJSG4wVnlwT0RmZnRWNDA4QmRaVGJfWXVjX1ZDXzl2dTZEWnN4bDF1bmxYZ1pEbnUycjd5NHBqX1djYmc4OVNfYzJDNmpwdkNybVNBcmlQY3N4ZFhVTW1oaldMUVk5TU5KRHUxOFlDRnpFODlLWWlyYjZmTzk1TnBmNVcxX3dJRDREbm5BQnhjdFRpVk5jaGMxMjNQUGQwLWxCRTM5b2ZsVFB6ZlJZZGpubElFc1FZVkxrNk1ZREppejdwNmR4U1dxZFJEMDhfbnZtZ2hoaWpxS3ZWeW5BcUZJcFhvUlV6M3NVNjROZ0tTQ1RISUtfTURRRWdxdXh6NUJweDVhZU1XZ3NBWXdzbGpOIiwib2F1dGhfdG9rZW4iOiJFQUFCd3pMaXhuallCQUxrZ2xwQWJsWkNFdGlMUlRqS24zUTNMQzM4Zkw3dGRaQWtGbWk2V0JaQkxEQ1Jxb2hwNGFsQ3hGOXhBbEo3UmNkRzRzR0dueGRqWVpBMmxaQjlsVFpBbGdSRnJxWWJua1RTWkJqQmZOU3Y5cVRuMzNJN1lTZ280bGpFZVh5NTY3c1E4WkJDRmhRb3FwN2t1eWNMNlpBOUhLMWJnbFZUWkJHYmRET0hrMWFEOXZnIiwiYWxnb3JpdGhtIjoiSE1BQy1TSEEyNTYiLCJpc3N1ZWRfYXQiOjE1OTY4NzU2ODJ9; csrftoken=fxjaPYfL12MdeHJE0Hxp97sqH2InqCwa; ds_user_id=1698926261; sessionid=1698926261%3AdsGUDhGrIRqHOl%3A20; shbid=15998; shbts=1596875684.2646637; rur=VLL; urlgen="{\"150.116.182.98\": 131627}:1k4LU8:WLU9Hz1_Sd7u40hAAixjKqQRxmM"'}
        response = requests.request("GET", url, data=payload, headers=headers, params=querystring)
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
