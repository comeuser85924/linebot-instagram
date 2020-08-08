
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
app = Flask(__name__)

# LINE 聊天機器人的基本資料
config = configparser.ConfigParser()
config.read('config.ini')

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

def handleCount(dataList):
    if('edge_sidecar_to_children' in dataList):
        return len(dataList['edge_sidecar_to_children']['edges'])
    return 1
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

    msg = event.message.text
    # print(type(msg))
    msg = msg.encode('utf-8')
    headers = {'cookie': 'ig_did=AE5CF047-1E27-4940-B4A0-7197554C736F; mid=XzeFfAALAAHpt1UUmdWWrpl7kVe2; ds_user_id=40346245145; csrftoken=g7bSE3UVfGAN9je1hDrMRV3vmiOAnqXY; sessionid=40346245145%3ATLNKRMHXLKOR0h%3A12; shbid=12878; shbts=1600336282.0021117; rur=ASH; urlgen="{\"220.134.112.170\": 3462}:1kIqeL:9gRjocByF2-gEwik8kNwy8P_GDk"'}
    if (('神秘帳號' in event.message.text) or ('instagram.com' in event.message.text) or (event.message.text == '天選之人')):
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
        elif('instagram.com' in msg):
            # 處理網址 確認取得帳號
            for i in range(0,len(msg)):
                if (msg[i] == '?'):
                    url = msg[0:i]
        elif(event.message.text == '天選之人'):
            url='https://www.instagram.com/graphql/query/?query_hash=d04b0a864b4b54837c0d870b0e77e076&variables={"id":"40346245145","include_reel":true,"fetch_mutual":false,"first":50}'
            response = requests.request("GET", url ,headers=headers)
            if(response.status_code == 200): 
                lotteryList = response.json()['data']['user']['edge_follow']['edges']
                endSum = random.randint(1,len(lotteryList)) 
                account = lotteryList[endSum]['node']['username']
                url = "https://www.instagram.com/"+account+"/"
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
                    if (handleCount(personalFile[idx]['node']) != 1):
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
                                                "text": "下載單圖:"+account + '-' + str(idx)
                                            }
                                        },
                                        {
                                            "type": "box",
                                            "layout": "vertical",
                                            "contents": [
                                            {
                                                "type": "box",
                                                "layout": "vertical",
                                                "contents": [
                                                {
                                                    "type": "filler"
                                                },
                                                {
                                                    "type": "box",
                                                    "layout": "baseline",
                                                    "contents": [
                                                    {
                                                        "type": "filler"
                                                    },
                                                    {
                                                        "type": "text",
                                                        "text": "我想一次看" + str(handleCount(personalFile[idx]['node'])) + '張',
                                                        "color": "#ffffff",
                                                        "flex": 0,
                                                        "offsetTop": "-2px",
                                                        "weight": "bold",
                                                        "action": {
                                                            "type": "message",
                                                            "label": "action",
                                                            "text": "下載多圖:"+account + "順序" + str(idx)
                                                        }
                                                    },
                                                    {
                                                        "type": "filler"
                                                    }
                                                    ],
                                                    "spacing": "sm"
                                                },
                                                {
                                                    "type": "filler"
                                                }
                                                ],
                                                "borderWidth": "1px",
                                                "cornerRadius": "4px",
                                                "spacing": "sm",
                                                "borderColor": "#ffffff",
                                                "margin": "xxl",
                                                "height": "40px"
                                            }
                                            ],
                                            "position": "absolute",
                                            "offsetBottom": "0px",
                                            "offsetStart": "0px",
                                            "offsetEnd": "0px",
                                            "paddingAll": "20px",
                                            "paddingTop": "18px"
                                        },
                                        {
                                            "type": "box",
                                            "layout": "vertical",
                                            "contents": [
                                                {
                                                    "type": "text",
                                                    "text": '查看文章',
                                                    "color": "#ffffff",
                                                    "align": "center",
                                                    "size": "xs",
                                                    "offsetTop": "3px"
                                                }
                                            ],
                                            "position": "absolute",
                                            "cornerRadius": "20px",
                                            "offsetTop": "18px",
                                            "backgroundColor": "#ff334b",
                                            "offsetStart": "18px",
                                            "height": "25px",
                                            "width": "75px",
                                            "action": {
                                                "type": "uri",
                                                "label": "action",
                                                "uri": "https://www.instagram.com/p/"+personalFile[idx]['node']['shortcode']+"/"
                                                }
                                        }
                                    ],
                                "paddingAll": "0px"
                            }
                        })
                    else:
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
                                                "text": "下載單圖:"+account + '-' + str(idx)
                                            }
                                        },
                                        {
                                            "type": "box",
                                            "layout": "vertical",
                                            "contents": [
                                                {
                                                    "type": "text",
                                                    "text": '查看文章',
                                                    "color": "#ffffff",
                                                    "align": "center",
                                                    "size": "xs",
                                                    "offsetTop": "3px"
                                                }
                                            ],
                                            "position": "absolute",
                                            "cornerRadius": "20px",
                                            "offsetTop": "18px",
                                            "backgroundColor": "#ff334b",
                                            "offsetStart": "18px",
                                            "height": "25px",
                                            "width": "75px",
                                            "action": {
                                                "type": "uri",
                                                "label": "action",
                                                "uri": "https://www.instagram.com/p/"+personalFile[idx]['node']['shortcode']+"/"
                                                }
                                        }
                                    ],
                                "paddingAll": "0px"
                            }
                        })
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
