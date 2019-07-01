#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import random
import subprocess as sp
from datetime import datetime
from JsonManager import JsonManager

DEBUG = False

class MessageManager(JsonManager):
    def __init__(self, filepath, kamonohashi_uri, postmessage_uri):
        super(MessageManager, self).__init__(filepath=filepath)
        self.kamonohashi_uri = kamonohashi_uri
        self.postmessage_uri = postmessage_uri
        self.sendtime = datetime.now()
        self.senditem = 0

    def ResetSendItem(self):
        self.senditem = 0

    def CountSendItem(self):
        return self.senditem

    def IsContainMessage(self, keyword):
        return True if keyword in self.dictdata['Message'] else False

    def IsContainSystemMessage(self, keyword):
        return True if 'System.' + keyword in self.dictdata['Message'] else False

    def GetMessage(self, keyword):
        return random.choice(self.dictdata['Message'][keyword if keyword in self.dictdata['Message'] else 'Unknown'])

    def GetSystemMessage(self, keyword):
        keyword = 'System.' + keyword
        return random.choice(self.dictdata['Message'][keyword if keyword in self.dictdata['Message'] else 'System.Unknown'])

    def CreateMessage(self, tenant, id, keyword):
        return '{}テナントのジョブ(<{}/training/{}|{}>)は{}'.format(
                tenant,
                self.kamonohashi_uri,
                id,
                id,
                self.GetMessage(keyword)
            )

    def CreateMessageTo(self, tenant, id, keyword, users):
        message = ''
        for user in users:
            message = message + '<@' + user + '>さん、'
        return '{}{}テナントのジョブ(<{}/training/{}|{}>)は{}'.format(
                message, 
                tenant,
                self.kamonohashi_uri,
                id,
                id,
                self.GetMessage(keyword)
            )

    def CreateTenantsRunningInfo(self, tenants, running):
        run = []
        nop = []
        for itr in tenants.keys():
            if itr in running:
                run.append('{}テナントのジョブは{}件'.format(tenants[itr], running[itr]))
            else:
                nop.append('{}テナント'.format(tenants[itr]))
        ret_message = ''
        # 実行あり
        run_n = len(run)
        if run_n > 1:
            for i in range(run_n):
                ret_message += '・' + run[i] + '\n'
            ret_message += '以上がそれぞれのテナントで実行中カモ!\n'
        elif run_n == 1:
            ret_message += run[0] + 'が実行中カモ!\n'
        # 実行なし
        nop_n = len(nop)
        if nop_n > 1:
            for i in range(nop_n):
                ret_message += '・' + nop[i] + '\n'
            ret_message += '上記のテナントでは実行中のものがないカモ\n'
        elif nop_n == 1:
            ret_message += nop[0] + 'については実行中のものがないカモ'
        # 監視なし
        if run_n + nop_n == 0:
            ret_message = random.choice(self.dictdata['Message']['Bored']) if 'Bored' in self.dictdata['Message'] else None
        return ret_message

    def SendMessage(self, message):
        if message is not None:
            if DEBUG:
                print('message : {}'.format(message))
            else:
                out = sp.run(['/usr/bin/curl', '-X', 'POST', '-H', '\'Content-type: application/json\'', '--data', '{ \"text\" : \"' + message + '\" }', self.postmessage_uri ], stdout=sp.PIPE)
            self.sendtime = datetime.now()
            self.senditem = self.senditem + 1

    def SendSystemMessage(self, message):
        if message is not None:
            if DEBUG:
                print('message : {}'.format(message))
            else:
                out = sp.run(['/usr/bin/curl', '-X', 'POST', '-H', '\'Content-type: application/json\'', '--data', '{ \"text\" : \"' + message + '\" }', self.postmessage_uri ], stdout=sp.PIPE)

    def UpdateTimestamp(self):
        self.sendtime = datetime.now()

    def IsPassedTime(self, seconds):
        return True if int((datetime.now() - self.sendtime).total_seconds()) > seconds else False
