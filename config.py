from os import environ

# Tuple of (MAJOR, MINOR) minimum plugin version
REQUIRED_VERSION = (1, 1)

# TCP port for streaming events to clients
TCP_LISTEN_PORT = 6600

# HTTP port for the client API
HTTP_LISTEN_PORT = 8080

# Reconnection Timeout (in seconds)
RECONNECT_TIMEOUT = 120

# Use the MOTD to uniquely identify a server instance
USER_AGENT = "Bingoserver " + environ.get("USERAGENT_MOTD", "(Development)")

# Developer Restricted API key
SECRET_KEY = environ.get("SECRET_KEY", "")
