import os
import requests
import json
import random
from module import mails

#heroku Config Vars
query_hash = os.environ['user_multiple_photos_query_hash']
headers = headers = eval(os.environ['headers']) 

host = 'https://www.instagram.com'
graphql_url = host + "/graphql/query/"
api_v1_host = 'https://i.instagram.com/api/v1'
profile_info_url = api_v1_host + "/users/web_profile_info/"

queryString = { 'username' : 'brunomars' }
profile_info_resp = requests.request("GET", profile_info_url, headers = headers, params = queryString)
if (profile_info_resp.status_code == 200):
    print("profile_info API response success")
    user_id = profile_info_resp.json()['data']['user']['id'] # user_id = 取得 user 的 id
    first = '10' # first = 顯示數量
    query_path = '?query_hash=' + query_hash + '&variables={"id":"'+ user_id +'","first":' + first + '}'
    graphql_resp = requests.request("GET", graphql_url+query_path, headers = headers)
    if(graphql_resp.status_code == 200):
        print("graphql API response success")
        media_id = graphql_resp.json()['data']['user']['edge_owner_to_timeline_media']['edges'][0]['node']['id']
        media_info_url = api_v1_host + '/media/' + media_id + '/info/'
        media_info_resp = requests.request("GET", media_info_url, headers = headers)
        if(media_info_resp.status_code == 200):
            print("media API response success")
        else:
            print("Error message:" + media_info_resp.json())
            mails('【每日 API 檢查】：' + str(media_info_resp))
    else:
        print("Error message:" + graphql_resp.json())
        mails('【每日 API 檢查】：' + str(graphql_resp))
else:
    print("Error message:" + profile_info_resp.json())
    mails('【每日 API 檢查】：' + str(profile_info_resp))
