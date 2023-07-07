import asyncio
import re
import logging
from potnanny.utils.shell import run

logger = logging.getLogger(__name__)
DEFAULT_PATH = "/etc/wpa_supplicant/wpa_supplicant.conf"
DEFAULT_SOCK = "/var/run/wpa_supplicant"


async def current_wifi():
    """
    get name of currently connected wifi
    """

    cmd = 'sudo iwgetid -r'
    try:
        rval, stdout, stderr = await run(cmd);
        if rval == 0:
            network = stdout.decode().strip()
            return network
    except:
        logger.warning(f"unexpected error: {stderr.decode().strip()}")
        pass

    return None


async def wifi_networks() -> list:
    """
    Scan for wifi network info. returns a list of dicts
    """

    results = []
    current = await current_wifi()
    cmd = 'sudo iwlist wlan0 scan'

    try:
        rval, stdout,stderr = await run(cmd)
        if rval != 0:
            logger.warning(f"unexpected error: {stderr.decode().strip()}")
            return []

        raw = stdout.decode().strip()
        results = parse_wifi_results(raw)
        for r in results:
            if 'essid' in r and r['essid'] == current:
                r['in_use'] = True
    except Exception as x:
        logger.warning(str(x))

    return results


async def wpa_networks() -> dict:
    """
    Get wpa supplicant known network data as dict: {id: ssid, ...}
    """

    data = {}
    cmd = "wpa_cli list_networks"
    try:
        rval, stdout, stderr = await run(cmd)
        if proc.returncode != 0:
            logger.warning(stderr.decode().strip())
            return {}

        for line in stdout.decode().splitlines():
            if re.search(r'^(Selected interface|network id)', line):
                continue
            if re.search(r'^\s*$', line):
                continue

            atoms = line.split()
            if len(atoms) >= 2:
                data[atoms[0]] = atoms[1]
    except:
        pass

    return data


async def wpa_drop_network(ssid: str) -> tuple:
    """
    Removed named network from the wpa config
    returns tuple(exit-code, message)
    """

    target = None
    data = await wpa_networks()
    for k,v in data.items():
        if v == ssid:
            target = k
            break

    if target is None:
        return (1, f"network ssid {ssid} not found")

    cmd = f"sudo wpa_cli remove_network {target}"
    try:
        rval, stdout, stderr = await run(cmd)
        if rval != 0:
            logger.warning(stderr.decode())
            return (rval, f"unexpected error: {stderr.decode()}")
    except:
        pass

    return (0, "ok")


async def wpa_password_entry(ssid: str, pw: str) -> str:
    """
    Generate a network entry for wpa_supplicant.conf, from the SSID/password
    """

    cmd = f"wpa_passphrase {ssid} {pw}"
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)

    stdout, stderr = await proc.communicate()
    if proc.returncode != 0:
        logger.warning(stderr.decode())
        return ""

    atoms = stdout.decode().split("\n")

    # the priority above zero is important, for the way potnanny is working
    # with wpa, and the auto AP hotspot function.
    atoms.insert(-3, "\tpriority=10")

    # join to str, but omit the plain text passwd from the output
    return "\n".join([a for a in atoms if not a.startswith("\t#")]).strip()


async def append_to_wpaconf(entry: str, path: str = DEFAULT_PATH):
    """
    Append a network entry block to the wpa_supplicant.conf file
    """

    cmd = f'printf "\n{entry}\n" | sudo tee -a {path}'
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)

    stdout, stderr = await proc.communicate()
    if proc.returncode != 0:
        logger.warning(stderr.decode())
        return (proc.returncode, "unexpected error: {stderr.decode()}")

    return (0, "ok")


def parse_wifi_results(txt: str) -> list:
    results = {}
    bufr = []
    for line in txt.splitlines():
        if re.search(r'Cell \d+', line):
            if bufr:
                cell = extract_network_data(bufr)
                if cell and 'essid' in cell:
                    results[cell['essid']] = cell
                bufr = []
        bufr.append(line)

    # last check of the remaining buffer
    if bufr:
        cell = extract_network_data(bufr)
        if cell and 'essid' in cell:
            results[cell['essid']] = cell

    return list(results.values())


def extract_network_data(bufr: list) -> dict:
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
