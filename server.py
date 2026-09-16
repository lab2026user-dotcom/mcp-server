import ssl
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

from mcp.server import MCPServer

mcp = MCPServer("Enterprise AI Platform MCP")


def http_check(
    name: str,
    url: str,
    verify_tls: bool = True,
    timeout: int = 5,
) -> dict:
    try:
        context = None if verify_tls else ssl._create_unverified_context()

        request = Request(url, method="GET")

        with urlopen(request, timeout=timeout, context=context) as response:
            body = response.read().decode("utf-8", errors="replace").strip()

            return {
                "status": "healthy",
                "http_status": response.status,
                "endpoint": url,
                "response": body[:500],
            }

    except HTTPError as exc:
        return {
            "status": "reachable",
            "http_status": exc.code,
            "endpoint": url,
            "note": "HTTP endpoint reachable but returned an error status",
        }

    except (URLError, TimeoutError, OSError) as exc:
        return {
            "status": "unhealthy",
            "endpoint": url,
            "error": str(exc),
        }

    except Exception as exc:
        return {
            "status": "unhealthy",
            "endpoint": url,
            "error": str(exc),
        }


@mcp.tool()
def get_platform_status() -> dict:
    """Check the health and reachability of Enterprise AI Platform components."""

    components = {
        "langgraph": http_check(
            "langgraph",
            "http://langgraph-api.lab.local/health",
        ),
        "n8n": http_check(
            "n8n",
            "http://n8n.lab.local/healthz",
        ),
        "ollama": http_check(
            "ollama",
            "http://10.10.10.11:11434/api/tags",
        ),
        "qdrant": http_check(
            "qdrant",
            "https://192.168.5.13:6333/healthz",
            verify_tls=False,
        ),
        "litellm": http_check(
            "litellm",
            "http://litellm.lab.local/health",
        ),
    }

    return {
        "platform": "Enterprise AI Lab",
        "status": (
            "healthy"
            if all(
                component["status"] in {"healthy", "reachable"}
                for component in components.values()
            )
            else "degraded"
        ),
        "components": components,
        "note": "LangChain health is validated inside Kubernetes and will be added when this MCP server runs in-cluster.",
    }


if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=8000,
    )
