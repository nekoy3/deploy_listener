from flask import Flask, request, jsonify
import requests
import paramiko
import csv
import os
import ast

def load_webhook(filename):
    with open(filename, 'r') as file:
        for line in file:
            return line.rstrip()

def load_keypath(filename):
    with open(filename, 'r') as file:
        for line in file:
            return line.rstrip()

app = Flask(__name__)
WEBHOOK_URL = load_webhook("webhook.txt")
KEYPATH = load_keypath("keypath.txt")
CSVPATH = "machines.csv"

def check_csv(filename):
    if not os.path.exists(filename):
        # ファイルが存在しない場合はヘッダを追加して生成
        with open(filename, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(headers)
            print(f"{filename} ファイルが作成され、ヘッダが追加されました。\nマシンを追加してください。\n")

def load_csv(filename):
    #csvファイルを読み取る
    data = []
    with open(filename, mode="r", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            # scripts列の文字列をリストに変換
            row["scripts"] = ast.literal_eval(row["scripts"])
            data.append(row)
    return data

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
def execute_ssh_command(host, username, commands):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=host, username=username, key_filename=KEYPATH)
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
    # POSTリクエストからidを取得
    post_request_id = request.get_json().get('password')
    print("Deploy request id --> " + str(post_request_id))
    
    # CSVファイルを読み取る
    data_lines = load_csv(CSVPATH)
    # request_id, ssh_host, ssh_user, scripts
    for l in data_lines:
        print(l['request_id'])
        if post_request_id == l['request_id']:
            ssh_host = l['ssh_host']

            if ssh_host and l['ssh_user']:
                # SSH接続してコマンドを実行
                execute_ssh_command(l['ssh_host'], l['ssh_user'], l['scripts'])
                return jsonify({'status': 'success', 'message': f'Commands executed on {ssh_host}'})
            else:
                return jsonify({'status': 'error', 'message': 'Invalid SSH configuration'})
    
    return jsonify({'status': 'error', 'message': 'Password does not match any machine'})

if __name__ == '__main__':
    #csvファイルが存在しなければ作成し終了する。
    #もしくは作成プログラムの実行をうながす
    app.run(host='0.0.0.0', port=80)
