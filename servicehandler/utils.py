#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utils class for ServiceHandler
Alberto Santagostino, 2020
"""

import subprocess


def systemctl_command(command, unit_file):
    """Run: systemctl --user {command} {unit_file}"""
    subprocess.call(['systemctl', '--user', command, unit_file])
