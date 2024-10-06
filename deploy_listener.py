from flask import Flask, request, jsonify
import requests
import paramiko
import os

app = Flask(__name__)

def load_webhook(filename):
    with open(filename, 'r') as file:
        for line in file:
            return line

WEBHOOK_URL = load_webhook("webhook.txt")

# machinesディレクトリ内のホスト情報を読み込む関数
def load_machine_config(filename):
    config = {}
    with open(filename, 'r') as file:
        lines = file.readlines()
        for line in lines:
            if '=' in line:
                key, value = line.strip().split('=', 1)
                config[key] = value
            else:
                config.setdefault('commands', []).append(line.strip())
    return config

# Discordメッセージの送信
def send_to_discord(title, description, color=0xFFA500):  # オレンジ色
    payload = {
        "embeds": [
            {
                "title": title,
                "description": description,
                "color": color
            }
        ]
    }
    response = requests.post(WEBHOOK_URL, json=payload)
    if response.status_code != 204:
        print(f"Failed to send message to Discord: {response.status_code}, {response.text}")

# SSHでコマンドを実行する関数
def execute_ssh_command(host, username, password, commands):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=host, username=username, password=password)
    try:
        log_lines = [f"{host}を{username}でデプロイ実行\n\n----------------------------\n"]
        for command in commands:
            stdin, stdout, stderr = ssh.exec_command(command)
            print(f"Executed: {command}")
            out = stdout.read().decode()
            err = stderr.read().decode()

            log = f"**Command:**\n{command}\n\n**Output:**\n{out}\n\n**Errors:**\n{err}\n\n----------------------------\n"
            log_lines.append(log)
    finally:
        send_to_discord("デプロイ実行", ''.join(log_lines))
        ssh.close()

@app.route('/deploy', methods=['POST'])
def deploy():
    # POSTリクエストからパスワードを取得
    request_password = request.get_json().get('password')
    print("Deploy request key --> " + str(request_password))
    
    # machinesディレクトリ内の各ホストファイルをチェック
    machines_dir = './machines'
    print(os.listdir(machines_dir))
    for filename in os.listdir(machines_dir):
        if filename.endswith('.txt'):
            config = load_machine_config(os.path.join(machines_dir, filename))
            
            # リクエストパスワードが一致するか確認
            if config.get('request_password') == config['request_password']:
                ssh_host = config.get('ssh_host')
                ssh_user = config.get('ssh_user')
                ssh_password = config.get('ssh_password')
                commands = config.get('commands', [])

                if ssh_host and ssh_user and ssh_password:
                    # SSH接続してコマンドを実行
                    execute_ssh_command(ssh_host, ssh_user, ssh_password, commands)
                    return jsonify({'status': 'success', 'message': f'Commands executed on {ssh_host}'})
                else:
                    return jsonify({'status': 'error', 'message': 'Invalid SSH configuration'})
    
    return jsonify({'status': 'error', 'message': 'Password does not match any machine'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
