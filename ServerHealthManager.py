#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import subprocess as sp
from datetime import datetime

def GetTemparetureFromNvidiaSmi(message):
    init = False
    head = False
    hpos = 0
    vpos = 0
    cpos = 0
    spos = 0
    ret = []
    for i, line in enumerate(message):
        if not init:
            if line.startswith('+-'):
                init = True
            continue
        elif line.startswith('|-'):
            head = True
        elif line.startswith('|='):
            head = False
            spos = i + 1
        elif line.startswith('+-'):
            text = message[spos + vpos]
            temp = text[hpos:text.find('C', hpos)].strip()
            ret.append(int(temp))
            head = False
            spos = i + 1
        elif len(line.strip()) == 0:
            break
        elif head:
            if 'Temp' in line:
                hpos = line.find('Temp')
                vpos = cpos
            else:
                cpos = cpos + 1
    return ret

def GetServerGPUTemparetures(hostname, username, userpass):
    cmd = [ 'sshpass', '-p', userpass, 'ssh', username + '@' + hostname, 'nvidia-smi' ]
    ret = sp.run(cmd, stdout=sp.PIPE)
    msg = ret.stdout.decode().split('\n')
    return GetTemparetureFromNvidiaSmi(msg)

