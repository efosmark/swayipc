import enum
import json
from collections import defaultdict
from typing import Any, Callable, Literal, Optional, List, Dict, Protocol, Self, Sequence, Tuple, TypeVar, cast
from .loadable import FromDict
from .ipc import BarConfig, Input, Workspace, Node, MessageType, get_ipc_socket, serialize_message, deserialize_message, PAYLOAD_MAGIC_STRING, RESPONSE_BUFFER_SIZE

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

class SwayEvent(FromDict):
    mtype: MessageType

class WorkspaceEvent(SwayEvent):
    change: WorkspaceChangeType
    current: Workspace
    old: Optional[Workspace]

class ModeEvent(SwayEvent):
    change:str
    pango_markup:bool

class WindowEvent(SwayEvent):
    change:WindowChangeType
    container:Node

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

class BarStateEvent(SwayEvent):
    id:str
    visible_by_modifier:bool

class InputEvent(SwayEvent):
    change:str
    input:Input

class BarConfigEvent(SwayEvent, BarConfig):...

class CanBeBuiltFromDict(Protocol):
    @classmethod
    def from_dict(cls, data:Dict[str, Any]) -> Self:...

Dispatchable = MessageType | Tuple[MessageType, WindowChangeType|WorkspaceChangeType]
_E = TypeVar("_E", bound=SwayEvent)

EVENT_TYPE_TO_EVENT:Dict[MessageType, CanBeBuiltFromDict] = {
    MessageType.EVT_BAR_STATE: BarStateEvent,
    MessageType.EVT_BARCONFIG: BarConfigEvent,
    MessageType.EVT_BINDING: BindingEvent,
    MessageType.EVT_INPUT: InputEvent,
    MessageType.EVT_MODE: ModeEvent,
    MessageType.EVT_TICK: TickEvent,
    MessageType.EVT_SHUTDOWN: ShutdownEvent,
    MessageType.EVT_WINDOW: WindowEvent,
    MessageType.EVT_WORKSPACE: WorkspaceEvent
}



def subscribe(events:Sequence[MessageType]):
    """ Subscribe to the given sequence of events.
    
    This function returns a generator that yields each message recieved from the IPC socket.
    """
    with get_ipc_socket() as s:
        s.send(serialize_message(
            MessageType.SUBSCRIBE,
            json.dumps([e.subfield() for e in events if e.subfield() is not None])
        ))
        buffer = b""
        while True:
            buffer += s.recv(RESPONSE_BUFFER_SIZE)
            while PAYLOAD_MAGIC_STRING in buffer:
                mtype, message, buffer = deserialize_message(buffer)
                if mtype == MessageType.SUBSCRIBE: continue
                if not mtype.is_event():
                    raise TypeError(f"The payload type of a subscribe response is not an event. mtype={mtype}")
                event = cast(SwayEvent, EVENT_TYPE_TO_EVENT[mtype].from_dict(message))
                event.mtype = mtype
                yield event



#
# Event handler callback types
#
EventHandler_T = Callable[[BarStateEvent], bool|None]
BarStateHandler_T = Callable[[BarStateEvent], bool|None]
BarConfigHandler_T = Callable[[BarConfigEvent], bool|None]
BindingHandler_T = Callable[[BindingEvent], bool|None]
InputHandler_T = Callable[[InputEvent], bool|None]
ModeHandler_T = Callable[[ModeEvent], bool|None]
TickHandler_T = Callable[[TickEvent], bool|None]
ShutdownHandler_T = Callable[[ShutdownEvent], bool|None]
WindowHandler_T = Callable[[WindowEvent], bool|None]
WorkspaceHandler_T = Callable[[WorkspaceEvent], bool|None]

