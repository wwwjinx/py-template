import socket


def get_ip_address() -> str:
    """Best-effort LAN IPv4 (like koa getIpAddress). Falls back to 127.0.0.1."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
