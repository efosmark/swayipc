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
    handler.start()
