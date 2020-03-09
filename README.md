# Systemd service handler (servicehandler)

**servicehandler** is an orchestrator for systemd services, distributed as Python package. It abstracts services as objects and provides helper methods, wrapping the `systemctl` command

Using the module does not require root permissions, as the service manager used is the one of the calling user (the service configuration files are in `/usr/lib/systemd/user/`)

## Usage and features

**Sample system file** (located under `/usr/lib/systemd/user/my-service.service`)

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

**Access and control easily the service through servicehandler**

```python
import servicehandler as sh

# Create a new service handler providing a name and the configuration file
MyService = sh.ServiceHandler('My service','my-service.service')

# Start the service
MyService.start()

# Check the status
MyService.status()
> <ServiceState.RUNNING: 1>
    
# Terminate the service
MyService.stop()

# Force kill the service
MyService.kill()
```

**Iterate over different services and perform batch operations**

```python
import servicehandler as sh

ServiceA = sh.ServiceHandler('A service','A-config-file.service')
ServiceB = sh.ServiceHandler('B service','B-config-file.service')
ServiceC = sh.ServiceHandler('C service','C-config-file.service')

services = [ServiceA, ServiceB, ServiceC]

# Iterate over the services easily
for sr in services:
    if sr.state == sh.ServiceStatus.STOPPED:
        sr.restart()
    print(sr)
```

## Installation

To install the package building it from source, run:

```bash
git clone https://github.com/albertosantagostino/systemd-servicehandler
cd systemd-servicehandler
python3 setup.py install
```

*WIP: Soon on pypi*

## Development history and use cases

### Manage multiple services from a single entry-point

The package was born while developing a Telegram bot ~~overlord~~ manager, to handle other bots (and services) running on the same platform, providing a single point of access to the user

More specifically, 4 different telegram bots (developed with the [python-telegram-bot](https://python-telegram-bot.org) library) were running on a headless Raspberry Pi Zero. In order to start them when needed, check their logs and provide an easy way to handle them without SSHing into the RPi every time, a new all-powerful Telegram bot was created, armed with the newly created package **servicehandler**

## License

The package is distributed under the [MIT License](https://opensource.org/licenses/MIT)

