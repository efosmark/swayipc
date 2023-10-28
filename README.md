# `swayipc` - Interact with Sway
A fully-typed package for interacting with the [Sway](https://swaywm.org/) window manager via its IPC connection. Run `man 7 sway` for more information on its IPC protocol. <sup>[(docs)](https://man.archlinux.org/man/sway-ipc.en)</sup>

## Goals

- [x] Low-level interface for interacting with the IPC socket (See section [Low-level](#Low-level))
- [x] A model of the Sway IPC objects and their main commands (See section [Commands](#Commands))
- [ ] Maintain a fully-typed high-level data model
- [ ] Example-driven documentation as a Sphinx project
- [ ] A data model allowing actions such as `Workspace(name="dev").focus()`
- [ ] A typed command builder. _low priority, but it'd be handy._

 >[!NOTE]
 >This package was started as a precursor to a different project that I'm working on, and originally spawned as a way for me to learn more about the IPC. As such, it's very likely to experience significant changes until its first stable release.

## Install
```shell
pip install swayipc
```

# Commands

## `run_command(...)`
Runs a sway command, or a series of sway commands. Each command, separated by a comma, will have its own `CommandResult`.

>**REPLY:** An array of objects corresponding to each command that was parsed. Each object has the property `success`, which is a boolean indicating whether the command was successful. The object may also contain the properties `error` and `parse_error`. The `error` property is a human readable error message while `parse_error` is a boolean indicating whether the reason the command failed was because the command was unknown or not able to be parsed.
<sup>[(docs)](https://man.archlinux.org/man/sway-ipc.7.en#0._RUN_COMMAND)</sup>

```python
>>> import swayipc
>>> swayipc.run_command('floating toggle')
[CommandResult(success=True)]
>>> swayipc.run_command('floating toggle, fake command')
[
    CommandResult(success=True),
    CommandResult(
       error="Unknown/invalid command 'fake'",
       parse_error=True,
       success=False
    )
]
```

## `get_workspaces()`
>Retrieves the list of workspaces.
>
>**REPLY:** The reply is an array of objects corresponding to each workspace.
<sup>[(docs)](https://man.archlinux.org/man/sway-ipc.en#1._GET_WORKSPACES)</sup>

```python
>>> import swayipc
>>> ws = swayipc.get_workspaces()
>>> ws[0]
Workspace(
  border='none',
  current_border_width=0,
  deco_rect=Rect(height=0, width=0, x=0, y=0),
  floating_nodes=[],
  focus=[27],
  focused=False,
  fullscreen_mode=1,
  geometry=Rect(height=0, width=0, x=0, y=0),
  id=28,
  layout='splith', 
  marks=[],
  name='3',
  nodes=[],
  num=3,
  orientation='horizontal',
  output='DSI-1',
  percent=None,
  rect=Rect(height=800, width=1280, x=0, y=0),
  representation='H[appname]',
  sticky=False,
  type='workspace',
  urgent=False, 
  visible=False, 
  window=None,
  window_rect=Rect(height=0, width=0, x=0, y=0),
)
```

## `subscribe(events)`
>Subscribe this IPC connection to the event types specified in the message payload. The payload should be a valid JSON array of events.
<sup>[(docs)](https://man.archlinux.org/man/sway-ipc.en#2._SUBSCRIBE)</sup>

This function returns a generator that yields each event recieved from the IPC socket.

## `get_outputs()`
>Retrieve the list of outputs.
>
>**REPLY:** An array of objects corresponding to each output.
<sup>[(docs)](https://man.archlinux.org/man/sway-ipc.en#3._GET_OUTPUTS)</sup>

```python
>>> import swayipc
>>> swayipc.get_outputs()
[
   Output(
     active=True, 
     adaptive_sync_status='disabled', 
     border='none', 
     current_border_width=0, 
     current_mode=OutputMode(
       height=1280,
       refresh=59928,
       width=800
    ),
    current_workspace='4',
    deco_rect=Rect(height=0, width=0, x=0, y=0),
    dpms=True, 
    floating_nodes=[], 
    focus=[314, 28, 310, 304], 
    focused=True, 
    fullscreen_mode=0, 
    geometry=Rect(height=0, width=0, x=0, y=0), 
    id=3, 
    layout='output', 
    make='Unknown', 
    marks=[], 
    max_render_time=0, 
    model='Unknown', 
    modes=[
      OutputMode(height=1280, refresh=59928.0, width=800),
      OutputMode(height=1920, refresh=60000.0, width=1200)
    ],
    name='DSI-1', 
    nodes=[], 
    non_desktop=False, 
    orientation='none', 
    percent=1.0, 
    power=True, 
    primary=False, 
    rect=Rect(height=800, width=1280, x=0, y=0),
    scale=1.0,
    scale_filter='nearest',
    serial='Unknown', 
    sticky=False,
    subpixel_hinting=<Hinting.RGB: 'rgb'>,
    transform=<OutputTransform.T_90: '90'>,
    type='output',
    urgent=False,
    window=None,
    window_rect=Rect(height=0, width=0, x=0, y=0)
  )
]
```

## `get_tree()`
Get the full view tree. Each tree object can be one of: `RootNode`, `ContainerNode`, `OutputNode`, or `ViewNode`.

>**REPLY:** An array of objects that represent the current tree. <sup>[(docs)](https://man.archlinux.org/man/sway-ipc.en#4._GET_TREE)</sup>

 >[!NOTE]
 >If you are needing to walk every node in order to perform some action, there's a helper function, `get_nodes()` which returns a list of all nodes available from `get_tree()`.

## `get_marks()`
>Retrieve the currently set marks.
>
>**REPLY:** An array of marks current set. Since each mark can only be set for one container, this is a set so each value is unique and the order is undefined.
<sup>[(docs)](https://man.archlinux.org/man/sway-ipc.en#5._GET_MARKS)</sup>

## `get_bar_config(bar_id?)`

### Without a `bar_id` specified
>Retrieves the list of configured bar IDs.
>
>**REPLY:** An array of bar IDs, which are strings
<sup>[(docs)](<https://man.archlinux.org/man/sway-ipc.en#6._GET_BAR_CONFIG_(WITHOUT_A_PAYLOAD>)</sup>

```python
>>> import python
>>> swayipc.get_bar_config()
['bar-0', 'bar-primary']
```

### With a `bar_id` specified
>When sent with a bar ID as the payload, this retrieves the config associated with the specified by the bar ID in the payload. This is used by swaybar, but could also be used for third party bars.
>
>**REPLY:** An object that represents the configuration for the bar with the bar ID sent as the payload. ^[<https://man.archlinux.org/man/sway-ipc.en#6._GET_BAR_CONFIG_(WITH_A_PAYLOAD>)]

```python
>>> import python
>>> swayipc.get_bar_config('bar-0')
BarConfig(
  bar_height=0,
  binding_mode_indicator=True,
  colors=dict(...),
  font='Compagnon 10',
  gaps=Gaps(bottom=0, left=0, right=0, top=0), 
  hidden_state='hide',
  id='bar-0',
  mode='dock', 
  pango_markup=True, 
  position='bottom',
  status_command=None,
  status_edge_padding=3,
  status_padding=1,
  strip_workspace_name=False,
  strip_workspace_numbers=False,
  tray_padding=2,
  verbose=False,
  workspace_buttons=True,
  workspace_min_width=0,
  wrap_scroll=False
)
```

## `get_version()`
>Retrieve version information about the sway process <sup>[(docs)](https://man.archlinux.org/man/sway-ipc.en#7._GET_VERSION)</sup>

```python
>>> import swayipc
>>> swayipc.get_version()
{
   'human_readable': '1.8.1',
   'variant': 'sway',
   'major': 1,
   'minor': 8,
   'patch': 1,
   'loaded_config_file_name': '/home/user/.config/sway/config'
}
```

## `get_binding_modes()`
>Retrieve the list of binding modes that currently configured.
>
>**REPLY**  
>An array of strings, with each string being the name of a binding mode. This will always contain at least one mode (currently `"default"`), which is the default binding mode. <sup>[(docs)](https://man.archlinux.org/man/sway-ipc.en#8._GET_BINDING_MODES)</sup>

```python
>>> import swayipc
>>> swayipc.get_binding_modes()
[ 'default', 'resize', 'screenshot', 'dd-term' ]
```

## `get_config()`
>Retrieve the contents of the config that was last loaded.[](https://man.archlinux.org/man/sway-ipc.7.en#9._GET_CONFIG)

```python
>>> import swayipc
>>> swayipc.get_config()
'# The entire config contents that was last loaded'
```
## `send_tick(payload="")`
>Issues a _TICK_ event to all clients subscribing to the event to ensure that all events prior to the tick were received. If a `payload` is given, it will be included in the _TICK_ event. <sup>[(docs)](https://man.archlinux.org/man/sway-ipc.en#10._SEND_TICK)</sup>

```python
>>> import swayipc
>>> swayipc.send_tick()
True
```

## `get_binding_state()`
>Returns the currently active binding mode. <sup>[(docs)](https://man.archlinux.org/man/sway-ipc.en#12._GET_BINDING_STATE)</sup>

```python
>>> import swayipc
>>> swayipc.get_binding_state()
'default'
```

## `get_inputs()`
>Retrieve a list of the input devices currently available
>
>**REPLY** An array of objects corresponding to each input device. <sup>[(docs)](https://man.archlinux.org/man/sway-ipc.en#100._GET_INPUTS)</sup>

```python
>>> import swayipc
>>> inputs = swayipc.get_inputs()
>>> inputs[0]
Input(
    identifier='10182:275:GXTP7380:00_27C6:0113_Keyboard', 
    libinput=LibInput(send_events='enabled'), 
    name='GXTP7380:00 27C6:0113 Keyboard',
    product='275', 
    repeat_delay=600.0,
    repeat_rate=25.0,
    type='keyboard', 
    vendor='10182',
    xkb_active_layout_index='0', 
    xkb_active_layout_name='English (US)',
    xkb_layout_names=['English (US)']
)
```

>[!NOTE]
>The sway-ipc documentation states the following:
>>The `libinput` object describes the device configuration for libinput devices. Only properties that are supported for the device will be added to the object. In addition to the possible options listed, all string properties may also be _unknown_, in the case that a new option is added to libinput.

## `get_seats()`
>Retrieve a list of the seats currently configured
>
>**REPLY** An array of objects corresponding to each seat.
<sup>[(docs)](https://man.archlinux.org/man/sway-ipc.en#101._GET_SEATS)</sup>

```python
>>> import swayipc
>>> swayipc.get_seats()
[ 
  Seat(
    capabilities=7,
    devices=[
      Input(...),
      Input(...),
      Input(...),
      ...
    ],
    focus=313,
    name='seat0'
  )
]
```

# Low-level functions
The following functions are the low-level interface with the IPC socket.
These are found in the `swayipc.ipc` module.

## `get_socket_location`
Obtain the Sway socket location via the `I3SOCK` environment variable.
This is usually unnecessary to call, as calling `get_ipc_socket()` without any arguments will give you the socket at the default location.

## `get_ipc_socket`
Get a Sway IPC socket as a Python socket.

## `serialize_message`
Take a payload type and payload body, and serialize it into a series of bytes in the expected format.

**Arguments**
- `payload_type: MessageType`
- `payload: str`

## `deserialize_message`
Take a message recieved from the IPC socket, and parse it into a `Payload` object. This returns a tuple consisting of the message type, the message object (typically a `dict` or `list`), and any remainder from the message buffer. The remainder is only needed when using a pattern like `subscribe()` where multiple messages my be recieved and the buffer needs to be maintained.

**Arguments**
- `payload: bytes` - The raw bytes from the IPC socket.

## `send_ipc_message`
Send a message to the Sway IPC consisting of the given `payload_type` and `message`.

**Arguments**
- `ptype: MessageType` - The `MessageType` being sent
- `payload` - The serialized payload data being sent

## The `MessageType` enum

The following enum is present inside of `swayipc.ipc`.

```python
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
    EVT_WORKSPACE = 0x80000000
    EVT_MODE = 0x80000002
    EVT_WINDOW = 0x80000003
    EVT_BARCONFIG = 0x80000004
    EVT_BINDING = 0x80000005
    EVT_SHUTDOWN = 0x80000006
    EVT_TICK = 0x80000007
    EVT_BAR_STATE = 0x80000014
    EVT_INPUT = 0x80000015
```


# Event dispatcher

The event dispatcher can help when writing scripts to respond to specific events.
In this example, we'll remove the title-bar when there's only one container is within a workspace.

```python
from swayipc import *

def show_titlebar_smart(event):
    """ Hide the application title bar when there's only one visible app in the workspace."""
    for n in get_nodes():
        if n.type != NodeType.WORKSPACE or n.name == "__i3_scratch":
            continue
        border = "none" if len(n.nodes) == 1 else "normal"        
        run_command(f'{where(workspace=n.name)} border {border}')

if __name__ == "__main__":
    handler = event.Dispatcher()
    handler.on_window_close(show_titlebar_smart)
    handler.on_window_new(show_titlebar_smart)
    handler.start() # Blocking call that subscribes to IPC events and dispatches them as they arrive
                    # If you already have an event loop, you can manually call `handler.dispatch()` instead
```

Alternatively, it can be configured with function decorators.

```python
from swayipc import *

handler = event.Dispatcher()

@handler.on_window_close
@handler.on_window_new
def show_titlebar_smart(event):
    """ Hide the application title bar when there's only one visible app in the workspace."""
    for n in get_nodes():
        if n.type != NodeType.WORKSPACE or n.name == "__i3_scratch":
            continue
        border = "none" if len(n.nodes) == 1 else "normal"        
        run_command(f'{where(workspace=n.name)} border {border}')

if __name__ == "__main__":
    handler.start()
```

These are the following event hooks available:

- `on_bar_state_changed`
- `on_bar_config_changed`
- `on_binding_changed`
- `on_input_changed`
- `on_mode_changed`
- `on_tick`
- `on_shutdown`
- `on_window_changed`
- `on_workspace_changed`
- `on_window_new`
- `on_window_close`
- `on_window_focus`
- `on_window_title`
- `on_window_fullscreen`
- `on_window_move`
- `on_window_floating`
- `on_window_urgent`
- `on_window_mark`
- `on_workspace_init`
- `on_workspace_empty`
- `on_workspace_focus`
- `on_workspace_move`
- `on_workspace_rename`
- `on_workspace_urgent`
- `on_workspace_reload`


# License

MIT license. See [LICENSE](LICENSE).
