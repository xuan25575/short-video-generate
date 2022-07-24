import requests
import json


def get_info(url='https://api.uixsj.cn/hitokoto/get?type=hitokoto&code=json'):
    response = requests.get(url)
    # 获取请求状态码 200为正常
    if (response.status_code == 200):
        # 获取相应内容
        content = response.text
        # json转数组（Py叫字典，我喜欢叫数组）
        json_dict = json.loads(content)['content']
        print(json_dict)
        return json_dict
    else:
        print("请求失败!")
        return '悲伤中产生的是温柔，愤怒中产生的是力量，但是憎恨中产生的东西，通常都是愚昧。'


def transfor(text, url='http://fanyi.youdao.com/translate?&doctype=json&type=AUTO&i='):
    response = requests.get(url + str(text))
    # 获取请求状态码 200为正常
    if (response.status_code == 200):
        # 获取相应内容
        content = response.text
        print(content)
        # json转数组
        json_dict = json.loads(content)['translateResult']
        print(json_dict[0][0]['tgt'])
        return json_dict[0][0]['tgt']
    else:
        print("请求失败!")
        return '悲伤中产生的是温柔，愤怒中产生的是力量，但是憎恨中产生的东西，通常都是愚昧。'


def get_poetry(url='https://v1.jinrishici.com/all.json'):
    response = requests.get(url)
    # 获取请求状态码 200为正常
    if response.status_code == 200:
        # 获取相应内容
        content = response.text
        # json转数组
        json_dict = json.loads(content)
        print(json_dict['origin'] + ",--" + json_dict['author'] + "," + json_dict['content'])
        return json_dict['content'] + "," + ",--" + json_dict['author'] + ",--" + json_dict['origin'].replace("·", "")
    else:
        print("请求失败!")
        return '悲伤中产生的是温柔，愤怒中产生的是力量，但是憎恨中产生的东西，通常都是愚昧。'


if __name__ == '__main__':
    transfor('悲伤中产生的是温柔，愤怒中产生的是力量，但是憎恨中产生的东西，通常都是愚昧。')

# if __name__ == '__main__':
#     get_info("https://api.uixsj.cn/hitokoto/get?type=hitokoto&code=json")

#if __name__ == '__main__':
#     get_poetry()
