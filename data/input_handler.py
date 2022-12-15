import pygame as pg


class InputHandler:
    def __init__(self, g) -> None:
        self.g = g
        if not g.settings.has_section('keybinds'):
            g.settings.add_section('keybinds')
        self.keybinds = g.settings['keybinds']
        self.active = True # TODO LAST: SET TO FALSE WHEN COMPLETE FOR MAIN MENU LOADING

    def feed(self, e: pg.event.Event) -> list[tuple[str, dict]]:
        output = list()
        pre_bind = 'null'
        c_event = 'null'
        data = {}
        if e.type == pg.MOUSEMOTION:
            pre_bind = 'mouse'
            c_event = 'motion'
            data.update( {'x': e.pos[0], 'y': e.pos[1]} )

        elif e.type == pg.KEYUP or e.type == pg.KEYDOWN:
            pre_bind = pg.key.name(e.key)
            if e.type == pg.KEYUP: c_event = 'up'
            else: c_event = 'down'
            data.update( {'mod': e.mod} )

        elif e.type == pg.MOUSEBUTTONUP or e.type == pg.MOUSEBUTTONDOWN:
            pre_bind = 'mouse' + str(e.button)
            if e.type == pg.MOUSEBUTTONUP: c_event = 'up'
            else: c_event = 'down'

        elif e.type == pg.MOUSEWHEEL:
            pre_bind = 'mouse'
            c_event = 'scroll'
            data.update( {'y': e.y} )

        GUI_output = 'gui.' + pre_bind + '.' + c_event
        output.append( (GUI_output, data) )
        if self.active and self.keybinds.get(pre_bind, fallback=False):
            post_bind = self.keybinds[pre_bind]
            GAME_output = 'game.' + post_bind + '.' + c_event
            output.append( (GAME_output, data) )
        return output
