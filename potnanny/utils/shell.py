import asyncio

async def run(cmd: str):
    """
    Async run shell command
    args:
        command string
    returns:
        tuple (stdout, stderr)
    """

    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)

    stdout, stderr = await proc.communicate()
    return (stdout, stderr)
