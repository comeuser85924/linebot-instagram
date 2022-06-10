from flask import Flask, request, abort, render_template
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
from listview import handleListview # listview.py 中的 handleListview fnction
from listview import media_multiple_images_carousel_list # listview.py 中的 media_multiple_images_carousel_list fnction
from module import mails

import configparser
import gspread
import json
import time
import os
import random
import requests
import unicodedata  # 幫助我們全形轉半行

app = Flask(__name__)

#heroku Config Vars
line_bot_api = LineBotApi(os.environ['channel_access_token'])
handler = WebhookHandler(os.environ['channel_secret'])
query_hash = os.environ['user_multiple_photos_query_hash']
headers = headers = eval(os.environ['headers']) 

host = 'https://www.instagram.com'
graphql_url = host + "/graphql/query/"
api_v1_host = 'https://i.instagram.com/api/v1'
profile_info_url = api_v1_host + "/users/web_profile_info/"

try:
    creds = gspread.service_account(filename = 'google-credentials.json')
    client = creds.open_by_url(
    'https://docs.google.com/spreadsheets/d/' + os.environ['GOOGLE_SHEET_ID'] + '/edit#gid=0')
    sheet = client.get_worksheet(0) 
except gspread.exceptions.APIError as e:
    print(e)
    mails('【Google sheet 異常】：請盡速到到 https://dashboard.heroku.com/apps/linebot-instagram 查看' + str(e))
    line_bot_api.reply_message(
        event.reply_token, TextSendMessage(text='系統異常！已自動通知工程師了，請耐心稍等'))

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError as errorMsg:
        mails('【Line callback 異常】：請盡速到到 https://dashboard.heroku.com/apps/linebot-instagram 查看')
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = event.message.text
    if (('###' in event.message.text) or (event.message.text == '天選之人')):
        msg = msg.encode('utf-8')
        msg = unicodedata.normalize('NFKC', event.message.text).replace(" ", "")
        next_page_token = ''
        if('###' in msg):
            account = msg.split(':')[1]
        elif(event.message.text == '天選之人'): 
            accountList = sheet.get_all_records() # 取得 sheet 帳號列表  
            time.sleep(0.5) # 等待 0.5 秒，防止用戶觸發太過頻繁執行導致觸發 google sheet rate limit
            randomIndex = random.randint(1, len(accountList) - 1)  # 將帳號列表順序打亂，並隨機產一個數值當作 天選之人 代號
            account = accountList[randomIndex]['account']
        queryString = { 'username' : account }
        profile_info_resp = requests.request("GET", profile_info_url, headers = headers, params = queryString)
         # 有搜尋到正確帳號
        if(profile_info_resp.status_code == 200):
            user_id = profile_info_resp.json()['data']['user']['id'] # user_id = 取得 user 的 id
            if profile_info_resp.json()['data']['user']['edge_owner_to_timeline_media']['page_info']['has_next_page'] == True:
                next_page_token = profile_info_resp.json()['data']['user']['edge_owner_to_timeline_media']['page_info']['end_cursor'] # next_page_token = 下個輪播的 token
            first = '10' # first = 顯示數量
            ## https://www.instagram.com/graphql/query/?query_hash={{query_hash}}&variables={"id":{{user_id}},"first":{{first}},"after":{{after}}}
            query_path = '?query_hash=' + query_hash + '&variables={"id":"'+ user_id +'","first":' + first + '}'
            graphql_resp = requests.request("GET", graphql_url+query_path, headers = headers)
            if(graphql_resp.status_code == 200):
                # 取的 user 前 10 筆的文章資訊
                user_profile_info = graphql_resp.json()['data']['user']
                if(user_profile_info['edge_owner_to_timeline_media']['edges'] != []):
                    to_line_carousel_media_list(1, user_profile_info, event, user_id, account, next_page_token)
                else:
                    line_bot_api.reply_message(
                        event.reply_token, TextSendMessage(text='此帳號為私人帳號或無任何貼文，請輸入正確且公開的 instagram 帳號'))
            else:
                print(str(graphql_resp))
                mails('【取得用戶前10筆異常(graphql_resp)】：請盡速到到 https://dashboard.heroku.com/apps/linebot-instagram 查看' + str(graphql_resp))
                line_bot_api.reply_message(
                    event.reply_token, TextSendMessage(text='系統異常！已自動通知工程師了，請耐心稍等'))
        else:
            line_bot_api.reply_message(
                event.reply_token, TextSendMessage(text='查無此帳號，請輸入正確且公開的 instagram 帳號'))
    elif(event.message.text == 'devtestmail!#999'):
        mails('【測試Email】：有收到信件')
    return 'OK2'

