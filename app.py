from flask import Flask, request, abort, render_template
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
from countSum import handleCount # 引入countSum.py 中的 handleCount fnction
from listview import handleListview # listview.py 中的 handleListview fnction

import configparser
import json
import os
import random
import requests
import unicodedata  # 幫助我們全形轉半行

app = Flask(__name__)

#heroku
line_bot_api = LineBotApi(os.environ['channel_access_token'])
handler = WebhookHandler(os.environ['channel_secret'])
query_id = os.environ['query_id']
track_query_hash = os.environ['track_query_hash']
user_multiple_photos_query_hash = os.environ['user_multiple_photos_query_hash']
headers = {'cookie': os.environ['myself_cookies']}

instagramUrl = 'https://www.instagram.com/'
queryString = {"__a": "1"}
graphqlUrl = instagramUrl + "graphql/query/"

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

@handler.add(PostbackEvent)
def handle_postback(event):
    userID = ''
    account = ''
    nextpage = ''
    index = ''
    userQueryString = {}
    if(event.postback.data.split(' ')[0] == '單圖'):
        account = event.postback.data.split(' ')[1]
        shortcode = event.postback.data.split(' ')[2]
        pageToken = event.postback.data.split(' ')[3] 
        sort = ''
        if(len(event.postback.data.split(' ')) > 4):
            sort = int(event.postback.data.split(' ')[4])
        url = graphqlUrl+'?query_hash='+user_multiple_photos_query_hash+'&variables={%22shortcode%22:%22'+shortcode+'%22}'                      
        userBody = requests.request("GET", url, headers=headers)
        if(userBody.status_code == 200):
            personalFile = userBody.json()['data']['shortcode_media']
            if(sort == ''):
                if(personalFile['__typename'] == 'GraphImage'):
                    line_bot_api.reply_message(event.reply_token, ImageSendMessage(
                        original_content_url=personalFile['display_url'], preview_image_url=personalFile['display_url']))
                elif(personalFile['__typename'] == 'GraphSidecar'):
                    line_bot_api.reply_message(event.reply_token, ImageSendMessage(
                        original_content_url=personalFile['display_url'], preview_image_url=personalFile['display_url']))
                elif(personalFile['__typename'] == 'GraphVideo'):
                    line_bot_api.reply_message(event.reply_token, VideoSendMessage(
                    original_content_url=personalFile['video_url'], preview_image_url=personalFile['display_url']))
                else:
                    line_bot_api.reply_message(
                    event.reply_token, TextSendMessage(text='特殊狀況-1！小幫手也不知道發生甚麼事了！！！'))
            else:
                if(personalFile['edge_sidecar_to_children']['edges'][sort]['node']['__typename'] == 'GraphImage'):
                    line_bot_api.reply_message(event.reply_token, ImageSendMessage(
                        original_content_url=personalFile['edge_sidecar_to_children']['edges'][sort]['node']['display_url'], preview_image_url=personalFile['edge_sidecar_to_children']['edges'][sort]['node']['display_url']))
                elif(personalFile['edge_sidecar_to_children']['edges'][sort]['node']['__typename'] == 'GraphVideo'):
                    line_bot_api.reply_message(event.reply_token, VideoSendMessage(
                    original_content_url=personalFile['edge_sidecar_to_children']['edges'][sort]['node']['video_url'], preview_image_url=personalFile['edge_sidecar_to_children']['edges'][sort]['node']['display_url']))
                else:
                    line_bot_api.reply_message(
                    event.reply_token, TextSendMessage(text='特殊狀況-2！小幫手也不知道發生甚麼事了！！！'))
        elif(userBody.status_code == 429):
            line_bot_api.reply_message(
                event.reply_token, TextSendMessage(text='小幫手罷工啦！！工程師趕緊修啊~~~~~'))
        else:
            line_bot_api.reply_message(
                event.reply_token, TextSendMessage(text='您好，您提供的帳號查無資料，請確認帳號是否輸入正確'))

    elif(event.postback.data.split(' ')[0] == '多圖'):
        account = event.postback.data.split(' ')[1]
        shortcode = event.postback.data.split(' ')[2]
        nextpage = event.postback.data.split(' ')[3]
        url = graphqlUrl+'?query_hash='+user_multiple_photos_query_hash+'&variables={%22shortcode%22:%22'+shortcode+'%22}'                      
        userBody = requests.request("GET", url, headers=headers) 
        if(userBody.status_code == 200):
            personalFile = userBody.json()['data']['shortcode_media']
            edge_sidecar_to_children = personalFile['edge_sidecar_to_children']['edges']
            array = []
            for idx in range(len(edge_sidecar_to_children)):
                array.append({
                    "type": "bubble",
                    "body": {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "image",
                                    "url": edge_sidecar_to_children[idx]['node']['display_url'],
                                    "size": "full",
                                    "aspectMode": "cover",
                                    "aspectRatio": "2:3",
                                    "gravity": "top",
                                    "action": {
                                        "type": "postback",
                                        "label": "action",
                                        "data": "單圖 "+account + ' ' + shortcode + ' ' +nextpage + ' ' + str(idx),
                                        "displayText":"IG:"+account
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

    elif(event.postback.data.split(' ')[0] == '下一輪'):
        userID = event.postback.data.split(' ')[1]
        account = event.postback.data.split(' ')[2]
        pageToken = event.postback.data.split(' ')[3]
        userQueryString = {"query_id":query_id, 'id':userID ,'first':10,'after':pageToken}
        userBody = requests.request("GET", graphqlUrl, headers=headers, params=userQueryString)
        if(userBody.status_code == 200):
            userData = userBody.json()['data']['user']['edge_owner_to_timeline_media']['edges']
            if(userBody.json()['data']['user']['edge_owner_to_timeline_media']['page_info']['has_next_page'] == True):
                nextpage_next = userBody.json()['data']['user']['edge_owner_to_timeline_media']['page_info']['end_cursor']
            if len(userData) == 0:
                line_bot_api.reply_message(
                    event.reply_token, TextSendMessage(text='非常抱歉～由於Instagram安全隱私問題，此人非公開帳號，所以小幫手也無法取得相關資訊QQ..'))
            else:
                flexMsg = []
                for idx in range(len(userData)):
                    flexMsg.append(
                        handleListview(
                            userData, 
                            account, 
                            idx, 
                            graphqlUrl,
                            headers,
                            userData[idx]['node']['shortcode'],
                            user_multiple_photos_query_hash,
                            userID,
                            nextpage_next
                        ))
                flex_message = FlexSendMessage(
                    alt_text='潘多拉之盒已開啟',
                    contents={
                        "type": "carousel",
                        "contents": flexMsg[0:10]
                    }
                )
                line_bot_api.reply_message(event.reply_token, flex_message)
    else:
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text='小幫手不知道該如何反應了...'))

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = event.message.text
    msg = msg.encode('utf-8')

    if (('###' in event.message.text) or (event.message.text == '天選之人')):
        msg = unicodedata.normalize('NFKC', event.message.text).replace(" ", "")
        mores = 0
        account = ''
        url=''
        if('###' in msg):
            account = msg.split(':')[1]
        elif(event.message.text == '天選之人'):
            trackUrl='https://www.instagram.com/graphql/query/?query_hash='+os.environ['track_query_hash'] + '&variables=%7B%22id%22%3A%22' + os.environ['track_id'] + '%22%2C%22first%22%3A' + '50' +'%7D'
            print(trackUrl)
            trackBody = requests.request("GET", trackUrl ,headers=headers)
            print(trackBody.status_code)
            if(trackBody.status_code == 200): 
                print(trackBody.json()['data']['user']['edge_follow'])
                lotteryList = trackBody.json()['data']['user']['edge_follow']['edges']
                endSum = random.randint(1,len(lotteryList)-1) 
                account = lotteryList[endSum]['node']['username']

        response = requests.request("GET", instagramUrl + account + '/', headers=headers, params=queryString)
        if(response.status_code == 200):
            user = response.json()['graphql']['user']
            userQueryString = {"query_id":query_id, 'id':user['id'] ,'first':'10'}
            userBody = requests.request("GET", graphqlUrl, headers=headers, params=userQueryString)
            if(userBody.status_code == 200):
                userData = userBody.json()['data']['user']['edge_owner_to_timeline_media']['edges']
                pageToken = ''
                if(userBody.json()['data']['user']['edge_owner_to_timeline_media']['page_info']['has_next_page'] == True):
                    pageToken = userBody.json()['data']['user']['edge_owner_to_timeline_media']['page_info']['end_cursor']
                if len(userData) == 0:
                    line_bot_api.reply_message(
                        event.reply_token, TextSendMessage(text='非常抱歉～由於Instagram安全隱私問題，此人非公開帳號，所以小幫手也無法取得相關資訊QQ..'))
                else:
                    flexMsg = []
                    for idx in range(len(userData)):
                        flexMsg.append(
                            handleListview(
                                userData, 
                                account, 
                                idx, 
                                graphqlUrl,
                                headers,
                                userData[idx]['node']['shortcode'],
                                user_multiple_photos_query_hash,
                                user['id'],
                                pageToken
                            ))
                    flex_message = FlexSendMessage(
                        alt_text='潘多拉之盒已開啟',
                        contents={
                            "type": "carousel",
                            "contents": flexMsg[0:10]
                        }
                    )
                    line_bot_api.reply_message(event.reply_token, flex_message)
        elif(response.status_code == 429):
            line_bot_api.reply_message(
                event.reply_token, TextSendMessage(text='小幫手罷工啦！！工程師趕緊修啊~~~~~'))
        else:
            line_bot_api.reply_message(
                event.reply_token, TextSendMessage(text='您好，您提供的帳號查無資料，請確認帳號是否輸入正確'))

    return 'OK2'

if __name__ == "__main__":
    app.run()
