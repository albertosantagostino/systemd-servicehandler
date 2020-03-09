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

from servicehandler.servicestate import ServiceState, ServiceEnablementState, compute_state, compute_enablement_state
from servicehandler.utils import Response, compute_response


def expectation(target_state):
    """Decorator for ServiceHandler methods, wrap the commands around a state updater and set a target state"""
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            self.update_state()
            if (compute_response(self.state is target_state) is Response.OK):
                return Response.ALREADY
            func(self)
            self.update_state()
            return compute_response(self.state is target_state)

        return wrapper

    return decorator


class ServiceHandler():
    """
    Systemd service handler

    Args:
        service_name: Name of the service
        unit_file:    Service configuration file (/usr/lib/systemd/user/<unit_file>.service)

    Examples:
        ServiceHandler('Sample service', 'service-sample.service')

    Raises:
        ValueError: If service_name is empty or if unit_file is neither existing nor valid
    """
    def __init__(self, service_name, unit_file):
        # Validate service name
        if not service_name:
            raise ValueError("Service name cannot be empty")
        else:
            self.service_name = service_name
        # Validate unit file
        try:
            # TODO: Handle if .service is missing?
            proc = subprocess.check_output(['systemctl', '--user', 'cat', unit_file], stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError:
            raise ValueError("Invalid unit file, check existence and validity") from None
        else:
            self.unit_file = unit_file

        # Set and update properties and state
        self.state = ServiceState.UNSET
        self.enablement_state = ServiceEnablementState.UNSET
        self.properties = None
        self.update_state()

    def __str__(self):
        return f"Name: {self.service_name}\nUnit: {self.unit_file}\n" \
        + f"Enablement state: {self.enablement_state}\nState: {self.state}\nProperties: {self.properties}"

    def __repr__(self):
        return f"ServiceHandler('{self.service_name}','{self.unit_file}','{self.state}','{self.enablement_state}')"

    def __eq__(self, other):
        return self.service_name == other.service_name

    def _systemctl_command(self, command):
        """Run: systemctl --user {command} {unit_file}"""
        subprocess.call(['systemctl', '--user', command, self.unit_file])

    @expectation(ServiceState.RUNNING)
    def start(self):
        """Start the service"""
        self._systemctl_command('start')

    @expectation(ServiceState.RUNNING)
    def restart(self):
        """Restart the service"""
        self._systemctl_command('restart')

    @expectation(ServiceState.STOPPED)
    def stop(self):
        """Stop the service"""
        self._systemctl_command('stop')

    @expectation(ServiceState.STOPPED)
    def kill(self):
        """Kill the service"""
        self._systemctl_command('kill')

    def enable(self):
        """Enable the service"""
        if self.enablement_state is ServiceEnablementState.ENABLED:
            return Response.ALREADY
        self._systemctl_command('enable')
        self.update_state()
        return compute_response(self.state is ServiceEnablementState.ENABLED)

    def disable(self):
        """Disable the service"""
        if self.enablement_state is ServiceEnablementState.DISABLED:
            return Response.ALREADY
        self._systemctl_command('disable')
        self.update_state()
        return compute_response(self.state is ServiceEnablementState.DISABLED)

    def update_state(self):
        """Update service properties and states"""
        # Relevant properties to determine the state
        properties = ['ActiveState', 'SubState', 'Result', 'MainPID', 'UnitFileState']
        res = subprocess.check_output(['systemctl', '--user', 'show',
                                       f'{self.unit_file}']).decode('ascii').strip().split('\n')
        result = {prop.split('=')[0]: prop.split('=')[1] for prop in res}
        old_state = self.state
        self.properties = {k: result[k] for k in properties if k in result}
        self.state = compute_state(self.properties)
        self.enablement_state = compute_enablement_state(self.properties)

        # TODO: Remove, only for debug purposes
        if (old_state is not ServiceState.UNSET) and (old_state is not self.state):
            print(f"{self.service_name} changed state to {self.state}")
