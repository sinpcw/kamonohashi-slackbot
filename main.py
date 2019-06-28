#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import time
import Constant
import KamonohashiManager as kqi
from datetime import datetime
from JsonManager import JsonManager
from MessageManager import MessageManager
from absl import app, flags

""" 引数 """
FLAGS = flags.FLAGS
flags.DEFINE_string('config_root', None, '実行スクリプトの場所を指定する.')

""" 処理 """
def GetWatchCondition(configure):
    weekday = datetime.now().weekday()
    condition = configure['Watch']['Default']
    if Constant.WeekDayString[weekday] in configure['Watch']:
        weekday_condition = configure['Watch'][Constant.WeekDayString[weekday]]
        for itr in [ 'Active', 'Tenant', 'Enter', 'Leave' ]:
            if itr in weekday_condition:
                condition[itr] = weekday_condition[itr]
    return condition

def UpdateWatchStatus(status, condition, message):
    msg = None
    # 現在時間を取得
    date = datetime.now()
    hour = date.hour
    wday = date.weekday()
    # 日次処理未実行の場合は有効
    if status['dailyjob'] == False and condition['Active']:
        if not status['watching']:
            if condition['Enter'] <= hour and condition['Leave'] < hour:
                status['watching'] = False
                status['dailyjob'] = True
            elif condition['Enter'] <= hour:
                status['watching'] = True
                message.ResetSendItem()
                msg = message.GetSystemMessage('Enter')
        elif condition['Leave'] < hour:
            status['watching'] = False
            status['dailyjob'] = True
            if message.CountSendItem() == 0 and message.IsContainSystemMessage('Leave.Silent'):
                msg = message.GetSystemMessage('Leave.Silent')
            elif message.IsContainSystemMessage('Leave.' + WeekDayString[wday]):
                msg = message.GetSystemMessage('Leave.' + WeekDayString[wday])
            else:
                msg = message.GetSystemMessage('Leave')
    message.SendSystemMessage(msg)
    return status

def UpdateTenantTrainStatus(tenant_status, tenant_condition, tenant, watch_status, message, kqi):
    return UpdateTenantStatus(tenant_status, tenant_condition, tenant, watch_status, message, kqi, 'Train')

def UpdateTenantInferStatus(tenant_status, tenant_condition, tenant, watch_status, message, kqi):
    return UpdateTenantStatus(tenant_status, tenant_condition, tenant, watch_status, message, kqi, 'Infer')

def UpdateTenantStatus(tenant_status, tenant_condition, tenant, watch_status, message, kqi, state):
    tenant_name = str(tenant) + '.' + state
    if not watch_status['watching'] or not tenant_name in tenant_status:
        tenant_status['state'][tenant_name] = kqi.GetTrainJobsStatus() if state == 'Train' else kqi.GetInferJobsStatus()
        return tenant_status
    # ジョブ状況収集対象
    #       N/A -> Running
    #   Pending -> Running
    #   Running -> Completed
    #   Pending -> Completed
    #   Running -> Killed
    #   Pending -> Killed
    #       N/A -> UserCanceled
    #   Pending -> UserCanceled
    #   Running -> UserCanceled
    old_status = tenant_status['state'][tenant_name]
    now_status = kqi.GetTrainJobsStatus() if state == 'Train' else kqi.GetInferJobsStatus()
    for job in status:
        # テナントの実行ジョブ数に加算:
        if now_status[job]['status'] == 'Running':
            tenant_status['count'][tenant] = tenant_status['count'][tenant] + 1 if tenant in tenant_status['count'] else 1
        # ジョブステータス変更によるものをチェックする:
        if not job in old_status:
            # 過去: 履歴にない
            if now_status[job]['status'] == 'Running':
                # 現在: 実行中
                # 通知がおおくなりそうなのでとりあえずいまは実装していない
                pass
            elif now_status[jobid]['status'] in [ 'Completed', 'Killed', 'UserCanceled' ]:
                # 現在: 完了/キル/ユーザーキャンセル
                # ポーリングよりもジョブが終わるほうが早いケースはないと考えられるので実装していない
                pass
        else:
            # 過去: いずれかの情報が存在する
            if old_status[job]['status'] == 'Pending' and now_status[job]['status'] == 'Running':
                # 過去: 待機中
                # 現在: 実行中
                # 通知がおおくなりそうなのでとりあえずいまは実装していない
                pass
            elif old_status[job]['status'] == 'Running' and now_status[job]['status'] != 'Running':
                # 過去: 実行中
                # 現在: 完了/キル/ユーザーキャンセル
                if 'ByName' in tenant_condition and len(tenant_condition['ByName']) > 0:
                    message.SendMessage(message.CreateMessageTo(tenant, job, state[job]['status'], tenant_condition['ByName']))
                else:
                    message.SendMessage(message.CreateMessage(tenant, job, state[job]['status']))
    # ステータス更新
    tenant_status['state'][tenant_name] = status
    return tenant_status

