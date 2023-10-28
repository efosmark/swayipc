import swayipc
from swayipc.criteria import where, FOCUSED

def get_first_free_ws_number():
    """Query the current workspaces and get the first number that's not in use."""
    workspaces = swayipc.get_workspaces()
    ws_nums = sorted([w.num for w in workspaces if w.num > -1])
    for num in range(1, max(ws_nums)):
        if num not in ws_nums:
            return num
    return 1

if __name__ == "__main__":
    next_ws = get_first_free_ws_number()
    criteria = where(con_id=FOCUSED)
    swayipc.run_command(f"{criteria} move to workspace number {next_ws}, focus")
