#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import time
import json
import subprocess as sp

class JsonManager(object):
    def __init__(self, filepath):
        self.filepath = filepath
        self.readtime = os.path.getctime(filepath)
        with open(self.filepath, 'r', encoding='utf-8') as f:
            self.dictdata = json.load(f)
        self.readtime = os.path.getctime(self.filepath)

    def __getitem__(self, keyword):
        return self.dictdata[keyword]

    def Load(self):
        date = os.path.getctime(self.filepath)
        if self.readtime == date:
            return
        with open(self.filepath, 'r') as f:
            self.dictdata = json.load(f)
        self.readtime = date
