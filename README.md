<a href="https://pypi.org/project/servicehandler/" target="\_parent"><img alt="#PyPI" src="https://img.shields.io/pypi/v/servicehandler?color=blue"></a> <a href="https://github.com/albertosantagostino/systemd-servicehandler/blob/master/LICENSE" target="\_parent"><img alt="GitHub - License" src="https://img.shields.io/github/license/albertosantagostino/systemd-servicehandler"></a>

<p align="center"><img src="docs/img/banner.svg" /></p>

`servicehandler` is an orchestrator for systemd services, distributed as a Python package. It provides abstraction for services and implements helper methods, wrapping the `systemctl` command

Using the package does **not** require root permissions, as the user service manager is used (with unit files in `/usr/lib/systemd/user/`)

## Description

A service (aka *daemon*) is defined by its **unit file** (e.g. `/usr/lib/systemd/user/my-service.service`):

```ini
[Unit]
Description=My service

[Service]
ExecStart=/usr/bin/python3 /home/user/service_script/main.py
Environment=PATH=/bin:/usr/bin:/usr/local/bin
WorkingDirectory=/home/user/service_script/

[Install]
WantedBy=multi-user.target
```

### Usage

**Create a ServiceHandler object**

```python
import servicehandler as sh

my_service = sh.ServiceHandler('MyService','my-service.service')
```

**Control the state of a service**

```python
# Check current state
my_service.state()
<ServiceState.STOPPED: 2>

# Start the service
> my_service.start()
MyService changed state to ServiceState.RUNNING
<Response.OK: 1>

# Try to start again the service
> my_service.start()
<Response.ALREADY: 2>

# Terminate the service
> my_service.stop()
MyService changed state to ServiceState.STOPPED
<Response.OK: 1>

# Kill the service
# In this specific case, the unit file was configured with restart=on-failure (automatic restart)
> my_service.kill()
<Response.OK: 1>
```

**Control the enablement_state of a service (whether it automatically starts on system startup)**

```python
# Check current enablement_state
> my_service.enablement_state()
<ServiceEnablementState.DISABLED: 2>

# Enable the service
> my_service.enable()
Created symlink /home/user/.config/systemd/user/multi-user.target.wants/my_service.service → /usr/lib/systemd/user/my_service.service.
MyService changed enablement state to ServiceEnablementState.ENABLED
<Response.OK: 1>

# Disable the service
> my_service.disable()
Removed /home/user/.config/systemd/user/multi-user.target.wants/my_service.service.
MyService changed enablement state to ServiceEnablementState.DISABLED
<Response.OK: 1>
```

**Iterate over different services and perform batch operations**

```python
import servicehandler as sh

service_A = sh.ServiceHandler('ServiceA','A-config-file.service')
service_B = sh.ServiceHandler('ServiceB','B-config-file.service')
service_C = sh.ServiceHandler('ServiceC','C-config-file.service')

services = [ServiceA, ServiceB, ServiceC]

# Iterate over the services easily
for srv in services:
    if srv.state() == sh.ServiceStatus.STOPPED:
        srv.restart()
    print(srv.state())
```

## Installation

### Install using pip

`servicehandler` is available on [PyPI](https://pypi.org/project/servicehandler/) and it can be installed using **pip**:

```
pip install servicehandler
```

### Build from source

As an alternative, it's possible to build and install the package from source:

```
git clone https://github.com/albertosantagostino/systemd-servicehandler
cd systemd-servicehandler
python3 setup.py install
```

## Development history and use cases

### Manage multiple services from a single entry-point

This package was developed while working on a Telegram bot ~~overlord~~ manager, created to handle other bots (and services) running on the same platform, providing a single point of access to the user

In the scenario multiple bots run on a headless Raspberry Pi Zero. In order to start them when needed, check their logs and interact with them without opening an SSH session every time, a brand new all-powerful Telegram bot was created, weaponized with this newly created package

## License

The package is distributed under the [MIT License](https://opensource.org/licenses/MIT)

