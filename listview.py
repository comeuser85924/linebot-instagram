from countSum import handleCount
def handleListview(personalFile,account,idx):
    if(handleCount(personalFile[idx]['node']) != 1):
        return {
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
        }
    else:
        return {
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
        }