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
from abc import ABCMeta
import json
import socket
import sys
import os
import enum
from typing import Any, Final, Optional, Self, Set, cast, overload

from .loadable import Loadable

SCRATCHPAD_OUTPUT_NAME = "__i3_scratch"
PAYLOAD_MAGIC_STRING:Final = b"i3-ipc"
SWAY_SOCK_ENV_VAR:Final = 'I3SOCK'
RESPONSE_BUFFER_SIZE:Final = 1024 * 100
EVT_OFFSET = 0x80000000

class MessageType(enum.Enum):
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
    EVT_WORKSPACE = EVT_OFFSET
    EVT_MODE = EVT_OFFSET | 2
    EVT_WINDOW = EVT_OFFSET | 3
    EVT_BARCONFIG = EVT_OFFSET | 4
    EVT_BINDING = EVT_OFFSET | 5
    EVT_SHUTDOWN = EVT_OFFSET | 6
    EVT_TICK = EVT_OFFSET | 7
    EVT_BAR_STATE = EVT_OFFSET | 14
    EVT_INPUT = EVT_OFFSET | 15
     
    def is_event(self) -> bool:
        return self.value >= EVT_OFFSET
    
    @classmethod
    def all_events(cls) -> list['MessageType']:
        return [x for x in cls if x.is_event()]
    
    def subfield(self:'MessageType') -> str|None:
        return {
            self.EVT_WORKSPACE: 'workspace',
            self.EVT_MODE: 'mode',
            self.EVT_WINDOW: 'window',
            self.EVT_BARCONFIG: 'barconfig',
            self.EVT_BINDING: 'binding',
            self.EVT_SHUTDOWN: 'shutdown',
            self.EVT_TICK: 'tick',
            self.EVT_BAR_STATE: 'bar_state',
            self.EVT_INPUT: 'input'
        }.get(self, None)


## ---------------------
## Core IPC functions
## ---------------------

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

def serialize_message(payload_type:MessageType, payload:str|bytes) -> bytes:
    """Take a payload type and payload body, and serialize it into a series of bytes in the expected format."""
    if isinstance(payload, str):
        payload = payload.encode('utf-8')
    result:list[bytes] = []
    result.append(PAYLOAD_MAGIC_STRING)
    result.append(len(payload).to_bytes(4, byteorder=sys.byteorder))
    result.append(payload_type.value.to_bytes(4, byteorder=sys.byteorder))
    result.append(payload)
    return b"".join(result)

def deserialize_message(payload:bytes) -> tuple[MessageType, Any, bytes]:
    """Take a message recieved from the IPC socket, and parse it into a `Payload` object."""
    if not payload.startswith(PAYLOAD_MAGIC_STRING):
        raise Exception("Payload contents does not begin with magic string.")
    payload = payload[len(PAYLOAD_MAGIC_STRING):]
    payload_length = int.from_bytes(payload[:4], byteorder=sys.byteorder)
    payload_type_id = int.from_bytes(payload[4:8], byteorder=sys.byteorder)
    payload_type = MessageType(payload_type_id)
    current_payload = payload[8:8+payload_length]
    return payload_type, json.loads(current_payload.decode('utf-8')), payload[8+payload_length:]

def send_ipc_message(ptype: MessageType, payload:Any="") -> Any:
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

## ---------------------
## Core Sway objects
## ---------------------

class SwayObject(Loadable):
    ...

class CommandResult(SwayObject):
    success:bool
    parse_error:Optional[bool]
    error:Optional[str]

class Gaps(SwayObject):
    top:int
    left:int
    bottom:int
    right:int

class BarConfig(SwayObject):
    id:str
    mode:str
    position:str
    status_command:str
    font:str
    workspace_buttons:bool
    workspace_min_width:int
    binding_mode_indicator:bool
    verbose:bool
    colors:dict
    gaps:Gaps
    bar_height:int
    status_padding:int
    status_edge_padding:int
 
class Version(SwayObject):
    major:int
    minor:int
    patch:int
    human_readable:str
    loaded_config_file_name:str

