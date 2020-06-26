#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Helper class to ease access to systemd services (daemons)
"""

import logging
import os
import signal
import sys
import subprocess
import time

from enum import Enum

from servicehandler.servicestate import compute_enablement_state, compute_state, ServiceEnablementState, ServiceState
from servicehandler.utils import compute_response, Response

# Setup logging
log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs', 'main.log')
os.makedirs(os.path.dirname(log_file), exist_ok=True)
logging.basicConfig(format="[%(asctime)s] %(levelname)s: (%(name)s) %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S",
                    level=logging.INFO,
                    filename=log_file)
logger = logging.getLogger(__name__)
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))


def expectation(target_state):
    """
    Decorator for ServiceHandler: set a target state and wrap the commands around a state updater
    Currently the status of the service is updated twice: before and after a command is issued
    This is time consuming but speed comes after stability whenever a service changes state
    """
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            # Not nice: check if we are not decorating kill() (FIXME: Check for alternatives)
            if (self.state() is target_state) and (func.__name__ != 'kill'):
                return Response.ALREADY
            func(self)
            self.update_state()
            return compute_response(self.state() is target_state)

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
    def __init__(self, service_name, unit_file, log_path=None):
        # Validate service name
        if not service_name:
            raise ValueError("Service name cannot be empty")
        else:
            self.service_name = service_name
        # Validate unit file
        try:
            subprocess.check_output(['systemctl', '--user', 'cat', unit_file], stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError:
            raise ValueError("Invalid unit file, check existence of .service in /lib/systemd/user/")
        else:
            self.unit_file = unit_file
        # Set and update properties and state
        self.__state = ServiceState.UNSET
        self.__enablement_state = ServiceEnablementState.UNSET
        self.__properties = None
        self.update_state(initializing=True)
        # TODO: Implement log handling

    def __str__(self):
        return f"Name: {self.service_name}\nUnit: {self.unit_file}\n" \
        + f"Enablement state: {self.__enablement_state}\nState: {self.__state}\nProperties: {self.__properties}"

    def __repr__(self):
        return f"ServiceHandler('{self.service_name}','{self.unit_file}','{self.__state}','{self.__enablement_state}')"

    def __eq__(self, other):
        return self.service_name == other.service_name

    def _systemctl_command(self, command):
        """Run: systemctl --user {command} {unit_file}"""
        subprocess.call(['systemctl', '--user', command, self.unit_file])

    def state(self):
        """Get the current service state """
        return self.__state

    def enablement_state(self):
        """Get the current service enablement_state """
        return self.__enablement_state

    @expectation(target_state=ServiceState.RUNNING)
    def start(self):
        """Start the service"""
        self._systemctl_command('start')

    # target_state check, we want Response.OK, not Response.ALREADY (FIXME)
    @expectation(target_state=ServiceState.RUNNING)
    def restart(self):
        """Restart the service"""
        self._systemctl_command('restart')

    @expectation(target_state=ServiceState.STOPPED)
    def stop(self):
        """Stop the service"""
        self._systemctl_command('stop')

    # target_state for kill() depends on the parameter restart in the unit file (FIXME)
    @expectation(target_state=ServiceState.RUNNING)
    def kill(self):
        """
        Kill the service

        If the unit file is configured with 'restart=on-failure', this will trigger an hard restart
        This function ignores decorator updates and checks for flexibility
        """
        # Prevent a weird behavior: when STOPPED and kill() is called, app crashes (FIXME)
        if self.__state is not ServiceState.STOPPED:
            os.kill(int(self.__properties['MainPID']), signal.SIGKILL)
        # Not nice but simple and currently working (FIXME)
        # TODO: Change time.sleep to wait until process of same service but different PID is up and running
        time.sleep(0.5)

    # TODO: Decorator also for enable/disable
    def enable(self):
        """Enable the service"""
        if self.__enablement_state is ServiceEnablementState.ENABLED:
            return Response.ALREADY
        import ipdb
        ipdb.set_trace()
        self._systemctl_command('enable')
        self.update_state()
        return compute_response(self.__enablement_state is ServiceEnablementState.ENABLED)

    def disable(self):
        """Disable the service"""
        if self.__enablement_state is ServiceEnablementState.DISABLED:
            return Response.ALREADY
        self._systemctl_command('disable')
        self.update_state()
        return compute_response(self.__enablement_state is ServiceEnablementState.DISABLED)

    def update_state(self, initializing=False):
        """Update service properties and states"""
        # Relevant properties to determine the state
        properties = ['ActiveState', 'SubState', 'Result', 'MainPID', 'UnitFileState']
        res = subprocess.check_output(['systemctl', '--user', 'show',
                                       f'{self.unit_file}']).decode('ascii').strip().split('\n')
        result = {prop.split('=')[0]: prop.split('=')[1] for prop in res}
        old_state = self.__state
        old_enablement_state = self.__enablement_state
        self.__properties = {k: result[k] for k in properties if k in result}
        self.__state = compute_state(self.__properties)
        self.__enablement_state = compute_enablement_state(self.__properties)

        # TODO: Create function to avoid duplication
        if (old_state is not ServiceState.UNSET) and (old_state is not self.__state) and not initializing:
            logging.info(f"{self.service_name} changed enablement state to {self.__state}")
        if (old_enablement_state is not ServiceState.UNSET) and (old_enablement_state
                                                                 is not self.__enablement_state) and not initializing:
            logging.info(f"{self.service_name} changed enablement state to {self.__enablement_state}")
