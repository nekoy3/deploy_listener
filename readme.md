# Deploy Listener

## 概要

このプログラムは、POSTリクエストに応じてmachinesに格納されたSSH接続先とコマンドのセットを実行し、その標準出力と標準エラー出力をDiscordチャンネルに通知するデプロイ要求をlistenし実行するものである。

## ファイル

- `webhook.txt`: Discord Webhook URLを書いておくファイル。通知先のDiscordチャンネルを指定する。
- `machines/template.txt`: 各ホストの設定情報と実行コマンドを含むテンプレートファイル。ファイル名はホスト名にするといいかも。

## セットアップ

1. **テンプレートの準備**:

   `machines/template.txt` をコピーして、ホストごとの設定ファイルを作成する。

2. **Webhookの設定**:

   `webhook.txt` にDiscordのWebhook URLを設定します。（ﾛｸﾞﾌｧｲﾙを用意していないので、Discordに飛ばさないとコマンドのログが見れない）（現状）

3. **ライブラリのインストール**:
   ```bash
   pip install flask paramiko requests
   ```

4. **権限周りの設定**:

    全てのファイルをdp_listener所有にする。
    `sudo chown dp_listener:dp_listener`

5. **service化**

    /etc/systemd/system/deploy_listener.service を設置する。
    ```bash
    sudo systemctl daemon-reload
    sudo systemctl enable deploy_listener.service
    sudo systemctl start deploy_listener.service
    ```

## 使用方法

   curlコマンドを実行

 ```bash
    curl -X POST http://これ動いてるサーバ:5000/deploy \
    -H "Content-Type: application/json" \
    -d '{"password": "your_secret_password"}'
 ```
    
   を飛ばすことで、machinesのxxx.txt一行目にあるpasswordと今回渡したpasswordを比較し、一致していればそのマシンにssh接続しデプロイを実行する。
    
## よてい

   curlでmachinesにテキストファイル突っ込める/編集できるようにしようかな
   machinesの.txtに変数が使えるようにしようかな
   `echo 'password' | sudo -S systemctl restart xxx`とかが使えるように
