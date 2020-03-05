#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Helper class to ease access to systemd services (daemon)
Alberto Santagostino, 2020
"""

import os
import sys
import subprocess
import time

from enum import Enum

from servicehandler.servicestate import ServiceState, compute_state
from servicehandler.utils import *


class ServiceHandler():
    """
    Systemd service handler

    Args:
        name: Name of the service
        unit_file: Service configuration file (assumed in /usr/lib/systemd/user)
    """
    def __init__(self, name, unit_file):
        self.service_name = name
        self.unit_file = unit_file
        self.state = ServiceState.UNSET
        self.properties = None

        # Update properties and state
        self.update_state()

    def __str__(self):
        return f"Name: {self.service_name}\nUnit: {self.unit_file}\nState: {self.state}\nProperties:{self.properties}"

    def __repr__(self):
        return f"ServiceHandler('{self.service_name}','{self.unit_file}','{self.state}')"

    def __eq__(self, other):
        return self.service_name == other.service_name

    def start(self):
        """Start the service"""
        if self.state is ServiceState.RUNNING:
            return True
        systemctl_command('start', self.unit_file)
        self.update_state()
        return self.state is ServiceState.RUNNING

    def restart(self):
        """Restart the service"""
        # Always possible to restart the service, from any state
        systemctl_command('restart', self.unit_file)
        self.update_state()
        return self.state is ServiceState.RUNNING

    def stop(self):
        """Stop the service"""
        if self.state is ServiceState.STOPPED:
            return True
        systemctl_command('stop', self.unit_file)
        self.update_state()
        return self.state is ServiceState.STOPPED

    def kill(self):
        """Kill the service"""
        if self.state is ServiceState.STOPPED:
            return True
        systemctl_command('kill', self.unit_file)
        self.update_state()
        return self.state is ServiceState.STOPPED

    def status(self):
        """Check the service status"""
        return self.state

    def update_state(self):
        """Update service properties and ServiceState"""
        # Relevant properties to determine the state
        properties = ['ActiveState', 'SubState', 'Result', 'MainPID']
        res = subprocess.check_output(['systemctl', '--user', 'show',
                                       f'{self.unit_file}']).decode('ascii').strip().split('\n')
        result = {prop.split('=')[0]: prop.split('=')[1] for prop in res}

        self.properties = {k: result[k] for k in properties if k in result}
        self.state = compute_state(self.properties)