""" エントリポイント """
def main(argv):
    print('Kamonohashi Slackbot')

    # KQI実行のための環境変数追加
    if os.name == 'posix':
        # linux: kqiが格納されている場所 (デフォルトの想定場所)
        # 本当は外だしすべき
        kqicli = '/home/(username)/.local/bin'
        os.environ['PATH'] = os.environ['PATH'] + ':' + kqicli

    # 設定ファイルの読込み
    sec = JsonManager(filepath=os.path.join(FLAGS.config_root, 'secure.json'))
    cfg = JsonManager(filepath=os.path.join(FLAGS.config_root, 'config.json'))
    msg = MessageManager(filepath=os.path.join(FLAGS.config_root, 'message.json'), kamonohashi_uri=sec['KAMONOHASHI']['Server'], postmessage_uri=sec['SlackURI'])

    # 監視状態変数
    watch_status = { 
        'dailyjob' : False,
        'watching' : False,
        'waketime' : datetime.now()
    }
    # テナント状態変数
    tenant_status = {
        'count' : {},
        'state' : {}
    }
    tenant_active_job = {}
    # 監視開始
    print('Watch Loop Start')
    while True:
        sec.Load()
        kqi.Login(sec['KAMONOHASHI']['Application']['Username'], sec['KAMONOHASHI']['Application']['Password'])
        tenants = kqi.GetTenantDict()
        print('Daily Loop Start')
        while datetime.now().day == watch_status['waketime'].day:
            msg.Load()
            cfg.Load()
            # 監視状態更新
            watch_status = UpdateWatchStatus(watch_status, GetWatchCondition(cfg), msg)
            # 監視状態がアクティブの場合はテナント毎に監視処理を行う
            for tenant in tenants:
                tenant_condition = {}
                if str(tenant) in cfg['Tenant']:
                    tenant_condition = cfg['Tenant'][str(tenant)]
                kqi.SwitchTenant(tenant)
                # 監視状態かどうか
                tenant_status = UpdateTenantTrainStatus(tenant_status, tenant_condition, tenant, watch_status, msg, kqi)
                tenant_status = UpdateTenantInferStatus(tenant_status, tenant_condition, tenant, watch_status, msg, kqi)
            # サーバーヘルス監視(特に監視したいのはGPU温度)
            # T.B.D
            # すべての監視対象テナントでしばらくメッセージ送信していない場合は実行中に応じてメッセージを投げる
            if watch_status['watching'] and msg.IsPassedTime(seconds=120 * 60):
                msg.SendMessage(msg.CreateTenantsRunningInfo(tenants, tenant_status['count']))
            # 連続で処理すると負荷がかかるため、指定したポーリング間隔で待機
            time.sleep(cfg['Polling'])
        # 日の処理完了を抜けた場合はリセットする
        watch_status['dailyjob'] = False

if __name__ == '__main__':
    flags.mark_flag_as_required('config_root')
    app.run(main)