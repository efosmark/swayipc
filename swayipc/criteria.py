from typing import Final, Optional
from swayipc import *

def safe_value(input:str):
    for c in ('\\', '[', ']', '"', '\''):
        input = input.replace(c, f"\\{c}")
    return input

FOCUSED:Final = "__focused__"

CRITERIA_FIELDS:Final = dict(
    app_id='app_id',
    con_id='con_id',
    con_mark='con_mark',
    pid='pid',
    shell='shell',
    title='title',
    urgent='urgent',
    workspace='workspace',
    x11_class='class',
    x11_id='id',
    x11_instance='instance',
    x11_window_role='window_role',
    x11_window_type='window_type',
)
    
def where(
    floating=False,
    tiling=False,
    app_id:Optional[str]=None,
    con_id:Optional[str|int]=None,
    con_mark:Optional[str]=None,
    pid:Optional[int]=None,
    shell:Optional[str]=None,
    title:Optional[str]=None,
    urgent:Optional[str]=None,
    workspace:Optional[str|int]=None,
    x11_class:Optional[str]=None,
    x11_id:Optional[int]=None,
    x11_instance:Optional[str]=None,
    x11_window_role:Optional[str]=None,
    x11_window_type:Optional[str]=None,
):
    result = []
    
    if floating:
        result.append('floating')
    if tiling:
        result.append('tiling')
    
    fields:Dict[str, str|int|None] = {
        'app_id': app_id,
        'con_id': con_id,
        'con_mark': con_mark,
        'pid': pid,
        'shell': shell,
        'title': title,
        'urgent': urgent,
        'workspace': workspace,
        'class': x11_class,
        'id': x11_id,
        'instance': x11_instance,
        'window_role': x11_window_role,
        'window_type': x11_window_type,
    }
    
    for field_name, field_value in fields.items():
        if field_value is not None:
            if isinstance(field_value, str):
                field_value = safe_value(field_value)
            result.append(f"{field_name}={field_value}")
    return f"[{' '.join(result)}]"
