from .shell import run

SERIAL_NUMBER = None

async def load_serial_number():
    global SERIAL_NUMBER
    if not SERIAL_NUMBER:
        cmd = "cat /proc/cpuinfo | grep Serial | cut -d ' ' -f 2"
        (rval, stdout, stderr) = await run(cmd)
        if rval == 0:
            SERIAL_NUMBER = stdout.decode().strip()

    return SERIAL_NUMBER
