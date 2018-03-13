#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import os

from fabric.api import env, run, put
from fabric.contrib.files import exists

env.user = 'semrush_test'

REMOTE_PATH = os.path.join('/home', env.user)
LOCAL_PATH = os.path.join(os.path.dirname(__file__), 'www')


def tests():
    pass


def deploy():
    put(LOCAL_PATH, REMOTE_PATH)
