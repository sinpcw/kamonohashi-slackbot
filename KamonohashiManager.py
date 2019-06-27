#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import unicodedata
import subprocess as sp
import Constant


""" 全角半角の差分量を計算する """
def GetCharacterHalfAndFull(text):
    count = 0
    for c in text:
        if unicodedata.east_asian_width(c) in 'FWA':
            count += 1
    return count

""" KAMONOHASHIにログインする """
def Login(username, password):
    obj = sp.run(['kqi', 'account', 'login', '-u', username, '-p', password], stdout=sp.PIPE)

""" 閲覧可能なテナントを取得する """
def GetTenantDict():
    obj = sp.run(['kqi', 'account', 'get'], stdout=sp.PIPE)
    buf = obj.stdout.decode(Constant.KQIEncode).replace('\r\n', '\n').split('\n')
    act = False
    ret = {}
    for i in buf:
        if len(i) == 0:
            act = False
            continue
        if i.startswith('assigned tenant:'):
            act = True
        elif act:
            # 6文字のインデントがあり、テナントID(空白)テナント名称である
            ops = i[6:]
            pos = ops.find(' ')
            ret[int(ops[:pos])] = ops[pos + 1:]
    return ret

""" 指定したテナントに切替える """
def SwitchTenant(tenant):
    obj = sp.run(['kqi', 'account', 'switch-tenant', str(tenant)], stdout=sp.PIPE)

""" 現在テナントの指定したジョブIDの状態を取得する """
def GetTrainJobStatus(jobID):
    obj = sp.run(['kqi', 'training', 'get', str(jobID)], stdout=sp.PIPE)
    buf = obj.stdout.decode(Constant.KQIEncode).replace('\r\n', '\n').split('\n')
    key = 'status: '
    num = len(key)
    for itr in buf:
        if itr.startswith(key):
            return itr[num:]
    return 'Unknown'

""" 現在テナントの学習ジョブ状態一覧を取得する """
def GetTrainJobsStatus():
    obj = sp.run(['kqi', 'training', 'list'], stdout=sp.PIPE)
    buf = obj.stdout.decode(Constant.KQIEncode).replace('\r\n', '\n').split('\n')
    # Headerから各列の文字数を取得
    lst = [ 'id', 'name', 'started_at', 'dataset', 'memo', 'status' ]
    num = len(lst)
    ops = {}
    for i in range(num):
        u = buf[0].find(lst[i])
        if i == num - 1:
            ops[lst[i]] = [ u, len(buf[0]) ]
        else:
            v = buf[0].find(lst[i + 1])
            ops[lst[i]] = [ u, v - 1 ]
    # 各ヘッダー行からパース
    ret = {}
    for line in buf[1:]:
        # 必要な情報(id, name, status)を取得してまとめる.
        # id:
        pos = ops[lst[0]]
        id = line[pos[0]:pos[1]].strip()
        # name:
        pos = ops[lst[1]]
        name = line[pos[0]:pos[1]].strip()
        # status:
        # statusの前のメモ欄には全角がはいることがあるので差分値を吸収しておく
        dif = GetCharacterHalfAndFull(line)
        pos = ops[lst[5]]
        status = line[pos[0] - dif:pos[1] - dif].strip()
        # 辞書にいれる
        ret[id] = { lst[0] : id, lst[1] : name, lst[5] : status }
    return ret

""" 現在テナントの推論ジョブ一覧を取得する """
def GetInferJobsStatus():
    return {}
