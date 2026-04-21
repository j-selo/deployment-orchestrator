import asyncio


async def helm_rollback(release_name: str, namespace: str) -> str:
    process = await asyncio.create_subprocess_exec(
        "helm",
        "rollback",
        release_name,
        "--namespace",
        namespace,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        error_output = stderr.decode().strip()
        raise RuntimeError(f"Helm rollback failed for {release_name}: {error_output}")

    return stdout.decode().strip()