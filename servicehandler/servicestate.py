#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enum class to represent service status
Alberto Santagostino, 2020
"""

from enum import Enum, auto


class ServiceState(Enum):
    """Enum holding the current state of the service"""
    # yapf: disable
    RUNNING   = auto()
    STOPPED   = auto()
    ERROR     = auto()
    RELOADING = auto()
    UNSET     = auto()
    # yapf: enable


def compute_state(properties):
    """Return the current ServiceState depending on the service properties"""

    #    +-------------+--------------------------------+
    #    | PROPERTY    | STOPPED  | RUNNING | ERROR     |
    #    +-------------+----------+---------+-----------+
    #    | MainPID     | 0        | PID     | 0         |
    #    | ActiveState | inactive | active  | failed    |
    #    | SubState    | dead     | running | failed    |
    #    | Result      | success  | success | exit-code |
    #    +-------------+----------+---------+-----------+

    ActiveState, SubState, Result = properties['ActiveState'], properties['SubState'], properties['Result']

    if (ActiveState == 'active') and (SubState == 'running'):
        return ServiceState.RUNNING
    elif (ActiveState == 'inactive') and (SubState == 'dead'):
        return ServiceState.STOPPED
    elif (Result == 'exit-code'):
        return ServiceState.ERROR
    else:
        raise RuntimeError("Service in unknown state")
