from swayipc import *
from swayipc.criteria import where
from swayipc.event import WindowEvent

def transparent_unfocused_windows(event:WindowEvent):
    """Set the opacity to a lower setting for windows that aren't currently-focused."""
    
    cmd_reset_opacity = where(tiling=True) + " opacity 0.75"
    cmd_set_opaque = where(con_id=event.container.id) + " opacity 1.0"
    
    result = run_command("; ".join([cmd_reset_opacity, cmd_set_opaque]))
    print(result)

if __name__ == "__main__":
    handler = event.Dispatcher()
    handler.on_window_focus(transparent_unfocused_windows)
    handler.start()
