# Bingoserver Communication Protocol
The Bingo server (Python server) communicates to Bingo clients (Openplanet plugins) via a TCP connection using a websocket-like protocol detailed below.

## Frame Description
A message frame begins with an 8-bit opcode describing the message, followed in most cases with a 16-bit [Message ID](#message-ids) and a 16-bit unsigned integer representing the payload length. The next N bytes are the message payload.

Opcode | Description | Sent by
---|---|---
0x00 | Noop. This must be ignored, and this message does not contrain any payload. | Client/Server
0x01 | Identification. Sent during the [connection handshake](#connection-handshake). | Client
0x02 | Ready. The connection has been established. The payload contains a secret token to execute authenticated requests. | Server
0x03 | Ping. A regular connection test message. It expects an empty acknowledgement reply. | Server
0x04 | Request. A message expecting a reply. The payload is used to determine the request body. | Client/Server
0x05 | Reply. Sent in response to a message. The start of the payload contains the [Message ID](#message-ids) of the replied message. If the payload length is 2 bytes, this message has no other payload and signifies an acknowledgement. | Client/Server
0x06 | Error Reply. A reponse indicating an error. The payload contains a message to display to the client. If sent by client, payload must be empty. | Client/Server
0x07 | Protocol Error. The connection will close because the protocol is violated. | Client/Server
0x08 | Event. A message is sent but is not expecting a reply. Often this is a game-related event sent by the server. | Client/Server
0x09 | Data Update. An authoritative message to sync network variables between the peers. The client must immediately take into account the new values contained in the payload. | Server

## Message IDs
Message IDs are a unique identifier for each message sent on the network. Client message IDs start at `0` and server message IDs have their most significant bit set to `1`, meaning they start at `0x8000`.

## Connection Handshake
A client can open a TCP connection to the server's open TCP port to initialize a connection.

After the client successfully connects, it must send an identification message with opcode `0x01` and this JSON payload:

```json
{
    "login": "", // Ubisoft Login,
    "username": "" // Username
}
```

TODO