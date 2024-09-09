# Deploy Listener

## 概要

このプログラムは、POSTリクエストに応じてmachinesに格納されたSSH接続先とコマンドのセットを実行し、その標準出力と標準エラー出力をDiscordチャンネルに通知するデプロイ要求をlistenし実行するものである。

## ファイル

- `webhook.txt`: Discord Webhook URLを書いておくファイル。通知先のDiscordチャンネルを指定する。
- `machines/template.txt`: 各ホストの設定情報と実行コマンドを含むテンプレートファイル。ファイル名はホスト名にするといいかも。

## 使用方法

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