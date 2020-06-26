# Systemd service handler (servicehandler)

**servicehandler** is a Python library that provides an orchestrator for systemd services. It abstracts services as objects and implements helper methods, wrapping the `systemctl` command

Using this package does **not** require root permissions, as the service manager used is the one of the current user (the service configuration files are in `/usr/lib/systemd/user/`)

## Description

The first thing to handle services is to create a **service unit file** (under `/usr/lib/systemd/user/my-service.service`) like the following:

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

Depending on how you created the service file you may need to provide access to the user through `sudo chmod 644 my-service.service`

### Usage

**Control the state of a service**

```python
import servicehandler as sh

# Create a new service handler
my_service = sh.ServiceHandler('MyService','my-service.service')

# Check current state
my_service.state
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
**Control the enablement_state of a service (whether it starts automatically on system startup)**

```python
# Check current enablement_state
> my_service.enablement_state
<ServiceEnablementState.DISABLED: 2>

# Enable the service
> my_service.enable()
Created symlink /home/user/.config/systemd/user/multi-user.target.wants/my_service.service → /usr/lib/systemd/user/my_service.service.
<Response.OK: 1>
MyService changed enablement state to ServiceEnablementState.ENABLED

# Disable the service
> my_service.disable()
Removed /home/user/.config/systemd/user/multi-user.target.wants/my_service.service.
<Response.OK: 1>
MyService changed enablement state to ServiceEnablementState.DISABLED
```

**Iterate over different services and perform batch operations**

```python
import servicehandler as sh

service_A = sh.ServiceHandler('ServiceA','A-config-file.service')
service_B = sh.ServiceHandler('ServiceB','B-config-file.service')
service_C = sh.ServiceHandler('ServiceC','C-config-file.service')

services = [ServiceA, ServiceB, ServiceC]

# Iterate over the services easily
for sr in services:
    if sr.state == sh.ServiceStatus.STOPPED:
        sr.restart()
    print(sr)
```

## Installation

To build and install the package from source:

```
git clone https://github.com/albertosantagostino/systemd-servicehandler
cd systemd-servicehandler
python3 setup.py install
```

*WIP: Soon on pypi*

## Development history and use cases

### Manage multiple services from a single entry-point

This library was developed while working on a Telegram bot ~~overlord~~ manager, used to handle other bots (and services) running on the same platform, providing a single point of access to the user

In this scenario multiple bots run on a headless Raspberry Pi Zero. In order to start them when needed, check their logs and interact with them without opening an SSH session every time, a brand new all-powerful Telegram bot was created, weaponized with this new package, **servicehandler**

## License

The package is distributed under the [MIT License](https://opensource.org/licenses/MIT)

