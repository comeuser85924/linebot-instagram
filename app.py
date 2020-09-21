from flask import Flask, request, abort, render_template
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
import configparser
import os
import requests
import json
import random
import unicodedata  # 幫助我們全形轉半行
from countSum import handleCount # 引入countSum.py 中的 handleCount fnction
from listview import handleListview # listview.py 中的 handleListview fnction
app = Flask(__name__)

# LINE 聊天機器人的基本資料

#local testing
# config = configparser.ConfigParser()
# config.read('config.ini')
# line_bot_api = LineBotApi(config.get('line-bot', 'channel_access_token'))
# handler = WebhookHandler(config.get('line-bot', 'channel_secret'))

#heroku
line_bot_api = LineBotApi(os.environ['channel_access_token'])
handler = WebhookHandler(os.environ['channel_secret'])

# https://www.instagram.com/account/?__a=1 只能取得文章前12筆

# https://www.instagram.com/graphql/query/?query_hash=bfa387b2992c3a52dcbe447467b4b771&variables={%22id%22:%22506333587%22,%22first%22:13,%22after%22:%22QVFBNVZfYVJlRXNrWTdSdGJ4ZERwRDJvT2YxYW5LWlNWUEtGRGdtZHJNQmp1Xzg2NnFDcHQtRzk0dTFId1ktMVM5by1LZ0FVNi1YY3B4SkxhR2tqV2JYSw==%22}
# query_hash = 從network取出來 個人頁面往下滑 查看api (不確定是什麼)
# variables = { 
#           id= 使用者id (可從 https://www.instagram.com/account/?__a=1 中取得ID)
#           first = 數量 (目前得知一次最多50筆)
#           after = end_cursor值
# }

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

    msg = event.message.text
    # print(type(msg))
    msg = msg.encode('utf-8')
    headers = {'cookie': 'ig_did=AE5CF047-1E27-4940-B4A0-7197554C736F; mid=XzeFfAALAAHpt1UUmdWWrpl7kVe2; ig_nrcb=1; datr=pxu1XwkyUYUpoR3AARXvFIb-; shbid=7352; rur=ATN; csrftoken=wtkxupPbNc0Y8s2IGiwaeyQapeVxrBds; ds_user_id=44465382319; sessionid=44465382319%3AkBAsiqAU8R8SKn%3A19; shbts=1610462481.3135202; urlgen="{\"150.116.132.139\": 131627}:1kzKsW:wR5yiz-U0sdMoRaB0_mnwuCXFvc'}
    if (('神秘帳號' in event.message.text) or (event.message.text == '天選之人')):
        msg = unicodedata.normalize('NFKC', event.message.text).replace(" ", "")
        mores = 0
        account = ''
        url=''
        if('神秘帳號' in msg):
            if('~' in msg):
                account = msg.split(':')[1].split('~')[0]
                mores = int(msg.split(':')[1].split('~')[1])
            else:
                account = msg.split(':')[1]
            url = "https://www.instagram.com/"+account+"/"
        elif(event.message.text == '天選之人'):
            url='https://www.instagram.com/graphql/query/?query_hash=3dec7e2c57367ef3da3d987d89f9dbc8&variables=%7B%22id%22%3A%2244465382319%22%2C%22include_reel%22%3Atrue%2C%22fetch_mutual%22%3Afalse%2C%22first%22%3A24%7D'
            response = requests.request("GET", url ,headers=headers)
            if(response.status_code == 200): 
                lotteryList = response.json()['data']['user']['edge_follow']['edges']
                endSum = random.randint(1,len(lotteryList)-1) 
                account = lotteryList[endSum]['node']['username']
                url = "https://www.instagram.com/"+account+"/?"
        querystring = {"__a": "1"}
        payload = ""
        # 新增ig help測試帳號
        response = requests.request("GET", url, data=payload, headers=headers, params=querystring)
        if(response.status_code == 200):
            personalFile = response.json()['graphql']['user']['edge_owner_to_timeline_media']['edges']
            if len(personalFile) == 0:
                line_bot_api.reply_message(
                    event.reply_token, TextSendMessage(text='您好，由於Instagram安全隱私問題，此人非公開帳號，所以無法取得相關資訊'))
            else:
                array = []
                for idx in range(len(personalFile)):
                    array.append(handleListview(personalFile,account,idx))

                if(mores == 1):
                    flex_message = FlexSendMessage(
                        alt_text='潘多拉之盒已開啟',
                        contents={
                            "type": "carousel",
                            "contents": array[0:10]
                        }
                    )
                elif(mores == 2):
                    flex_message = FlexSendMessage(
                        alt_text='潘多拉之盒已開啟',
                        contents={
                            "type": "carousel",
                            "contents": array[10:20]
                        }
                    )
                else:
                    flex_message = FlexSendMessage(
                        alt_text='潘多拉之盒已開啟',
                        contents={
                            "type": "carousel",
                            "contents": array[0:10]
                        }
                    )
                line_bot_api.reply_message(event.reply_token, flex_message)
        elif(response.status_code == 429):
            line_bot_api.reply_message(
                event.reply_token, TextSendMessage(text='資料過期啦！！！工程師趕緊修啊~~~~~'))
        else:
            line_bot_api.reply_message(
                event.reply_token, TextSendMessage(text='您好，您提供的帳號查無資料，請確認帳號是否輸入正確'))
    elif ('下載單圖' in event.message.text):
        msg = unicodedata.normalize('NFKC', event.message.text)
        account = msg.split(':')[1].split('-')[0]
        index = msg.split(':')[1].split('-')[1]
        url = "https://www.instagram.com/"+account+"/"
        querystring = {"__a": "1"}
        payload = ""
        response = requests.request(
            "GET", url, data=payload, headers=headers, params=querystring)
        if(response.status_code == 200):
            personalFile = response.json(
            )['graphql']['user']['edge_owner_to_timeline_media']['edges']
            line_bot_api.reply_message(event.reply_token, ImageSendMessage(
                original_content_url=personalFile[int(index)]['node']['display_url'], preview_image_url=personalFile[int(index)]['node']['display_url']))
        else:
            line_bot_api.reply_message(
                event.reply_token, TextSendMessage(text='您好，您提供的帳號查無資料，請確認帳號是否輸入正確'))
    elif ('下載多圖' in event.message.text):
        msg = unicodedata.normalize('NFKC', event.message.text)
        account = msg.split(':')[1].split('順序')[0]
        index = int(msg.split(':')[1].split('順序')[1])
        url = "https://www.instagram.com/"+account+"/"
        querystring = {"__a": "1"}
        payload = ""
        response = requests.request("GET", url, data=payload, headers=headers, params=querystring)
        if(response.status_code == 200):
            personalFile = response.json()['graphql']['user']['edge_owner_to_timeline_media']['edges']
            if('edge_sidecar_to_children' in personalFile[index]['node']):
                array = []
                for idx in range(len(personalFile[index]['node']['edge_sidecar_to_children']['edges'])):
                    array.append({
                        "type": "bubble",
                        "body": {
                                "type": "box",
                                "layout": "vertical",
                                "contents": [
                                    {
                                        "type": "image",
                                        "url": personalFile[index]['node']['edge_sidecar_to_children']['edges'][idx]['node']['display_url'],
                                        "size": "full",
                                        "aspectMode": "cover",
                                        "aspectRatio": "2:3",
                                        "gravity": "top",
                                        "action": {
                                            "type": "message",
                                            "label": "action",
                                            "text": "顯示多圖檔:"+account + '-' + str(index) +"-"+str(idx)
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
    elif ('顯示多圖檔' in event.message.text):
        msg = unicodedata.normalize('NFKC', event.message.text)
        account = msg.split(':')[1].split('-')[0]
        main_index = int(msg.split(':')[1].split('-')[1])
        item_index = int(msg.split(':')[1].split('-')[2])
        url = "https://www.instagram.com/"+account+"/"
        querystring = {"__a": "1"}
        payload = ""
        response = requests.request("GET", url, data=payload, headers=headers, params=querystring)
        if(response.status_code == 200):
            personalFile = response.json()['graphql']['user']['edge_owner_to_timeline_media']['edges']
            line_bot_api.reply_message(event.reply_token, ImageSendMessage(
                original_content_url= personalFile[main_index]['node']['edge_sidecar_to_children']['edges'][item_index]['node']['display_url'],
                 preview_image_url= personalFile[main_index]['node']['edge_sidecar_to_children']['edges'][item_index]['node']['display_url']))

    return 'OK2'

if __name__ == "__main__":
    app.run()
