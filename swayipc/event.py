from typing import Any, Literal, Optional, List, Final, Dict, Self, Protocol
import enum
from .ipc import EventType
from .model import _LoadableSwayObject, Input, Workspace, RootNode, BarConfig

class WorkspaceChangeType(enum.Enum):
    init = "init"
    empty = "empty"
    focus = "focus"
    move = "move"
    rename = "rename"
    urgent = "urgent"
    reload = "reload"

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

ALL_EVENT_TYPES = [ EventType.workspace, EventType.mode, EventType.window, EventType.barconfig_update, EventType.binding,
                    EventType.shutdown, EventType.tick, EventType.bar_state_update, EventType.input ]

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

EVENT_TYPE_TO_EVENT:Final[Dict[EventType, CanBeBuiltFromDict]] = {
    EventType.bar_state_update: BarStateUpdateEvent,
    EventType.barconfig_update: BarConfigUpdateEvent,
    EventType.binding: BindingEvent,
    EventType.input: InputEvent,
    EventType.mode: ModeEvent,
    EventType.tick: TickEvent,
    EventType.shutdown: ShutdownEvent,
    EventType.window: WindowEvent,
    EventType.workspace: WorkspaceEvent
}
