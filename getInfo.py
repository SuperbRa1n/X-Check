import requests
import json

def get_token(app_id: str, app_secret: str) -> str:
    url = 'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal'
    headers = {
        'Content-Type': 'application/json; charset=utf-8'
    }
    data = {
        'app_id': app_id,
        'app_secret': app_secret
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    return response.json()['tenant_access_token']

def send_message(token: str, open_id: str, message: str) -> requests.models.Response:
    url = f'https://open.feishu.cn/open-apis/im/v1/messages'
    headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'Authorization': 'Bearer ' + token
    }
    data = {
        'receive_id': open_id,
        'msg_type': 'text',
        'content': json.dumps({
            'text': message
        })
    }
    params = {
        'receive_id_type': 'open_id'
    }
    response = requests.post(url, params=params, headers=headers, data=json.dumps(data))
    return response

def get_user_info(token: str, open_id: str) -> requests.models.Response:
    url = f'https://open.feishu.cn/open-apis/contact/v3/users/{open_id}'
    headers = {
        'Authorization': 'Bearer ' + token
    }
    response = requests.get(url, headers=headers)
    return response

def send_admin(token: str, admin_id: str, message: str) -> requests.models.Response:
    url = f'https://open.feishu.cn/open-apis/im/v1/messages'
    headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'Authorization': 'Bearer ' + token
    }
    data = {
        'receive_id': admin_id,
        'msg_type': 'text',
        'content': json.dumps({
            'text': message
        })
    }
    params = {
        'receive_id_type': 'chat_id'
    }
    response = requests.post(url, params=params, headers=headers, data=json.dumps(data))
    return response

def get_all_messages(token: str, chat_id: str) -> list:
    url = 'https://open.feishu.cn/open-apis/im/v1/messages'
    headers = {
        'Authorization': 'Bearer ' + token
    }
    params = {
        'container_id_type': 'chat',
        'container_id': chat_id,
    }
    page_token = ''
    messages = []
    while True:
        params['page_token'] = page_token
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        for i in data['data']['items']:
            messages.append(i['message_id'])
        if data['data']['has_more']:
            page_token = data['data']['page_token']
        else:
            break
    return messages

if __name__ == '__main__':
    with open('info.json', 'r') as f:
        info = json.load(f)
    app_id = info['app_id']
    app_secret = info['app_secret']
    admin_id = info['admin_id']
    token = get_token(app_id, app_secret)
    # message = 'Hello, XLab!'
    # print(send_message(token, admin_id, message).text)
    chat_id = 'oc_889307cd24676b019c46af0cf4fe8ae2'
    print(get_all_messages(token, chat_id))
