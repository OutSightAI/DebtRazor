import docker
import asyncio
from typing import Optional, Dict, Tuple
import logging
import concurrent.futures

# Configure logging
logging.basicConfig(level=logging.INFO)

class DockerExecutor:
    def __init__(self, max_workers: int = 20):
        self.client = docker.from_env()
        self.loop = asyncio.get_event_loop()
        self.api_client = docker.APIClient()
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        self.loop.set_default_executor(self.executor)

    async def start_container(self, image_name: str, volumes: Optional[Dict[str, Dict[str, str]]] = None) -> Optional[docker.models.containers.Container]:
        """
        Start a Docker container asynchronously with optional volume bindings.
        """
        try:
            container = await self.loop.run_in_executor(None, lambda: self.client.containers.run(
                image_name,
                detach=True,
                tty=True,
                stdin_open=True,
                volumes=volumes,
                mem_limit='512m',
                cpu_quota=50000
            ))
            logging.info(f"Container {container.id} started with volumes: {volumes}")
            return container
        except docker.errors.APIError as e:
            logging.error(f"Error starting container: {e}", exc_info=True)
            return None

    async def stop_and_remove_container(self, container: docker.models.containers.Container) -> None:
        """
        Stop and remove a Docker container asynchronously.
        """
        try:
            if container.status == 'running' or container.status == 'created':
                await self.loop.run_in_executor(None, container.stop)
            await self.loop.run_in_executor(None, container.remove)
            logging.info(f"Container {container.id} stopped and removed.")
        except docker.errors.NotFound:
            logging.warning(f"Container {container.id} not found.")
        except docker.errors.APIError as e:
            logging.error(f"Error stopping/removing container {container.id}: {e}", exc_info=True)

    async def execute_command(self, container: docker.models.containers.Container, command: str, timeout: int = 60) -> Optional[Tuple[int, str]]:
        """
        Execute a stateless command inside the container using Docker exec_run with a timeout.
        """
        try:
            exec_output = await self.loop.run_in_executor(None, lambda: container.exec_run(command))
            exit_code, output = exec_output
            return exit_code, output.decode('utf-8', errors='replace')
        except docker.errors.NotFound:
            logging.error(f"Container {container.id} not found.")
            return None
        except docker.errors.APIError as e:
            logging.error(f"Error executing command in container {container.id}: {e}", exc_info=True)
            return None

    # async def attach_to_container(self, container: docker.models.containers.Container) -> Optional[docker.models.containers.Container]:
    #     """
    #     Attach to a running container for persistent interaction.
    #     """
    #     try:
    #         stream = await self.loop.run_in_executor(None, lambda: container.attach(stream=True, stdout=True, stderr=True, logs=True))
    #         logging.info(f"Attached to container {container.id}.")
    #         return stream
    #     except docker.errors.NotFound:
    #         logging.error(f"Container {container.id} not found.")
    #         return None
    #     except docker.errors.APIError as e:
    #         logging.error(f"Error attaching to container {container.id}: {e}", exc_info=True)
    #         return None

    # async def exec_persistent_command(self, stream, command: str) -> None:
    #     """
    #     Send a command to the attached container session.
    #     This allows for persistent interaction with the container, maintaining context between commands.
    #     """
    #     try:
    #         # Send the command to the container via the stream
    #         await self.loop.run_in_executor(None, lambda: stream.stdin.write(command.encode('utf-8') + b'\n'))
    #         await self.loop.run_in_executor(None, stream.stdin.flush)
    #         logging.info(f"Executed persistent command: {command}")
    #     except Exception as e:
    #         logging.error(f"Error writing command to attached stream: {e}", exc_info=True)

    


# Example usage
async def main():
    executor = DockerExecutor()

    # Define volume mapping
    volumes = {
        '/Users/agokrani/Documents/git/GPT-Migrate/results/target/703e9d0b-3518-4f1c-bff7-c1314d214ad9/grocery_app': {'bind': '/app', 'mode': 'rw'}
    }

    # Start a container with volume mapping
    container = await executor.start_container("python:3.9-slim", volumes=volumes)

    if container:
        # Execute a stateless command using exec_run
        result = await executor.execute_command(container, "python /app/Python/app.py")
        if result:
            exit_code, output = result
            logging.info(f"Exec_run Exit Code: {exit_code}")
            logging.info(f"Exec_run Output: {output}")

        # Attach to the container for a persistent session
        # stream = await executor.attach_to_container(container)
       
        # if stream:
        #     # Send persistent commands
        #     await executor.exec_persistent_command(stream, "echo 'Hello from persistent shell'")
        #     # Further commands can be sent to the same stream
        
        # Stop and remove the container
        await executor.stop_and_remove_container(container)

if __name__ == "__main__":
    asyncio.run(main())