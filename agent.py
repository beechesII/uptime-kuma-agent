#!/usr/bin/env python3

from argparse import ArgumentParser
import logging
import shlex, subprocess
import requests
import yaml
import sys

def create_parser():
    parser = ArgumentParser()
    parser.add_argument(
        '-c','--config-file',
        help="configuration file for agent",
        dest="config_file",
        required=True
    )
    return parser

args = create_parser().parse_args()

logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%d/%m/%y %H:%M:%S",
)

def execute_check(check):
    p = subprocess.Popen(
            shlex.split(check),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    out, err = p.communicate()
    if p.returncode == 0:
        if 'nagios' in check:
            msg = out.decode('utf-8').split('|')[0].replace(' ','+').replace(';','')
            status = 'up'
        else:
            msg = out.decode('utf-8')
            status = 'up'
    if p.returncode >= 1 and p.returncode <= 3:
        if 'nagios' in check:
            msg = out.decode('utf-8').split('|')[0].replace(' ','+').replace(';','')
            status = 'down'
        else:
            msg = out.decode('utf-8')
            status = 'down'
    if p.returncode >= 3:
        logging.error(f"{out.decode('utf-8')}")
        msg = 'UNKNOWN'
        status = 'down'
    return msg, status

def push_notification(msg, status, token, url):
    url = 'https://' + url + '/api/push/' + token + '?status=' + status + '&msg=' + msg
    try:
        requests.get(url, timeout=10)
    except TimeoutError:
        logging.error(f"Timeout for url: {url}")
    except ConnectionError:
        logging.error(f"Can't connect to url: {url}")

def load_configuration(config_file):
    try:
        with open(config_file, 'r') as f:
            try:
                config = yaml.safe_load(f)
            except yaml.scanner.ScannerError:
                logging.error(f"Cant't read yml file")
                sys.exit(2)
    except OSError as err:
        logging.error(f"{err}")
        sys.exit(2)
    return config

config = load_configuration(config_file=args.config_file)

for check in config['checks']:
    msg, status = execute_check(check = check['command'])
    push_notification(
        msg = msg,
        status = status,
        token = check['token'],
        url = config['url']
    )
