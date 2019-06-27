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

    def CreateMessage(self, tenant, id, status):
        return '{}テナントのジョブ(<{}/training/{}|{}>)は{}'.format(
                tenant,
                kamonohashi_uri,
                id,
                id,
                random.choice(self.dictdata['Message'][status if status in self.dictdata['Message'] else 'Unknown'])
            )

    def CreateMessageTo(self, tenant, id, status, users):
        message = ''
        for user in users:
            message = message + '<@' + user + '>さん、'
        return '{}{}テナントのジョブ(<{}/training/{}|{}>)は{}'.format(
                message, 
                tenant,
                kamonohashi_uri,
                id,
                id,
                random.choice(self.messages[status if status in self.messages else 'Unknown'])
            )

    def CreateTenantsRunningInfo(self, tenants, running):
        run_message = ''
        nop_message = ''
        for itr in tenants.keys():
            if itr in running:
                run_message += '{}テナントのジョブは{}件\n'.format(tenants[itr], running[itr])
            else:
                nop_message += '{}テナント\n'.format(tenants[itr])
        ret_message = ''
        if not act_message == '':
            ret_message += run_message
            ret_message += '以上がそれぞれ実行中カモ!\n'
        if not nop_message == '':
            ret_message += nop_message
            ret_message += '以上については実行中のものがないカモ'
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

    def IsPassedTime(self, seconds):
        return True if int((datetime.now() - self.sendtime).total_seconds()) > seconds else False
