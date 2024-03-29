from countSum import handleCount
import requests
import json
def handleListview(userBody, account, idx, shortcode, user_id, media_id, next_page_token):
    flex_message = {}
    # 單張
    # media_type = 0 單圖
    # media_type = 1 多圖
    # media_type = 2 下一輪
    if((userBody[idx]['node']['__typename'] == 'GraphImage' or userBody[idx]['node']['__typename'] == 'GraphVideo') and idx != 9):
        flex_message = {
            "type": "bubble",
            "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "image",
                            "url": userBody[idx]['node']['display_url'],
                            "size": "full",
                            "aspectMode": "cover",
                            "aspectRatio": "2:3",
                            "gravity": "top",
                            "action": {
                                "type": "postback",
                                "label": "action",
                                # "data": "單圖 "+ account + ' ' + shortcode + ' ' + nextpage,
                                "data": "media_type=0&account=" + account + '&media_id=' + media_id,
                                "displayText": account
                            }
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "查看文章",
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
                                "uri": "https://www.instagram.com/p/"+shortcode+"/"
                                }
                        }
                    ],
                "paddingAll": "0px"
            }
        }
    elif((userBody[idx]['node']['__typename'] == 'GraphImage' or userBody[idx]['node']['__typename'] == 'GraphVideo') and idx == 9):
        flex_message = {
            "type": "bubble",
            "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "image",
                            "url": userBody[idx]['node']['display_url'],
                            "size": "full",
                            "aspectMode": "cover",
                            "aspectRatio": "2:3",
                            "gravity": "top",
                            "action": {
                                "type": "postback",
                                "label": "action",
                                "data":  "media_type=0&account=" + account + '&media_id=' + media_id,
                                "displayText": account
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
                                        "text": "點我看第下一輪",
                                        "color": "#E1306C",
                                        "flex": 0,
                                        "offsetTop": "-2px",
                                        "size": "lg",
                                        "weight": "bold",
                                        "action": {
                                            "type": "postback",
                                            "label": "action",
                                            "data":"media_type=2&account=" + account + "&user_id="+ user_id +"&next_page_token:" + next_page_token,
                                            "displayText":"看下一輪囉！"
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
                                    "cornerRadius": "4px",
                                    "spacing": "sm",
                                    "margin": "xxl",
                                    "height": "40px",
                                    "borderWidth": "1px",
                                    "borderColor": "#E1306C"
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
                                "uri": "https://www.instagram.com/p/"+shortcode+"/"
                                }
                        }
                    ],
                "paddingAll": "0px"
            }
        }
    elif(userBody[idx]['node']['__typename'] == 'GraphSidecar' and idx == 9):
        flex_message = {
            "type": "bubble",
            "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "image",
                            "url":  userBody[idx]['node']['display_url'],
                            "size": "full",
                            "aspectMode": "cover",
                            "aspectRatio": "2:3",
                            "gravity": "top",
                            "action": {
                                "type": "postback",
                                "label": "action",
                                "data": "media_type=0&account=" + account + '&media_id=' + media_id,
                                "displayText": account
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
                                        "text": "我想一次看多張點",
                                        "color": "#ffffff",
                                        "flex": 0,
                                        "offsetTop": "-2px",
                                        "weight": "bold",
                                        "action": {
                                            "type": "postback",
                                            "label": "action",
                                            "data": "media_type=1&account=" + account + '&media_id=' + media_id + '&index=' + str(idx),
                                            "displayText":account
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
                            },
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
                                        "text": "點我看第下一輪",
                                        "color": "#E1306C",
                                        "flex": 0,
                                        "offsetTop": "-2px",
                                        "size": "lg",
                                        "weight": "bold",
                                        "action": {
                                            "type": "postback",
                                            "label": "action",
                                            "data":"media_type=2&account=" + account + "&user_id="+ user_id +"&next_page_token:" + next_page_token,
                                            "displayText":"看下一輪囉！"
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
                                    "cornerRadius": "4px",
                                    "spacing": "sm",
                                    "margin": "xxl",
                                    "height": "40px",
                                    "borderWidth": "1px",
                                    "borderColor": "#E1306C"
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
                                "uri": "https://www.instagram.com/p/"+shortcode+"/"
                                }
                        }
                    ],
                "paddingAll": "0px"
            }
        }
    # 多張
    else:
        flex_message = {
            "type": "bubble",
            "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "image",
                            "url":   userBody[idx]['node']['display_url'],
                            "size": "full",
                            "aspectMode": "cover",
                            "aspectRatio": "2:3",
                            "gravity": "top",
                            "action": {
                                "type": "postback",
                                "label": "action",
                                "data": "media_type=0&account=" + account + '&media_id=' + media_id,
                                "displayText":account
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
                                        "text": "我想一次看多張點",
                                        "color": "#ffffff",
                                        "flex": 0,
                                        "offsetTop": "-2px",
                                        "weight": "bold",
                                        "action": {
                                            "type": "postback",
                                            "label": "action",
                                            "data": "media_type=1&account=" + account + '&media_id=' + media_id + '&index=' + str(idx),
                                            "displayText":account
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
                                "uri": "https://www.instagram.com/p/"+shortcode+"/"
                                }
                        }
                    ],
                "paddingAll": "0px"
            }
        }
    return flex_message
    
# 當點 我想一次看多張點
def media_multiple_images_carousel_list(userBody, account, idx, shortcode, user_id, media_id, nextpage):
    flex_message = {
            "type": "bubble",
            "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "image",
                            "url": userBody[idx]['image_versions2']['candidates'][0]['url'],
                            "size": "full",
                            "aspectMode": "cover",
                            "aspectRatio": "2:3",
                            "gravity": "top",
                            "action": {
                                "type": "postback",
                                "label": "action",
                                "data": "media_type=0&account=" + account + '&media_id=' + media_id + '&index=' + str(idx),
                                "displayText": account
                            }
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "查看文章",
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
                                "uri": "https://www.instagram.com/p/"+shortcode+"/"
                                }
                        }
                    ],
                "paddingAll": "0px"
            }
        }
    return flex_message