@handler.add(PostbackEvent)
def handle_postback(event):
    postback_msg = event.postback.data
    account = postback_msg.split('&')[1].split('=')[1]
    # 點擊輪播中大張圖片時
    if(postback_msg.split('&')[0].split('=')[1] == '0'):
        media_id = postback_msg.split('&')[2].split('=')[1]
        media_info_url = api_v1_host + '/media/' + media_id + '/info/'
        # 先取的單篇文章資訊
        media_info_resp = requests.request("GET", media_info_url, headers = headers)
        if(media_info_resp.status_code == 200):
            media_info_resp_item = media_info_resp.json()['items'][0]
            # 單圖 feed
            if(media_info_resp_item['product_type'] == 'feed'):
                img_url = media_info_resp_item['image_versions2']['candidates'][0]['url']
                line_bot_api.reply_message(event.reply_token, ImageSendMessage(
                    original_content_url = img_url,
                    preview_image_url = img_url
                ))
            # 多圖 carousel_container
            elif(media_info_resp_item['product_type'] == 'carousel_container'):
                # 我想一次看多張點
                if "index" in postback_msg:
                    index = int(postback_msg.split('&')[3].split('=')[1])
                    # 多圖的文章中會有圖片及影片兩種類型
                    # media_type = 1 圖片
                    if(media_info_resp_item['carousel_media'][index]['media_type'] == 1):
                        img_url = media_info_resp_item['carousel_media'][index]['image_versions2']['candidates'][0]['url']
                        line_bot_api.reply_message(event.reply_token, ImageSendMessage(
                            original_content_url = img_url,
                            preview_image_url = img_url
                        ))
                    # media_type = 1 影片
                    elif(media_info_resp_item['carousel_media'][index]['media_type'] == 2):
                        video_url = media_info_resp_item['carousel_media'][index]['video_versions'][0]['url']
                        img_url =  media_info_resp_item['carousel_media'][index]['image_versions2']['candidates'][0]['url']
                        line_bot_api.reply_message(event.reply_token, VideoSendMessage(
                            original_content_url = video_url,
                            preview_image_url = img_url
                        ))
                # 多圖中預設的大張單圖
                else:
                    img_url = media_info_resp_item['carousel_media'][0]['image_versions2']['candidates'][0]['url']
                    line_bot_api.reply_message(event.reply_token, ImageSendMessage(
                        original_content_url = img_url,
                        preview_image_url = img_url
                    ))
            # 影片clips、igtv
            elif(media_info_resp_item['product_type'] == 'clips' or media_info_resp_item['product_type'] == 'igtv'):
                video_url = media_info_resp_item['video_versions'][0]['url']
                img_url =  media_info_resp_item['image_versions2']['candidates'][0]['url']
                line_bot_api.reply_message(event.reply_token, VideoSendMessage(
                    original_content_url = video_url,
                    preview_image_url = img_url
                ))
            else:
                print(str(media_info_resp_item))
                mails('【文章異常(media_info_resp_item)】：請盡速到到 https://dashboard.heroku.com/apps/linebot-instagram 查看' + str(media_info_resp_item))
                line_bot_api.reply_message(
                    event.reply_token, TextSendMessage(text='系統異常！已自動通知工程師了，請耐心稍等'))
        else:
            print(str(media_info_resp))
            mails('【文章異常(media_info_resp)】：請盡速到到 https://dashboard.heroku.com/apps/linebot-instagram 查看' + str(media_info_resp))
            line_bot_api.reply_message(
                event.reply_token, TextSendMessage(text='系統異常！已自動通知工程師了，請耐心稍等'))
    # 點擊 我想一次看多張點 時
    elif(postback_msg.split('&')[0].split('=')[1] == '1'):
        media_id = postback_msg.split('&')[2].split('=')[1]
        media_info_url = api_v1_host + '/media/' + media_id + '/info/'
        # 取的單篇文章資訊(多圖)
        media_info_resp = requests.request("GET", media_info_url, headers = headers)
        if(media_info_resp.status_code == 200):
            media_info_resp_item = media_info_resp.json()['items'][0]
            to_line_carousel_media_list(2, media_info_resp_item, event,'','','')
    # 點擊 點我看下一輪 時
    elif(postback_msg.split('&')[0].split('=')[1] == '2'):
        user_id = postback_msg.split('&')[2].split('=')[1] # user_id = 取得 user 的 id
        next_page_token = postback_msg.split('&')[3].split(':')[1] # next_page_token = 下個輪播的 token
        first = '10' # first = 顯示數量
        # https://www.instagram.com/graphql/query/?query_hash={{query_hash}}&variables={"id":{{user_id}},"first":{{first}},"after":{{after}}}
        query_path = '?query_hash=' + query_hash + '&variables={"id":"'+ user_id +'","first":' + first + ',"after":"' + next_page_token +'"}'
        graphql_resp = requests.request("GET", graphql_url+query_path, headers = headers)
        if(graphql_resp.status_code == 200):
            user_profile_info = graphql_resp.json()['data']['user']  # 取的 user 文章資訊
            if user_profile_info['edge_owner_to_timeline_media']['page_info']['has_next_page'] == True:
                new_next_page_token = user_profile_info['edge_owner_to_timeline_media']['page_info']['end_cursor']
            to_line_carousel_media_list(1, user_profile_info, event, user_id, account, new_next_page_token)
    else:
        print(str(postback_msg))
        mails('【LineBot postback 異常】：請盡速到到 https://dashboard.heroku.com/apps/linebot-instagram 查看' )
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text='系統異常！已自動通知工程師了，請耐心稍等'))