class LibInput(SwayObject):
    send_events:Optional[str]
    tap:Optional[str]
    tap_button_map:Optional[str]
    tap_drag:Optional[str]
    tap_drag_lock:Optional[str]
    accel_speed:Optional[float]
    accel_profile:Optional[str]
    natural_scroll:Optional[str]
    left_handed:Optional[str]
    click_method:Optional[str]
    middle_emulation:Optional[str]
    scroll_method:Optional[str]
    scroll_button:Optional[int]
    dwt:Optional[str]
    dwtp:Optional[str]
    calibration_matrix:Optional[list]
 
class Input(SwayObject):
    identifier:str
    name:str
    vendor:str
    product:str
    type:str
    xkb_active_layout_name:Optional[str]
    xkb_layout_names:Optional[list]
    xkb_active_layout_index:Optional[str]
    scroll_factor:Optional[float]
    libinput:Optional[LibInput]
    repeat_delay:Optional[float]
    repeat_rate:Optional[float]
 
class Seat(SwayObject):
    name:str
    capabilities:int
    focus:int
    devices:list[Input]

class X11Window(SwayObject):
    title:str
    class_:str 
    instance:Any
    window_role:Any
    window_type:Any
    transient_for:Any

class Rect(SwayObject):
    x:int
    y:int
    width:int
    height:int

class OutputMode(SwayObject):
    width:int
    height:int
    refresh:float

class Hinting(enum.Enum):
    RGB = 'rgb'
    BGR = 'bgr'
    VRGB = 'vrgb'
    VBGR = 'vbgr'
    UNKNOWN = "unknown"

class Transform(enum.Enum):
    NORMAL = 'normal'
    T_90 = '90'
    T_180 = '180'
    T_270 = '170'
    FLIPPED_90 = 'flipped-90'
    FLIPPED_180 = 'flipped-180'
    FLIPPED_270 = 'flipped-270'

class BorderStyle(enum.Enum):
    NORMAL = "normal"
    PIXEL = "pixel"
    CSD = "csd"

class LayoutType(enum.Enum):
    NONE = 'none'
    SPLITH = "splith"
    SPLITV = "splitv"
    STACKED = "stacked"
    TABBED = "tabbed"
    OUTPUT = "output"

class Orientation(enum.Enum):
    NONE = 'none'
    VERTICAL= 'vertical'
    HORIZONTAL = 'horizontal'

class InputType(enum.Enum):
    TOUCHPAD = 'touchpad'
    POINTER = 'pointer'
    KEYBOARD = 'keyboard'
    TOUCH = 'touch'
    TABLET_TOOL = 'tablet_tool'
    TABLET_PAD = 'tablet_pad'
    SWITCH = 'switch'

class NodeType(enum.Enum):
    ROOT = "root"
    OUTPUT = "output"
    WORKSPACE = "workspace"
    CON = "con"
    FLOATING_CON = "floating_con"

class Node(SwayObject, metaclass=ABCMeta):
    id:int
    type:NodeType
    orientation:Orientation
    percent:float
    urgent:bool
    marks:list[str]
    focused:bool
    layout:LayoutType
    border:BorderStyle
    current_border_width:int
    rect:Rect
    window_rect:Rect
    deco_rect:Rect
    geometry:Rect
    name:str
    focus:list[int]
    fullscreen_mode:int
    sticky:bool
    nodes:list
    floating_nodes:list
    
    def __new__(cls, data:dict) -> Self:
        if cls is Node:
            node_type = data.get('type')
            if node_type == NodeType.CON.value or node_type == NodeType.FLOATING_CON.value:
                cls = ContainerNode
            elif node_type == NodeType.OUTPUT.value:
                cls = Output
            elif node_type == NodeType.WORKSPACE.value:
                cls = Workspace
            elif node_type == NodeType.ROOT.value:
                cls = RootNode
            else:
                raise Exception(f"Unknown NodeType: {node_type}")
        return cast(Self, Loadable.__new__(cls, data))

class RootNode(Node):
    nodes:list['Output']
    floating_nodes:list['Output']

class Output(Node):
    make:str
    model:str
    serial:str
    active:bool
    dpms:bool
    power:bool
    primary:bool
    scale:float
    subpixel_hinting:Optional[Hinting]
    transform:Transform
    current_workspace:Optional[str]
    modes:list[OutputMode]
    current_mode:OutputMode
    nodes:list['Workspace']
    floating_nodes:list['Workspace']

