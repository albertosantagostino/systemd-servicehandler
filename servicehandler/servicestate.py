#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enum classes to represent service status
"""

from enum import Enum, auto
from operator import itemgetter


class ServiceState(Enum):
    """Enum holding the current state of the service"""
    # yapf: disable
    RUNNING   = auto()
    STOPPED   = auto()
    ERROR     = auto()
    RELOADING = auto()
    UNSET     = auto()
    # yapf: enable


class ServiceEnablementState(Enum):
    """Enum holding the current enablement state of the service"""
    # yapf: disable
    ENABLED  = auto()
    DISABLED = auto()
    UNSET    = auto()
    # yapf: enable


def compute_state(properties):
    """Return the current ServiceState depending on the service properties"""
    #    +-------------+--------------------------------+
    #    | PROPERTY    | STOPPED  | RUNNING | ERROR     |
    #    +-------------+----------+---------+-----------+
    #    | ActiveState | inactive | active  | failed    |
    #    | SubState    | dead     | running | failed    |
    #    | Result      | success  | success | exit-code |
    #    | (MainPID)   | 0        | (PID)   | 0         |
    #    +-------------+----------+---------+-----------+

    ActiveState, SubState, Result = itemgetter('ActiveState', 'SubState', 'Result')(properties)

    if ActiveState == 'active' and SubState == 'running':
        return ServiceState.RUNNING
    elif ActiveState == 'inactive' and SubState == 'dead':
        return ServiceState.STOPPED
    elif ActiveState == 'activating' and SubState == 'auto-restart':
        return ServiceState.RELOADING
    elif Result == 'exit-code':
        return ServiceState.ERROR
    else:
        raise RuntimeError("Service in unknown state")


def compute_enablement_state(properties):
    """Return the current ServiceState depending on the service properties"""
    #    +---------------+----------+----------+
    #    | PROPERTY      | ENABLED  | DISABLED |
    #    +---------------+----------+--------- +
    #    | UnitFileState | enabled  | disabled |
    #    +---------------+----------+----------+

    UnitFileState = itemgetter('UnitFileState')(properties)

    if UnitFileState == 'enabled':
        return ServiceEnablementState.ENABLED
    elif UnitFileState == 'disabled':
        return ServiceEnablementState.DISABLED
    else:
        raise RuntimeError("Service in unknown enablement state")