def to_line_carousel_media_list(carousel_type, list_data, event, user_id, account, next_page_token):
    carousel_array = []
    # 天選之人 or 指定帳號 的預設 10 篇文章的情境
    if(carousel_type == 1):
        for index in range(len(list_data['edge_owner_to_timeline_media']['edges'])):
            carousel_array.append(
                handleListview(
                    list_data['edge_owner_to_timeline_media']['edges'], 
                    account, 
                    index,       
                    list_data['edge_owner_to_timeline_media']['edges'][index]['node']['shortcode'],  # 文章網址的 shortcode
                    user_id, # user 的 id
                    list_data['edge_owner_to_timeline_media']['edges'][index]['node']['id'], # 文章 media 的 id
                    next_page_token # 下一輪的 10 筆資料 token
                ))
    # 單篇文章(多圖) 我想一次看多張點 的情境
    elif(carousel_type == 2):
        for index in range(len(list_data['carousel_media'])):
            carousel_array.append(
                media_multiple_images_carousel_list(
                    list_data['carousel_media'], 
                    list_data['user']['username'], # user 的 帳號
                    index, 
                    list_data['code'],  # 文章網址的 shortcode
                    list_data['user']['pk'],  # user 的 id
                    list_data['pk'], # 文章 media 的 id
                    ''
                ))
    flex_message = FlexSendMessage(
        alt_text='潘多拉之盒已開啟',
        contents={
            "type": "carousel",
            "contents": carousel_array[0:10]
        }
    )
    line_bot_api.reply_message(event.reply_token, flex_message)

if __name__ == "__main__":
    app.run()