# uptime-kuma-agent

This python script is an agent for [uptime-kuma](https://github.com/louislam/uptime-kuma). It uses the push monitor to create monitoring events.

You can use nagios-plugins or self written checks to monitor your systems.

Feel free to [contribute](CONTRIBUTING.md).

## Requirements

* python3

## Installation

Install python3 and some nagios-plugins on Rocky Linux 8:

```bash
dnf install -y python3 nagios-plugins-uptime nagios-plugins-ssh nagios-plugins-disk nagios-plugins-load nagios-plugins-log nagios-plugins-users nagios-plugins-procs
```

Example configuration.yml:
```yaml
---
url: uptime-kuma.example.com
checks:
  - command: '/usr/lib64/nagios/plugins/check_disk -w 20% -c 10% -p / -p /home -p /var -p /var/log'
    token: 'E0yTZWLuZJ'
  - command: '/usr/lib64/nagios/plugins/check_uptime'
    token: 'w5cC95KjLF'
```

Note: Configure the URL without `https://` protocol in front of your domain. Otherwise you will receive a connection error.

Download and install agent.py:
```bash
curl -s https://raw.githubusercontent.com/beechesII/uptime-kuma-agent/main/agent.py -o ~/agent.py
chmod +x ~/agent.py
```

Configure cronjob:
```bash
*/5 * * * * ~/agent.py -c ~/configuration.yml
```

## License

GPLv3