class Workspace(Node):
    name:str
    rect:Rect
    visible:bool
    focused:bool
    urgent:bool
    num:int
    output:str
    representation:str
    nodes:list['ContainerNode']
    floating_nodes:list['ContainerNode']

class ContainerNode(Node):
    fullscreen_mode:int
    app_id:Optional[str]
    pid:int
    visible:bool
    shell:str
    inhibit_idle:bool
    idle_inhibitors:Any
    window:Optional[int]
    window_properties: Optional[X11Window]

## ---------------------
## Primary IPC messages
## ---------------------

def run_command(command:str) -> list[CommandResult]:
    """Run a Sway command, or series of commands delimited by comma or semiolon."""
    result = send_ipc_message(
        MessageType.RUN_COMMAND, 
        command
    )
    return [CommandResult(r) for r in result]

def command_succeeds(command:str) -> bool:
    """Helper function that returns whether the command succeeded."""
    return False not in [res.success for res in run_command(command)]

def get_workspaces() -> list[Workspace]:
    """Get a list of all workspaces."""
    result = send_ipc_message(MessageType.GET_WORKSPACES)
    return [Workspace(op) for op in result]

def get_outputs() -> list[Output]:
    """Get a list of all outputs, including the invisible scratchpad output."""
    result = send_ipc_message(MessageType.GET_OUTPUTS)
    return [Output(op) for op in result]

def get_tree() -> RootNode:
    """Get the full node tree."""
    return RootNode(send_ipc_message(MessageType.GET_TREE))

def get_nodes() -> Set[RootNode|Output|Workspace|ContainerNode]:
    """Get the node tree and flatten it into a set."""
    result = set()
    nodes:list[RootNode|Output|Workspace|ContainerNode] = [get_tree()]
    if nodes is None:
        return set()
    while len(nodes) > 0:
        n = nodes.pop(0)
        result.add(n)
        nodes.extend(n.nodes)
        nodes.extend(n.floating_nodes)
    return result

def get_marks() -> list[str]:
    """Get a list of marks currently in use."""
    return send_ipc_message(MessageType.GET_MARKS)

@overload
def get_bar_config() -> list[str]:...
@overload
def get_bar_config(bar_id:str) -> BarConfig:...
def get_bar_config(bar_id:Optional[str]=None) -> Any:
    """
    Get bar config information.
    
    If the `bar_id` is not specified, it will return a list of bar IDs.
    Otherwise, it will return the full bar config.
    """
    if bar_id is None:
        return send_ipc_message(MessageType.GET_BAR_CONFIG)
    return BarConfig(send_ipc_message(MessageType.GET_BAR_CONFIG, bar_id))

def get_version() -> Version:
    """Get version information."""
    return Version(send_ipc_message(MessageType.GET_VERSION))

def get_binding_modes() -> list[str]:
    """Get the list of available binding modes."""
    return send_ipc_message(MessageType.GET_BINDING_MODES)

def get_config() -> str:
    return send_ipc_message(MessageType.GET_CONFIG)["config"]

def send_tick(payload:str="") -> bool:
    """Send a tick, with an optional payload."""
    return send_ipc_message(MessageType.SEND_TICK, payload)["success"]

def sync() -> bool:
    """Send a sync message (unused in Wayland)."""
    return send_ipc_message(MessageType.SYNC)["success"]

def get_binding_state() -> str:
    """Get the currently-used binding state."""
    return send_ipc_message(MessageType.GET_BINDING_STATE)

def get_inputs() -> list[Input]:
    """Get a list of all inputs."""
    return [
        Input(op)
        for op in send_ipc_message(MessageType.GET_INPUTS)
    ]

def get_seats() -> list[Seat]:
    """Get a list of all seats."""
    return [
        Seat(op) 
        for op in send_ipc_message(MessageType.GET_SEATS)
    ]

def kill(criteria_or_node:Node):
    if isinstance(criteria_or_node, Node):
        run_command(f'kill ${criteria_or_node.id}')