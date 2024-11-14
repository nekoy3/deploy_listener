import csv
import os
import ast
import random
import string

# ファイルパスを指定
csv_file_path = "machines.csv"
headers = ["request_id", "ssh_host", "ssh_user", "scripts"]

def initialize_csv(file_path, headers):
    """ファイルが存在しない場合に作成し、ヘッダを追加する"""
    if not os.path.exists(file_path):
        with open(file_path, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(headers)
            print(f"{file_path} ファイルが作成され、ヘッダが追加されました。")

def generate_random_request_id(length=8):
    """ランダムな英数字のリクエストIDを生成する"""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

# CSVファイルの初期化（存在しなければヘッダを追加）
initialize_csv(csv_file_path, headers)

# 新しい行のデータを作成
new_row = {
    "request_id": generate_random_request_id(),
    "ssh_host": input("デプロイ先のホスト名を入力: "),
    "ssh_user": input("デプロイ先のユーザ名: "),
    "scripts": [s for s in iter(lambda: input("コマンド: "), '')]
}

# `scripts`を文字列に変換してCSVに書き込む
new_row["scripts"] = str(new_row["scripts"])

# ファイルに新しい行を追加する
with open(csv_file_path, mode="a", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=headers)
    writer.writerow(new_row)
    print("新しいデータが追加されました。")
    print(f"データのIDは {new_row['request_id']} です。")
