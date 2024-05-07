import json
import random
import time

import numpy as np
import requests

# 表單URL
form_url = "https://docs.google.com/forms/d/e/1FAIpQLSdJw3iS47uo-RhBo9hZXHcFbJ6AUSWhLu0BhIk50hP84drHmw/formResponse"


# 表單第一頁的回答
a = ["男","女"]
b = ["16-18歲","18-25歲"]
c = ["高中", "大學本科","研究生及以上"]
d=["在校學生","企業工作者","個體經營者","自由職業者","流浪者","全職子女"]
e =["2000元以下","2000-4000元","4000-6000元","6000-8000元","8000-10000元","10000元以上"]
f=["便宜","貴","適中"]
g =["節假日或者特殊的日子，作為禮物給自己","送給朋友作為禮物","jellycat出了新品就買","有活動折扣時","沒有特定時期，随意購買","完全不買"]
h = ["線下店鋪","微博","微信/QQ","IG","抖音","小紅書","好友推薦"]
ia = ["7","8","9","10"]
j = ["Mpay等支付apps","街邊的廣告牌","巴士上的電視","巴士外觀","社交媒體"]
k = ["6","7","8","9","10"]

period = np.arange(0.5, 5.0, 0.1)
delay = 0  # delay of execution
# 填寫50份表單
for i in range(50):
    # 第一頁回答
    page1_data = {
        "entry.1350030702": random.choice(a),
        "entry.900160485": random.choice(c),
        "entry.1422879354": random.choice(b),
        "entry.280306757": random.choice(e),
        "entry.2122947685": random.choice(d),
        "entry.1815756121": random.choice(f),
        "entry.1872631711":random.choice(g),#random.sample(g, random.randint(1, len(g))),
        "entry.317247863": random.choice(h),#random.sample(h, random.randint(1, len(h))),
        #"entry.317247863": random.sample(h, random.randint(1, len(h))),

        "dlut": "1714062990648",
        'fvv': '1',
        'draftResponse': '[]',
        'pageHistory': '0',
        'fbzx': '-3654520240353581290'
    }
    # 轉換為 partialResponse 格式
    partialResponse = [
        [
            [None, 1350030702, [page1_data["entry.1350030702"]], 0],
            [None, 1422879354, [page1_data["entry.1422879354"]], 0],
            [None, 900160485, [page1_data["entry.900160485"]], 0],
            [None, 2122947685, [page1_data["entry.2122947685"]], 0],
            [None, 280306757, [page1_data["entry.280306757"]], 0],
            [None, 1815756121, [page1_data["entry.1815756121"]], 0],
            [None, 1872631711, [page1_data["entry.1872631711"]], 0],
            [None, 317247863, [page1_data["entry.317247863"]], 0]
        ],
        None,
        "445041842044259497"
    ]

    #json_partialResponse = json.dumps({"partialResponse": partialResponse})
    # 第二頁回答
    page2_data = {

        "entry.1350030702": random.choice(a),
        "entry.900160485": random.choice(c),
        "entry.1422879354": random.choice(b),
        "entry.280306757": random.choice(e),
        "entry.2122947685": random.choice(d),
        "entry.1815756121": random.choice(f),
        "entry.1872631711": random.choice(g),  # random.sample(g, random.randint(1, len(g))),
        "entry.317247863": random.choice(h),

        "entry.1640980101": random.choice(j),#random.sample(j, random.randint(1, len(j))),
        "entry.937103656": random.choice(ia),
        "entry.2058500634": random.choice(k),
        'hud':'true',
        'fvv': '1',
        'pageHistory': '0,1',
        #'dlut': '1714065009120',
        #'fbzx':'4450418420442594978',
        "partialResponse":  partialResponse
    }



    try:
        # 發送POST請求
        response = requests.post(form_url, data=page2_data)
        # 檢查回應狀態碼
        if response.status_code == 200:
            print(page2_data)
            print(f"第 {i + 1} 份表單填寫成功")
        else:
            print(f"第 {i + 1} 份表單填寫失敗")
        response.raise_for_status()
        if response.status_code == 200:
            delay = round(random.choice(period), 2)  # round off to the 2nd decimal place

            time.sleep(delay)
    except requests.HTTPError:
        print('HTTP Error!')
