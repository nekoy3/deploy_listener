# Deploy Listener

## 概要

このプログラムは、POSTリクエストに応じてmachinesに格納されたSSH接続先とコマンドのセットを実行し、その標準出力と標準エラー出力をDiscordチャンネルに通知するデプロイ要求をlistenし実行するものである。

## ファイル

- `webhook.txt`: Discord Webhook URLを書いておくファイル。通知先のDiscordチャンネルを指定する。
- `machines/template.txt`: 各ホストの設定情報と実行コマンドを含むテンプレートファイル。ファイル名はホスト名にするといいかも。

## セットアップ

1. **テンプレートの準備**:

   `machines/template.txt` をコピーして、ホストごとの設定ファイルを作成する。

2. **鍵の準備**:

   このデプロイリスナが動作するマシンで鍵ペアを作っておき、ssh-copy-idで共有しておく。
   何となくデフォルトのid_rsaではなく、deploy_keyというファイルを作ってやっているが、id_rsaでもいいと思う。
   -m PEMしておかないとparamikoがinvalid key判定してssh接続できないので注意
   ```bash
   $ ssh-keygen -t rsa -m PEM -C "deploy.mynk.home" -f ~/.ssh/deploy_key
   $ ssh-copy-id -i ~/.ssh/deploy_key.pub ユーザ名@ホスト名(user@example.com)
   ```
   接続確認 Permission Deniedが出たら鍵交換ミスってるかも
   ```bash
   $ ssh -i ~/.ssh/deploy_key user@example.com 'echo "success"'
   ```

3. **Webhookの設定**:

   `webhook.txt` にDiscordのWebhook URLを設定します。（ﾛｸﾞﾌｧｲﾙを用意していないので、Discordに飛ばさないとコマンドのログが見れない）（現状）

4. **ライブラリのインストール**:
   ```bash
   pip install flask paramiko requests
   ```

5. **権限周りの設定**:

    全てのファイルをdp_listener所有にする。
    `sudo chown dp_listener:dp_listener`

6. **service化**

    /etc/systemd/system/deploy_listener.service を設置する。
    ```bash
    sudo systemctl daemon-reload
    sudo systemctl enable deploy_listener.service
    sudo systemctl start deploy_listener.service
    ```

## 使用方法

   curlコマンドを実行

 ```bash
    curl -X POST http://これ動いてるサーバ/deploy \
    -H "Content-Type: application/json" \
    -d '{"password": "your_secret_password"}'
 ```
    
   を飛ばすことで、machinesのxxx.txt一行目にあるpasswordと今回渡したpasswordを比較し、一致していればそのマシンにssh接続しデプロイを実行する。
    
## よてい

   curlでmachinesにテキストファイル突っ込める/編集できるようにしようかな  
     
   machinesの.txtに変数が使えるようにしようかな  
   `echo 'password' | sudo -S systemctl restart xxx`とかが使えるように  

   これ自身のデプロイだとcurlで応答する前にrestartしてしまうから、restartのために別プロセスで時間差かけて再起動するとかしないといけないかも  
   めんどいからうちはtxtファイルにwebhook URL直打ちしてgit pullの履歴だけ通知するようにした
