import pygame as pg
from data.asset_handler import AssetHandler
from data import basic, display, gui, text, world, input_handler


class Game:
    def __init__(self):
        self.settings = basic.load_ini('data/settings.ini')
        pg.mixer.pre_init()
        pg.init()
        self.clock = pg.time.Clock()
        self.paused, self.__skip = False, 0

        # TODO LAST: LOADING SCREEN HERE, MAYBE ^^
        res = self.settings.getint('settings', 'res_x', fallback=0), self.settings.getint('settings', 'res_y', fallback=0)
        self.display = display.DisplayHandler(self,res=res, flags=self.settings.getint('settings', 'display_flags', fallback=pg.FULLSCREEN))
        AssetHandler.init()
        text.load('data/assets/font')
        self.guis = gui.UIHandler(self, 'data/assets/gui')
        self.camera = self.display.renderer.camera
        self.world = world.World(self)
        self.input = input_handler.InputHandler(self)

        self.target_fps = 150
        self.d_time = 1 / self.target_fps
        self.speed_modifier = 1.0

        self.world.load('test', 0, 0)
        self.world.spawn()

        self.clock.tick(24)     # DELAY TO SMOOTH AFTER LOADING

    def update(self):

        self.d_time = self.clock.tick(self.target_fps) / 1000 * 60 * self.speed_modifier
        outputs = []
        for e in pg.event.get():
            if e.type == pg.QUIT:
                self.quit()
                return 0
            elif e.type == pg.WINDOWRESIZED:
                self.skip()
                self.display.resize((e.x, e.y))
            elif e.type == pg.WINDOWMOVED:
                self.skip(30)

            outputs.extend(self.input.feed(e))

        for code, data in outputs:
            c_target = code.split('.')[0]
            code = '.'.join(code.split('.')[1:])
            if c_target == 'gui':
                self.guis.feed(code, data)
            elif c_target == 'game':
                self.world.feed(code, data)

        self.guis.update(self.d_time)

        if self.paused or bool(self.__skip):  # RETURN WITHOUT UPDATING IF PAUSED
            if self.__skip > 0: self.__skip -= 1
            return 1

        # UPDATE HANDLERS AND CONTAINERS

        self.world.update(self.d_time)
        self.camera.update(self.d_time)

        self.display.draw()
        return 1

    def skip(self, num=1):
        self.__skip = num

    def pause(self, force=False):
        if force: self.paused = False
        self.paused = not self.paused

    def quit(self):
        basic.save_ini('data/settings.ini', self.settings)
