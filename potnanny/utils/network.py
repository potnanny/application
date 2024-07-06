import re
from .shell import run

LOCAL_ADDRESS = None

async def load_local_address():
    global LOCAL_ADDRESS

    if not LOCAL_ADDRESS:
        in_block = False
        cmd = "ifconfig -a"
        (rval, stdout, stderr) = await run(cmd)
        if rval == 0:
            for line in stdout.splitlines():
                match = re.search(r'inet (\d+\.\d+\.\d+\.\d+)', line)
                if match and match.group(1) != '127.0.0.1':
                    LOCAL_ADDRESS = match.group(1)
                    break

    return LOCAL_ADDRESS
