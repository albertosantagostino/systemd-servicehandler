# Service (systemd) configuration

**Path**: `usr/lib/systemd/user`
**Permissions**: `sudo chmod 644 bot-weather-dude.service`

```ini
[Unit]
Description=WeatherDude

[Service]
ExecStart=/usr/bin/python3 /home/qxu5978/shared/telegram-bots/WeatherDude-telegram-bot/src/main.py
Environment=PATH=/bin:/usr/bin:/usr/local/bin
WorkingDirectory=/home/qxu5978/shared/telegram-bots/WeatherDude-telegram-bot/
StandardOutput=inherit
StandardError=inherit

[Install]
WantedBy=multi-user.target
```

### Execution

```bash
systemctl --user daemon-reload
systemctl --user start bot-weather-dude.service
systemctl --user status bot-weather-dude.service
systemctl --user stop bot-weather-dude.service
```

