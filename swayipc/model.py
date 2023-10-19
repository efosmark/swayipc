import enum
from types import NoneType
from typing import Any, List, Optional, Union, get_type_hints
try:
    from typing import get_args, get_origin
except ImportError:
    get_args = lambda t: getattr(t, '__args__', ())
    get_origin = lambda t: getattr(t, '__origin__', None)

class _LoadableSwayObject:

    @staticmethod
    def _value(field_type, value):
        if value is None or value == "none":
            return None
        if issubclass(field_type, _LoadableSwayObject):
            return field_type.from_dict(value)
        return field_type(value)

    @classmethod
    def from_dict(cls, data:dict[str,Any]):
        self = cls()
        hints = get_type_hints(cls)
        for key, value in data.items():
            if key not in hints:
                setattr(self, key, value)
                continue
            field_type = hints[key]
            field_origin = get_origin(field_type)
            field_args = set(get_args(field_type))
            
            if field_origin == list:
                field_type = field_args.pop()
                setattr(self, key, [self._value(field_type, v) for v in value])
            
            elif field_origin == Union and NoneType in field_args and len(field_args) == 2:
                field_args.remove(NoneType)
                field_type = field_args.pop()
                setattr(self, key, self._value(field_type, value))
            
            else:
                setattr(self, key, self._value(field_type, value))
        return self

    def __repr__(self):
        kv = [
            f"{n}={repr(getattr(self, n))}" 
            for n in dir(self)
            if not n.startswith('_') and n not in ['from_dict']
        ]
        return f"{self.__class__.__name__}({', '.join(kv)})"




class CommandResult(_LoadableSwayObject):
    success:bool
    parse_error:Optional[bool]
    error:Optional[str]

class Gaps(_LoadableSwayObject):
    top:int
    left:int
    bottom:int
    right:int

class BarConfig(_LoadableSwayObject):
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
 
class Version(_LoadableSwayObject):
    major:int
    minor:int
    patch:int
    human_readable:str
    loaded_config_file_name:str

class LibInput(_LoadableSwayObject):
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
 
class Input(_LoadableSwayObject):
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
 
class Seat(_LoadableSwayObject):
    name:str
    capabilities:int
    focus:int
    devices:List[Input]

class Hinting(enum.Enum):
    RGB = 'rgb'
    BGR = 'bgr'
    VRGB = 'vrgb'
    VBGR = 'vbgr'
    unknown = "unknown"

class BorderStyle(enum.Enum):
    normal = "normal"
    pixel = "pixel"
    csd = "csd"

class LayoutType(enum.Enum):
    splith = "splith"
    splitv = "splitv"
    stacked = "stacked"
    tabbed = "tabbed"
    output = "output"

class Orientation(enum.Enum):
    vertical= 'vertical'
    horizontal = 'horizontal'

class X11Window(_LoadableSwayObject):
    title:str
    class_:str 
    instance:Any
    window_role:Any
    window_type:Any
    transient_for:Any

class Rect(_LoadableSwayObject):
    x:int
    y:int
    width:int
    height:int

class NodeType(enum.Enum):
    root = "root"
    output = "output"
    workspace = "workspace"
    con = "con"
    floating_on = "floating_con"

class Workspace(_LoadableSwayObject):
    id:int
    name:str
    rect:Rect
    visible:bool
    focused:bool
    urgent:bool
    num:int
    output:str

class OutputMode(_LoadableSwayObject):
    width:int
    height:int
    refresh:float

class OutputTransform(enum.Enum):
    NORMAL = 'normal'
    T_90 = '90'
    T_180 = '180'
    T_270 = '170'
    FLIPPED_90 = 'flipped-90'
    FLIPPED_180 = 'flipped-180'
    FLIPPED_270 = 'flipped-270'

class Output(_LoadableSwayObject):
    name:str
    rect:Rect
    make:str
    model:str
    serial:str
    active:bool
    dpms:bool
    power:bool
    primary:bool
    scale:float
    subpixel_hinting:Optional[Hinting]
    transform:OutputTransform
    current_workspace:Optional[str]
    modes:List[OutputMode]
    current_mode:OutputMode




class RootNode(_LoadableSwayObject):
    id:int
    name:str
    type:NodeType
    border:Optional[BorderStyle]
    current_border_width:int
    layout:LayoutType
    orientation:Optional[Orientation]
    percent:Optional[float]
    rect:Rect
    window_rect:Rect 
    deco_rect:Rect 
    geometry:Rect 
    urgent:bool
    sticky:bool
    marks:List[str]
    focused:bool
    focus:List[int]
    nodes:List['RootNode']
    floating_nodes:List['RootNode']

class WorkspaceNode(RootNode, Workspace):
    representation:str

class ContainerNode(RootNode):
    fullscreen_mode:int

class ViewNode(RootNode):
    app_id:Optional[str]
    pid:int
    visible:bool
    shell:str
    inhibit_idle:bool
    idle_inhibitors:Any

class X11ViewNode(ViewNode):
    window:Optional[int]
    window_properties: Optional[X11Window]

class OutputNode(RootNode, Output):...
