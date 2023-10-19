"""
https://man.archlinux.org/man/sway-ipc.7.en

Payload structure

    <magic-string> <payload-length> <payload-type> <payload>

    Where,
        <magic-string>   = "i3-ipc"
        <payload-length> = 32-bit integer in native byte order
        <payload-type>   = 32-bit integer in native byte order 
        <payload>        = The bytes containing the payload

"""
import json
import socket
import sys
import os
import enum
from typing import Any, Final, Optional

PAYLOAD_MAGIC_STRING:Final = b"i3-ipc"
SWAY_SOCK_ENV_VAR:Final = 'I3SOCK'
RESPONSE_BUFFER_SIZE:Final = 1024 * 100

class PayloadType(enum.Enum):
    RUN_COMMAND = 0
    GET_WORKSPACES = 1
    SUBSCRIBE = 2
    GET_OUTPUTS = 3
    GET_TREE = 4
    GET_MARKS = 5
    GET_BAR_CONFIG = 6
    GET_VERSION = 7
    GET_BINDING_MODES = 8
    GET_CONFIG = 9
    SEND_TICK = 10
    SYNC = 11
    GET_BINDING_STATE = 12
    GET_INPUTS = 100
    GET_SEATS = 101

class EventType(enum.Enum):
    workspace = 0x80000000
    mode = 0x80000002
    window = 0x80000003
    barconfig_update = 0x80000004
    binding = 0x80000005
    shutdown = 0x80000006
    tick = 0x80000007
    bar_state_update = 0x80000014
    input = 0x80000015

def get_socket_location() -> str:
    """Obtain the Sway socket location via the I3SOCK environment variable."""
    if SWAY_SOCK_ENV_VAR in os.environ:
        return os.environ[SWAY_SOCK_ENV_VAR]
    raise ValueError('No default socket location available. Is Sway installed and running?')

def get_ipc_socket(socket_location:Optional[str]=None) -> socket.socket:
    """Get a Sway IPC socket."""
    if socket_location is None:
        socket_location = get_socket_location()
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.connect(socket_location)
    return s

def serialize_message(payload_type:PayloadType, payload:str|bytes) -> bytes:
    """Take a payload type and payload body, and serialize it into a series of bytes in the expected format."""
    if isinstance(payload, str):
        payload = payload.encode('utf-8')
    result:list[bytes] = []
    result.append(PAYLOAD_MAGIC_STRING)
    result.append(len(payload).to_bytes(4, byteorder=sys.byteorder))
    result.append(payload_type.value.to_bytes(4, byteorder=sys.byteorder))
    result.append(payload)
    return b"".join(result)

def deserialize_message(payload:bytes) -> tuple[PayloadType|EventType, Any, bytes]:
    """Take a message recieved from the IPC socket, and parse it into a `Payload` object."""
    if not payload.startswith(PAYLOAD_MAGIC_STRING):
        raise Exception("Payload contents does not begin with magic string.")
    payload = payload[len(PAYLOAD_MAGIC_STRING):]
    payload_length = int.from_bytes(payload[:4], byteorder=sys.byteorder)
    payload_type_id = int.from_bytes(payload[4:8], byteorder=sys.byteorder)
    if payload_type_id > 101:
        payload_type = EventType(payload_type_id)
    else:
        payload_type = PayloadType(payload_type_id)
    current_payload = payload[8:8+payload_length]
    return payload_type, json.loads(current_payload.decode('utf-8')), payload[8+payload_length:]

def send_ipc_message(ptype: PayloadType, payload:Any="") -> Any:
    """Send a message to the Sway IPC consisting of the given payload type and message."""
    with get_ipc_socket() as s:
        s.send(serialize_message(ptype, payload))
        buffer = s.recv(RESPONSE_BUFFER_SIZE)
        mtype, message, remaining = deserialize_message(buffer)
        if mtype != ptype:
            raise Exception(f"IPC response type {mtype} does not match sent type {ptype}")
        if len(remaining) > 0:
            raise Exception(f"There should not be any buffer remainder from standard IPC responses. r={repr(remaining)}")
        return message
