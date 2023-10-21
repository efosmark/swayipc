from typing import Any, Literal, Optional, List, Final, Dict, Self, Protocol
import enum

from .model import _LoadableSwayObject, Input, Workspace, RootNode, BarConfig
from .ipc import EVT_OFFSET, PayloadType

class WindowChangeType(enum.Enum):
    new = "new"
    close = "close"
    focus = "focus"
    title = "title"
    fullscreen_mode = "fullscreen_mode"
    move = "move"
    floating = "floating"
    urgent = "urgent"
    mark = "mark"

class WorkspaceChangeType(enum.Enum):
    init = "init"
    empty = "empty"
    focus = "focus"
    move = "move"
    rename = "rename"
    urgent = "urgent"
    reload = "reload"

ALL_EVENTS = [x for x in PayloadType if x.value >= EVT_OFFSET]

class SwayEvent(_LoadableSwayObject):...

class WorkspaceEvent(SwayEvent):
    change: WorkspaceChangeType
    current: Workspace
    old: Optional[Workspace]

class ModeEvent(SwayEvent):
    change:str
    pango_markup:bool

class WindowEvent(SwayEvent):
    change:WindowChangeType
    container:RootNode

class BindingEvent(SwayEvent):
    change:str
    command:str
    event_state_mask:List[str]
    input_code:int
    symbol:str
    input_type:str

class ShutdownEvent(SwayEvent):
    change:Literal["exit"]

class TickEvent(SwayEvent):
    first:bool
    payload:str

class BarStateUpdateEvent(SwayEvent):
    id:str
    visible_by_modifier:bool

class InputEvent(SwayEvent):
    change:str
    input:Input

class BarConfigUpdateEvent(SwayEvent, BarConfig):...

class CanBeBuiltFromDict(Protocol):
    @classmethod
    def from_dict(cls, data:Dict[str, Any]) -> Self:...

EVENT_TYPE_TO_EVENT:Final[Dict[PayloadType, CanBeBuiltFromDict]] = {
    PayloadType.EVT_BAR_STATE: BarStateUpdateEvent,
    PayloadType.EVT_BARCONFIG: BarConfigUpdateEvent,
    PayloadType.EVT_BINDING: BindingEvent,
    PayloadType.EVT_INPUT: InputEvent,
    PayloadType.EVT_MODE: ModeEvent,
    PayloadType.EVT_TICK: TickEvent,
    PayloadType.EVT_SHUTDOWN: ShutdownEvent,
    PayloadType.EVT_WINDOW: WindowEvent,
    PayloadType.EVT_WORKSPACE: WorkspaceEvent
}