class Dispatcher:
    handlers: Dict[Dispatchable, list[Callable]]
    
    def __init__(self):
        self.handlers = defaultdict(list)
    
    def dispatch(self, event:SwayEvent, change_type:Optional[WindowChangeType|WorkspaceChangeType]=None):
        t = event.mtype
        if change_type is not None:
            t = (t, change_type)
        if t in self.handlers:
            for handler in self.handlers[t]:
                result = handler(event)
                if result == False:
                    break
    
    def register(self, mtype:Dispatchable, func:Callable[[_E], bool|None]) -> Callable[[_E], bool|None]:
        if func not in self.handlers[mtype]:
            self.handlers[mtype].append(func)
        return func
    
    def start(self):
        for event in subscribe(MessageType.all_events()):
            self.dispatch(event)
            if isinstance(event, WindowEvent) or isinstance(event, WorkspaceEvent):
                self.dispatch(event, change_type=event.change)
    
    def on_bar_state_changed(self, func:BarStateHandler_T) -> BarStateHandler_T:
        return self.register(MessageType.EVT_BAR_STATE, func)
    
    def on_bar_config_changed(self, func:BarConfigHandler_T) -> BarConfigHandler_T:
        return self.register(MessageType.EVT_BARCONFIG, func)

    def on_binding_changed(self, func:BindingHandler_T) -> BindingHandler_T:
        return self.register(MessageType.EVT_BINDING, func)
    
    def on_input_changed(self, func:InputHandler_T) -> InputHandler_T:
        return self.register(MessageType.EVT_BAR_STATE, func)
    
    def on_mode_changed(self, func:ModeHandler_T) -> ModeHandler_T:
        return self.register(MessageType.EVT_MODE, func)
    
    def on_tick(self, func:TickHandler_T) -> TickHandler_T:
        return self.register(MessageType.EVT_TICK, func)
    
    def on_shutdown(self, func:ShutdownHandler_T) -> ShutdownHandler_T:
        return self.register(MessageType.EVT_SHUTDOWN, func)
    
    def on_window_changed(self, func:WindowHandler_T) -> WindowHandler_T:        
        return self.register(MessageType.EVT_WINDOW, func)
    
    def on_workspace_changed(self, func:WorkspaceHandler_T) -> WorkspaceHandler_T:
        return self.register(MessageType.EVT_WORKSPACE, func)
    
    #
    # Window-specific events
    #
    def on_window_new(self, func:WindowHandler_T) -> WindowHandler_T:
        return self.register((MessageType.EVT_WINDOW, WindowChangeType.new), func)
    
    def on_window_close(self, func:WindowHandler_T) -> WindowHandler_T:
        return self.register((MessageType.EVT_WINDOW, WindowChangeType.close), func)
    
    def on_window_focus(self, func:WindowHandler_T) -> WindowHandler_T:
        return self.register((MessageType.EVT_WINDOW, WindowChangeType.focus), func)
    
    def on_window_title(self, func:WindowHandler_T) -> WindowHandler_T:
        return self.register((MessageType.EVT_WINDOW, WindowChangeType.title), func)
    
    def on_window_fullscreen(self, func:WindowHandler_T) -> WindowHandler_T:
        return self.register((MessageType.EVT_WINDOW, WindowChangeType.fullscreen_mode), func)
    
    def on_window_move(self, func:WindowHandler_T) -> WindowHandler_T:
        return self.register((MessageType.EVT_WINDOW, WindowChangeType.move), func)
    
    def on_window_floating(self, func:WindowHandler_T) -> WindowHandler_T:
        return self.register((MessageType.EVT_WINDOW, WindowChangeType.floating), func)
    
    def on_window_urgent(self, func:WindowHandler_T) -> WindowHandler_T:
        return self.register((MessageType.EVT_WINDOW, WindowChangeType.urgent), func)
    
    def on_window_mark(self, func:WindowHandler_T) -> WindowHandler_T:
        return self.register((MessageType.EVT_WINDOW, WindowChangeType.mark), func)
    
    #
    # Workspace-specific events
    #
    def on_workspace_init(self, func:WorkspaceHandler_T) -> WorkspaceHandler_T:
        return self.register((MessageType.EVT_WORKSPACE, WorkspaceChangeType.init), func)
    
    def on_workspace_empty(self, func:WorkspaceHandler_T) -> WorkspaceHandler_T:
        return self.register((MessageType.EVT_WORKSPACE, WorkspaceChangeType.empty), func)
    
    def on_workspace_focus(self, func:WorkspaceHandler_T) -> WorkspaceHandler_T:
        return self.register((MessageType.EVT_WORKSPACE, WorkspaceChangeType.focus), func)
    
    def on_workspace_move(self, func:WorkspaceHandler_T) -> WorkspaceHandler_T:
        return self.register((MessageType.EVT_WORKSPACE, WorkspaceChangeType.move), func)
    
    def on_workspace_rename(self, func:WorkspaceHandler_T) -> WorkspaceHandler_T:
        return self.register((MessageType.EVT_WORKSPACE, WorkspaceChangeType.rename), func)
    
    def on_workspace_urgent(self, func:WorkspaceHandler_T) -> WorkspaceHandler_T:
        return self.register((MessageType.EVT_WORKSPACE, WorkspaceChangeType.urgent), func)
    
    def on_workspace_reload(self, func:WorkspaceHandler_T) -> WorkspaceHandler_T:
        return self.register((MessageType.EVT_WORKSPACE, WorkspaceChangeType.reload), func)
