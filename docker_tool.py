from typing import Any, Dict, List
import docker


def docker_list_containers() -> List[Dict[str, Any]]:
    """
    Return a list of running containers with id, name, image, status.

    Requires docker SDK and Docker Engine accessible by environment (socket/daemon).
    """
    client = docker.from_env()
    containers = []
    for c in client.containers.list():
        containers.append({"id": c.id, "name": c.name, "image": getattr(c, "image").tags, "status": c.status})
    return containers


def docker_container_logs(container_id: str, tail: int = 200) -> str:
    """
    Get last `tail` lines of container logs.

    Args:
        container_id: Container ID or name.
        tail: Number of tail lines.

    Returns:
        String logs (may be large).
    """
    client = docker.from_env()
    c = client.containers.get(container_id)
    return c.logs(tail=tail).decode("utf-8", errors="replace")


@mcp.tool()
def docker_tool(action: str, container: str = "", tail: int = 200) -> Dict[str, Any]:
    """
    Docker control (read-only) tool.

    Actions:
        - list: list running containers
        - logs: fetch container logs (container argument required)

    Returns:
        Dict with results or error message.

    Security note:
        This tool requires that the MCP server can access the Docker daemon. It does not perform destructive operations.
    """
    action = action.lower()
    if action == "list":
        return {"containers": docker_list_containers()}
    if action == "logs":
        if not container:
            raise ValueError("container argument is required for logs action.")
        return {"logs": docker_container_logs(container, tail=tail)}
    raise ValueError("Unsupported docker action. Use 'list' or 'logs'.")
