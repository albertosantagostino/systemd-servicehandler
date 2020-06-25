#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example 01: Single service handler
"""

import servicehandler as sh


def main():
    # Create a new service handler providing a name and the configuration file
    MyService = sh.ServiceHandler('My service', 'my-service.service')

    # Start the service
    MyService.start()

    # Check the status
    MyService.status()

    # Terminate the service
    MyService.stop()

    # Force kill the service
    MyService.kill()


if __name__ == "__main__":
    main()
