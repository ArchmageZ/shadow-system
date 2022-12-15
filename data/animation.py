import pygame as pg, random as ran


class Animation(object):
    def __init__(self, col, a_id: str, frame_times: list[int], tags: dict):
        self.c = col
        self.id = a_id
        self.current = 0
        self.timer = 0.0
        self.times = frame_times
        self.inc = 1
        self.tags = tags

    def update(self, d_time=1.0):
        if self.timer >= self.times[self.current]:
            self.timer = 0.0
            self.current += self.inc
        else:
            self.timer += d_time
        if self.current >= len(self.times) or self.current < 0:
            self.current = len(self.times) - 1 if self.current >= len(self.times) else 0
            if 'on_end' in self.tags:
                func = getattr(self, self.tags['on_end'], self.loop)
                r = func()
                if r: return False  # DENY THE ANIMATION HAS ENDED IF THE TAG CONFIRMS
            if 'next' in self.tags:
                return not self.c.set_anim(self.tags['next'])
            self.current = 0
            self.timer = 0.0
            return True  # CONFIRM THE ANIMATION HAS ENDED
        else:
            # TODO: ADDITIONAL TAG LOGIC HERE
            return False # DENY THE ANIMATION HAS ENDED

    def loop(self):
        self.current = 0
        self.timer = 0.0
        return True  # CONFIRM LOOP

    def reverse(self, once=True):
        if not (once and self.inc < 0):
            self.inc *= -1
            self.current += self.inc
            return True  # CONFIRM REVERSAL
        return False     # DENY REVERSAL IF ALREADY DONE ONCE

    def do_idle(self, var='idle'):
        count = len( [a_id for a_id in self.c.animations if a_id.startswith(var)] )
        return self.c.set_anim( var + '_' + str( ran.randint(0, count-1) ) )


class AnimationCollection(object):
    def __init__(self, id: str, anim_dict: dict):
        self.id = id
        self.animations = {}
        for a_id in anim_dict:
            self.animations.update( {a_id: Animation( self, a_id, anim_dict[a_id][0], anim_dict[a_id][-1])} )
        if len(self.animations) > 0:
            self.current = [a_id for a_id in self.animations][0]
        else: self.current = None
        self.animation_finished = False

    def update(self, d_time=1.0):
        if self.current:
            self.animation_finished = self.animations[self.current].update(d_time=d_time)
            return self.animation_finished
        return False

    @property
    def draw_result(self) -> tuple[str, str, int]:
        if self.current:
            return self.id, self.current, self.animations[self.current].current
        return "", "", 0

    def set_anim(self, new: str, reset=True):
        if new in self.animations and self.current != new and not self.animations[new].tags.get('forced', False):
            self.current = new
            if reset:
                self.animations[new].current = 0
                self.animations[new].timer = 0.0
                self.animations[new].inc = 1
            return True
        return False
