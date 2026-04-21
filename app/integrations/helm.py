import subprocess
import cmd

async def helm_deploy(release_name, chart_path, namespace):
    try:
        # Run the helm upgrade command
        result = subprocess.run(
            [
                "helm", "upgrade", "--install", release_name,
                chart_path, "--namespace", namespace
            ],
        )
        print(f"Helm deploy successful: {result.stdout.decode()}")
    except subprocess.CalledProcessError as e:
        print(f"Helm deploy failed: {e.stderr.decode()}")
        raise Exception("Helm deployment failed")
    
    subprocess.run(cmd, check=True)