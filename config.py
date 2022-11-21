from os import environ

# Tuple of (MAJOR, MINOR) minimum plugin version
REQUIRED_VERSION = (1, 0)

# TCP port for streaming events to clients
TCP_LISTEN_PORT = 6600

# HTTP port for the client API
HTTP_LISTEN_PORT = 8080

# Use the MOTD to uniquely identify a server instance
USER_AGENT = "Bingoserver " + environ.get("USERAGENT_MOTD", "(Development)")

# Developer Restricted API key
SECRET_KEY = environ.get("SECRET_KEY", "")

# Maximum number of teams per room. Don't set this higher than available colors in GameTeam.
MAX_ROOM_TEAM_COUNT = 6