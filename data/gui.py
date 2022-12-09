import os
from . import basic
from .gui_elements import *


class UIHandler:
    def __init__(self, g, path: str) -> None:
        self.g = g
        self.gui_db = {}
        self.loaded = {}
        self.hidden = {}

        os.makedirs(path, exist_ok=True)
        for dir in os.listdir(path):
            if dir.endswith('.json'):
                gui_type, gui_dict = basic.load_json(path + '/' + dir)
                gui_type = globals().get(gui_type, GUI)
                ele_list = []
                d = gui_dict.get('elements', [])
                for e_type in d:
                    data = d[e_type]
                    e_type = globals().get(e_type, GUIAnimatedElement)
                    if 'a_id' in data:
                        a_id = data.pop('a_id')
                        data['anim'] = AssetHandler.get_anim(a_id)
                    new = e_type()
                    for k in data:
                        if hasattr(new, k): setattr(new, k, data[k])
                    ele_list.append(new)
                gui_dict['elements'] = ele_list
                self.gui_db[dir.split('.')[0]] = gui_type(self.g, **gui_dict)

        pg.mouse.set_visible(False)
        self.cursor = self.gui_db.get('cursor', GUI(self.g))

    def __getitem__(self, item: str) -> GUI or None:
        if item in self.loaded: return self.loaded[item]
        return None

    def update(self, d_time=1.0):
        for ui in self.loaded:
            self[ui].update(d_time=d_time)

    def draw(self, surf: pg.Surface):
        for ui_id in self.loaded:
            self[ui_id].draw(surf)
        self.cursor.draw(surf)

    def feed(self, code: str, data: dict) -> None:
        for ui in self.loaded:
            if self[ui].active:
                self[ui].listen(code, data)
                if code.startswith('mouse') and code.endswith(('.down', '.up')):
                    self[ui].click(self.cursor.pos, code, data)
        self.cursor.listen(code, data)

    def add_layer(self, ui_id: str) -> None:
        if ui_id not in self.gui_db: return
        self.loaded.update({ui_id: self.gui_db[ui_id]})

    def remove_layer(self, ui_id: str) -> None:
        if ui_id not in self.loaded: return
        self.loaded.pop(ui_id)

    def hide_layer(self, ui_id: str) -> None:
        if ui_id not in self.loaded:
            if ui_id not in self.gui_db: return
            self.add_layer(ui_id)
        self.hidden.update( {ui_id: self.loaded.pop(ui_id)} )

    def unhide_layer(self, ui_id: str) -> None:
        if ui_id not in self.hidden: return
        self.loaded.update( {ui_id: self.hidden.pop(ui_id)} )
