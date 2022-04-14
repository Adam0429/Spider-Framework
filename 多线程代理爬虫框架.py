import time
import requests
import threading
import pandas as pd
from threading import Lock
from retrying import retry


@retry(stop_max_attempt_number=10)
def get_proxy():
    response = requests.get('http://api.hailiangip.com:8422/api/getIp?type=1&num=1&pid=-1&unbindTime=600&cid=-1&orderId=O21082311160736327125&time=1649430888&sign=2b225a028f191ab4cde34fccc0fa98c4&noDuplicate=0&dataType=0&lineSeparator=0&singleIp=')
    proxies = {
        'http': response.json()['data'][0]['ip']+':'+str(response.json()['data'][0]['port']),
        'https': response.json()['data'][0]['ip']+':'+str(response.json()['data'][0]['port'])
    }
    return proxies

@retry(stop_max_attempt_number=15)
def request_get_with_proxy(url,**argv):
    global my_proxy
    success = False
    while success == False:
        try:
            response = requests.get(url, proxies=my_proxy,**argv)
            success = True
        except:
            my_proxy = get_proxy()
    return response

@retry(stop_max_attempt_number=15)
def request_post_with_proxy(url,**argv):
    global my_proxy
    success = False
    while success == False:
        try:
            response = requests.post(url, proxies=my_proxy,**argv)
            success = True
        except:
            my_proxy = get_proxy()
    return response

def get_usehash(i):
    cookies = {
        'UM_distinctid': '18025c27fed133-07290167d7e959-35736a03-384000-18025c27feee3f',
        'CNZZDATA1279853600': '711148386-1649892416-%7C1649892416',
        'cna': 'd8bb02ad473d4f55a6463d957ff3e836',
    }

    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
        'Referer': 'https://h5.ubanquan.cn/auction/detail/AP788802761415571649748880',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Mobile Safari/537.36',
        'requestChannel': 'UBQ_H5',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'token': '',
    }

    response = request_get_with_proxy(f'https://h5.ubanquan.cn/api/opactivity/discoverView/getAuctionDetailApp/{i}', headers=headers, cookies=cookies)
    userhash = response.json()['data']['auctionInfo']['userHash']
    global lock
    with lock:
        global result
        result.append(userhash)
    return userhash

def length_of_result():
	while 1:
		global result
		print(len(result))
		time.sleep(1)
# t = threading.Thread(target=length_of_result)
# t.start()

if __name___ == '__main__':
	csv = pd.read_csv('data.csv')
	print(csv.author.value_counts())
	auctionNos = list(csv[csv['author'] == '十三楼'].auctionNo)

	global result
	global lock

	result = []
	lock = Lock()

	t_list = []
	for i in auctionNos:
	    t = threading.Thread(target=get_usehash,args=(i,))
	    t.start()
	    t_list.append(t)


	for t in t_list:
	    t.join()
