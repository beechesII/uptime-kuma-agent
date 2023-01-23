#!/usr/bin/env python3
"""
A script to run monitoring checks on a system and
push the result to uptime-kuma instance.
"""

from argparse import ArgumentParser
import sys
import logging
import shlex
import subprocess
import requests
import yaml

def create_parser():
    """
    create a parser with ArgumentParser to parse arguments
    """
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

def load_configuration(config_file):
    """
    load the configuration file
    """
    try:
        with open(config_file, 'r', encoding = 'utf-8') as file:
            try:
                configuration = yaml.safe_load(file)
            except yaml.scanner.ScannerError:
                logging.error("Cant't read yml file")
                sys.exit(2)
    except OSError as err:
        logging.error("%s", err)
        sys.exit(2)
    return configuration

def execute_check(chk):
    """
    execute a configuration given check and return a message
    and a status as result
    """
    with subprocess.Popen(
            shlex.split(chk),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        ) as process:
        out, err = process.communicate()
    if process.returncode == 0:
        if 'nagios' in chk:
            mes = out.decode('utf-8').split('|', maxsplit = 1)[0].replace(' ','+').replace(';','') # pylint: disable=line-too-long
            sta = 'up'
        else:
            mes = out.decode('utf-8')
            sta = 'up'
    if process.returncode >= 1 and process.returncode <= 3:
        if 'nagios' in chk:
            mes = out.decode('utf-8').split('|', maxsplit = 1)[0].replace(' ','+').replace(';','') # pylint: disable=line-too-long
            sta = 'down'
        else:
            mes = out.decode('utf-8')
            sta = 'down'
    if process.returncode >= 3:
        logging.error("%s", out.decode('utf-8'))
        logging.error("%s", err.decode('utf-8'))
        mes = 'UNKNOWN'
        sta = 'down'
    return mes, sta

def push_event(msg, status, token, url):
    """
    push event to uptime-kuma monitoring instance
    """
    url = 'https://' + url + '/api/push/' + token + '?status=' + status + '&msg=' + msg
    try:
        requests.get(url, timeout=10)
    except TimeoutError:
        logging.error("Timeout for url: %s", url)
    except ConnectionError:
        logging.error("Can't connect to url: %s", url)

config = load_configuration(config_file=args.config_file)

for check in config['checks']:
    message, state = execute_check(chk = check['command'])
    push_event(
        msg = message,
        status = state,
        token = check['token'],
        url = config['url']
    )
