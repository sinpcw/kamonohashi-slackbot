# kamonohashi-slackbot

## 概要
OSSであるAI開発プラットフォームの[KAMONOHASHI](https://github.com/KAMONOHASHI)の実行ジョブ状態監視を行い、変化を通知するSlackBotです.  
Slack側はincoming webhookを使用してAPI経由で通知を行います.  

### 現在監視している状態変化
* RunningからCompleted
* RunningからKilled
* PendingからCompleted
* PendingからKilled

PendingからRunningについては実行数次第です.  
通知が多くなり煩雑になると考えられるため、現状は監視対象としていません.

## 依存するプログラムなど
* curl
* python3
* python3-pip

## 環境設定

### 注意点
インストールするサーバーのユーザーによって変わるため、(username)など記載の部分は適宜変更が必要です.  
secure-template.jsonはsecure.jsonにリネームして運用してください.  
同梱のserviceファイルなどの配置想定は /home/(username)/kamonohashi-slackbot です.  
別のパスでサービスにする際には service 内の各ファイルのパスを適当に併せて変更してください.  

### 監視対象テナントの設定
config.jsonを開き設定を行います.  
KAMONOHASHI上のテナントIDを "Tenant" のリストに数値として記載します.  
ここに記載されていないIDのテナントでジョブ状態に変化があっても通知されません.  
```config.json
    ...
    "Default" :
    {
        "Active" : false,
        "Tenant" : [ (TenantIDs) ],
        "Enter" : 9,
        "Leave" : 17
    },
```

### ユーザー指定の通知の設定
config.jsonを開き設定を行います.  
テナント毎に通知したいユーザーがいる場合、@(SlackUserName)に飛ばすことができます.  
もしユーザー指定が不要の場合は (TenantID) の項目ごと削除してください.  
```config.json
    ...
    "Tenant" :
    {
        (TenantID) : {
            "ByName" : [ (SlackUserName) ]
        }
    }
    ...
}
```

### 認証関連情報設定
secure.jsonを開き設定を行います.  
ServerはKAMONOHASHIのURIを指定します.  
Application項のUsername, PasswordはKAMONOHASHIにアクセスするユーザーの認証情報を指定します.  
通常はリソース監視だけができるアカウントを作成する.
そのアカウントは監視専用で使用するという運用が望ましいと思います.  
またSlackURIには incoming-webhook のAPI URIを指定します.  
```
{
    "KAMONOHASHI" : 
    {
        "Server" : "http://kamonohashi.example.com/#/",
        "Application" :
        {
            "Username" : "watch_only_user",
            "Password" : "watch_only_pass"
        }
    },
    "SlackURI" : "https://example.slack.incoming-webhook/api"
}
```

## インストール方法

### ソースコードのダウンロード
```bash
git clone https://github.com/sinpcw/kamonohashi-slackbot.git
cd kamonohashi-slackbot
```

### ファイルの配置
secure-template.jsonをsecure.jsonにリネームします.  
先の環境設定を参考にSlackAPIのURIやKAMONOHASHIアプリケーションユーザー情報を設定します.  
```bash
cd config
mv secure-template.json secure.json
# 先の設定などをもとにsecure.jsonの中身を設定
vi secure.json
# 先の設定などをもとにconfig.jsonの中身を設定
vi config.json
cd ../
```

### 実行確認
下記コマンドで実行できることを確認します.
サービス実行時は root で実行されるために sudo で確認しておきます.  
```bash
sudo python3 main.py --config_root=/home/(username)/kamonohashi-slackbot/config
```

### serviceファイルを配置
テンプレートをそのまま使う場合は必要な個所を書き換えたうえで、下記コマンドでそのままを使えると思います.
```bash
cd service-template
sudo cp SlackBot.service /etc/systemd/system/SlackBot.service
sudo cp SlackBotConfig /etc/sysconfig/SlackBotConfig
```

### サービス登録
systemctlでサービスを登録します.  
```bash
sudo systemctl enable SlackBot.service
sudo systemctl start SlackBot.service
```

### サービスの起動確認
実行状態が active であるか確認します.
```bash
sudo systemctl status SlackBot.service
```

## その他の情報

### 監視できるテナントについて
SlackBotが監視できるテナントはアプリケーションアカウントが見えるテナントのみです.  
そのため他のテナントを見たい場合は管理者側でテナントにアクセス権を付与してもらう必要があります.  
