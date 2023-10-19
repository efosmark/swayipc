import json
from typing import Any, Optional, Sequence, overload
from .event import EVENT_TYPE_TO_EVENT
from .ipc import send_ipc_message, PayloadType, EventType, get_ipc_socket, serialize_message, deserialize_message, PAYLOAD_MAGIC_STRING, RESPONSE_BUFFER_SIZE
from .model import CommandResult, Gaps, BarConfig, Version, LibInput, Input, Seat, Hinting,\
                   BorderStyle, LayoutType, Orientation, X11Window, Rect, NodeType, Workspace,\
                   OutputMode, OutputTransform, Output, RootNode, WorkspaceNode, ContainerNode, \
                   ViewNode, X11ViewNode, OutputNode

def run_command(command:str) -> list[CommandResult]:
    result = send_ipc_message(
            PayloadType.RUN_COMMAND, 
            command
        )
    return [CommandResult.from_dict(r) for r in result]

def get_workspaces() -> list[Workspace]:
    result = send_ipc_message(PayloadType.GET_WORKSPACES)
    return [Workspace.from_dict(op) for op in result]

def subscribe(events:Sequence[EventType]):
    """ Subscribe to the given sequence of events.
    
    This function returns a generator that yields each message recieved from the IPC socket.
    """
    with get_ipc_socket() as s:
        s.send(serialize_message(PayloadType.SUBSCRIBE, json.dumps([e.name for e in events])))
        buffer = b""
        while True:
            buffer += s.recv(RESPONSE_BUFFER_SIZE)
            while PAYLOAD_MAGIC_STRING in buffer:
                mtype, message, buffer = deserialize_message(buffer)
                if mtype == PayloadType.SUBSCRIBE: continue
                if not isinstance(mtype, EventType):
                    raise TypeError(f"The payload type of a subscribe response is not an event. mtype={mtype}")
                yield EVENT_TYPE_TO_EVENT[mtype].from_dict(message)

def get_outputs() -> list[Output]:
    result = send_ipc_message(PayloadType.GET_OUTPUTS)
    return [Output.from_dict(op) for op in result]

def get_tree() -> RootNode:
    return RootNode.from_dict(send_ipc_message(PayloadType.GET_TREE))

def get_marks() -> list[str]:
    return send_ipc_message(PayloadType.GET_MARKS)

@overload
def get_bar_config() -> list[str]:...
@overload
def get_bar_config(bar_id:str) -> BarConfig:...
def get_bar_config(bar_id:Optional[str]=None) -> Any:
    if bar_id is None:
        return send_ipc_message(PayloadType.GET_BAR_CONFIG)
    return BarConfig.from_dict(send_ipc_message(PayloadType.GET_BAR_CONFIG, bar_id))

def get_version() -> Version:
    return send_ipc_message(PayloadType.GET_VERSION)

def get_binding_modes() -> list[str]:
    return send_ipc_message(PayloadType.GET_BINDING_MODES)

def get_config() -> str:
    return send_ipc_message(PayloadType.GET_CONFIG)["config"]

def send_tick(payload:str="") -> bool:
    return send_ipc_message(PayloadType.SEND_TICK, payload)["success"]

def sync() -> bool:
    return send_ipc_message(PayloadType.SYNC)["success"]

def get_binding_state() -> str:
    return send_ipc_message(PayloadType.GET_BINDING_STATE)

def get_inputs() -> list[Input]:
    return [
        Input.from_dict(op)
        for op in send_ipc_message(PayloadType.GET_INPUTS)
    ]

def get_seats() -> list[Seat]:
    return [Seat.from_dict(op) for op in send_ipc_message(PayloadType.GET_SEATS)]

__ALL__ = [
    "run_command", "get_workspaces", "subscribe", "get_outputs", "get_tree", "get_marks",
    "get_bar_config", "get_version", "get_binding_modes", "get_config", "send_tick", "sync", 
    "get_binding_state", "get_inputs", "get_seats", 
    
    "CommandResult", "Gaps", "BarConfig", "Version", "LibInput", "Input", "Seat", "Hinting",
    "BorderStyle", "LayoutType", "Orientation", "X11Window", "Rect", "NodeType", "Workspace",
    "OutputMode", "OutputTransform", "Output", "RootNode", "WorkspaceNode", "ContainerNode", 
    "ViewNode", "X11ViewNode", "OutputNode"
]
