# kamonohashi-slackbot

## 概要
KAMONOHASHIのジョブ状態監視を行い、変化を通知するSlackBotです.  
ユーザーによって変わるため(username)など記載の部分は適宜変更が必要です.  
secure-template.jsonはsecure.jsonにリネームして運用してください.  

### 現在監視している状態変化は下記の通り
* RunningからCompleted
* RunningからKilled
* PendingからCompleted
* PendingからKilled

## 必要なもの
* curl
* python3
* python3-pip

## requirements
必要なパッケージは以下の通り.  
* absl-py
* kamonohashi-cli

## 注意点
インストール先の想定は /home/(username)/kamonohashi-slackbot です.  
別のパスでサービスにする際には service 内の各ファイルのパスを適当に併せて変更してください.  

## インストール方法

### 適当なディレクトリに展開します.
```bash
git clone https://github.com/sinpcw/kamonohashi-slackbot.git
cd kamonohashi-slackbot
```
### ファイルの配置
secure-template.jsonをsecure.jsonにリネームして,  
Slack通知送付先URIやKAMONOHASHIアプリケーションユーザー情報を設定します.  
```bash
mv secure-template.json secure.json
vi secure.json
```

### 実行テスト
下記コマンドで実行できることを確認します.
サービス実行時は root で実行されるために sudo で確認しておきます.  
```bash
sudo python3 main.py --config_root=./config
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

### 状態確認
実行状態が active であるか確認します.
```bash
sudo systemctl status SlackBot.service
```

## 作業情報

### 監視できるテナントについて
SlackBotが監視できるテナントはアプリケーションアカウントが見えるテナントのみです.  
そのため他のテナントを見たい場合は管理者側でテナントにアクセス権を付与してもらう必要があります.  
