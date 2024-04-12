import flask
from gevent import pywsgi
import json
import os
from check import check, file_path
from getInfo import get_token, send_message, get_user_info, send_admin, get_all_messages

app = flask.Flask(__name__)
app.debug = False

msg_id_list = []

with open(f'{file_path}/info.json', 'r') as f:
    info = json.load(f)
app_id = info['app_id']
app_secret = info['app_secret']
admin_id = info['admin_id']
token = get_token(app_id, app_secret)

@app.route('/')
def index():
    return 'Hello, XLab!'

@app.route('/message', methods=['POST'])
def get_message():
    token = get_token(app_id, app_secret)
    data = flask.request.get_json()
    if data['header']['event_type'] != 'im.message.receive_v1':
        return 'OK', 200
    chat_id = data['event']['message']['chat_id']
    msg_id_list = get_all_messages(token, chat_id)
    score_dict = {}
    message = json.loads(data['event']['message']['content'])['text']
    response_message = ''
    msg_id = data['event']['message']['message_id']
    # 通过msg_id判断是否为重复消息
    if msg_id in msg_id_list[:-1]:
        print('重复消息')
        return 'OK', 200
    msg_id_list.append(msg_id)
    sender = data['event']['sender']['sender_id']['open_id']
    sender_name = json.loads(get_user_info(token, sender).text)['data']['user']['name']
    response_message += f'姓名：{sender_name}\n'
    response_message += f'发送内容：{message}\n'
    if 'github.com/' in message:
        user = message.split('github.com/')[1].split('/')[0]
        repo = message.split('github.com/')[1].split('/')[1]
        print(user, repo)
        os.chdir(f'{file_path}/..')
        if os.path.exists(f'./{repo}'):
            os.system(f'rm -rf {repo}')
        os.system(f'git clone git@github.com:{user}/{repo}.git')
        if os.path.exists(f'{repo}'):
            if os.path.exists(f'{repo}/CMakeLists.txt'):
                if os.path.exists(f'./{repo}/build'):
                    os.system(f'rm -rf {file_path}/../{repo}/build') 
                if os.path.exists(f'./{repo}/bin'):
                    os.system(f'rm -rf {file_path}/../{repo}/bin') 
                os.system(f'mkdir {file_path}/../{repo}/build')
                os.system(f'mkdir {file_path}/../{repo}/bin')
                os.chdir(f'{repo}/build')
                os.system('cmake .. && make')
                os.chdir(f'{file_path}/..')
                if os.path.exists(f'{repo}/bin'):
                    if os.listdir(f'{repo}/bin') != []:
                        exec_file = os.listdir(f'{repo}/bin')[0]
                        score_dict = check(repo, exec_file)
                        # 检测是否有错误
                        if 'error' in score_dict.keys():
                            response_message += f'消息：发生报错\n {score_dict["error"]}\n'
                            score_dict['compile_success'] = 0
                        else:
                            response_message += '消息：运行成功\n'
                        score_dict['compile_success'] = 25
                    else:
                        response_message += '消息：没找到可执行文件，请检查工程格式是否正确。\n'
                        score_dict['compile_success'] = 0
                else:
                    response_message += '消息：没找到bin文件夹，请检查工程格式是否正确。\n'
                    score_dict['compile_success'] = 0
            else:
                response_message += '消息：没找到CMakeLists.txt，请检查工程格式是否正确。\n'
                score_dict['compile_success'] = 0
            os.system(f'rm -rf {file_path}/../{repo}')
        else:
            response_message += '消息：没找到仓库，请检查仓库地址是否正确。\n'
            score_dict['compile_success'] = 0
    else:
        response_message += '消息：请发送github仓库地址。\n'
        score_dict['compile_success'] = 0
    for key, value in score_dict.items():
        response_message += f'{key}: {value}\n'
    response_message += f'总分：{sum([item for item in score_dict.values() if isinstance(item, int)])}\n'
    send_message(token, sender, response_message)
    # 发送给管理员
    send_admin(token, admin_id, response_message)
    return 'OK', 200

if __name__ == '__main__':
    server = pywsgi.WSGIServer(('0.0.0.0', 9051), app)
    server.serve_forever()