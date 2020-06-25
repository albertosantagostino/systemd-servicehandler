#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utils class for ServiceHandler
"""

from enum import Enum, auto


class Response(Enum):
    """Enum holding the response of a call"""
    # yapf: disable
    OK      = auto()
    ALREADY = auto()
    FAILED  = auto()
    # yapf: enable


def compute_response(condition):
    """Return OK if the condition is satisfied, otherwise FAILED"""
    if (condition):
        return Response.OK
    else:
        return Response.FAILED
