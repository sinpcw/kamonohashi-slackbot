#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os

""" 曜日インデックス(int)をJSON用文字列(string)に変換するためのリスト """
WeekDayString = [ 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday' ]

""" KAMONOHASHI-CLIで処理するエンコードを指定する """
KQIEncode = 'utf-8' if os.name == 'posix' else 'cp932'
