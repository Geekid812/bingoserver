from os import environ

# Use the MOTD to uniquely identify a server instance
USER_AGENT = "Bingoserver " + environ.get("USERAGENT_MOTD", "(Development)")
