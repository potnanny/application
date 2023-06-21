import asyncio
import re

async def wifi_networks():
    cmd = 'sudo iwlist wlan0 scan'
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)

    stdout, stderr = await proc.communicate()
    if proc.returncode != 0:
        pass

    results = parse_wifi_results(stdout)
    return results


def parse_wifi_results(raw):
    txt = raw.decode()
    results = []
    bufr = []
    for line in txt.splitlines():
        if re.search(r'Cell \d+', line):
            if bufr:
                cell = extract_network_data(bufr)
                if cell:
                    results.append(cell)
                bufr = []
        bufr.append(line)

    # last check of the remaining buffer
    if bufr:
        cell = extract_network_data(bufr)
        if cell:
            results.append(cell)

    return results


def extract_network_data(bufr: list):
    lookups = {
        'address': re.compile(r'Cell \d+ - Address: (\S+)'),
        'channel': re.compile(r'Channel:(\d+)'),
        'essid': re.compile(r'ESSID:\"(\S+)\"'),
        'quality': re.compile(r'Quality=(\d+/\d+)'),
        'signal': re.compile(r'Signal level=(-\d+ dBm)'),
        'ieee': re.compile(r'IE: (IEEE.+)'),
        'authentication': re.compile(r'Authentication Suites \(\d+\) : (.+)'),
        'mode': re.compile(r'Mode:(.+)'),
        'encryption': re.compile(r'Encryption key:(.+)'),
    }
    results = {}
    for line in bufr:
        for key, regex in lookups.items():
            match = regex.search(line)
            if match:
                results[key] = match.group(1).strip()

    return results
