# Deploy Listener

## 概要

このプログラムは、デプロイ要求をlistenし、要求に応じてsshでデプロイ処理をリモート実行するものである。
デプロイを実行するホストと実行コマンドを用意しておき、実行した際の出力をDiscordチャンネルに通知することも可能。

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
   deploy_lister内に`keypath.txt`を設置しキーの場所をフルパスで入力しておく。
   ```
   /home/ユーザ名/.ssh/deploy_key
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

## デプロイ時のsudoコマンド実行について

   `echo 'password' | sudo -S systemctl restart xxx`
   のように、パスワードを平文でsudo -Sに渡して実行することは可能だったが、危険なためNOPASSWD設定を推奨。
   ```bash
   $ sudo visudo
   ```
   で以下のように設定する。
   ```bash
   # User privilege specification
root    ALL=(ALL:ALL) ALL

# Members of the admin group may gain root privileges
%admin ALL=(ALL) ALL

# Allow members of group sudo to execute any command
%sudo   ALL=(ALL:ALL) ALL

# See sudoers(5) for more information on "@include" directives:
user ALL=(ALL) NOPASSWD: /bin/git pull
user ALL=(ALL) NOPASSWD: /bin/systemctl restart nsd

@includedir /etc/sudoers.d
   ```
   sudo時にパスワード認証が不要となるため、万が一NOPASSWD実行できても問題が無いと判断できたものだけ設定する。    

   例：
   ```
   user ALL=(ALL) NOPASSWD: /bin/git pull
   user ALL=(ALL) NOPASSWD: /bin/systemctl restart nsd
   ```
   の部分は「ユーザuserでsudo git pullとsudo systemctl restart nsdのみパスワード不要で実行する」という設定。
   また、
   ```
   %sudo   ALL=(ALL:ALL) ALL
   ```
   より下でなければ、sudoの実行権限があるユーザ（sudoグループのユーザ）はすべてパスワードありで実行できる権限で上書きされて、NOPASSWDが効果を発揮しないため注意。


    
## よてい

   curlでmachinesにデータ追加/編集できるようにしようかな  
