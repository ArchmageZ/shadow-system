import pygame, os


def load(path):
    fonts = dict()
    for font in os.listdir(path):
        font_img = pygame.image.load(path + '/' + font).convert()
        font = font.removesuffix('.png')
        last_x = 0
        font_chars = []
        font_spacing = []
        for x in range(font_img.get_width()):
            if font_img.get_at((x, 0))[0] == 127:
                font_chars.append(font_img.subsurface(pygame.Rect(last_x, 0, x - last_x, font_img.get_height())).copy())
                font_spacing.append(x - last_x)
                last_x = x + 1
        for char in font_chars:
            char.set_colorkey((255,255,255))

        new_font = Font()
        new_font.characters, new_font.spacing, new_font.line_height = font_chars, font_spacing, font_img.get_height()
        fonts.update({font: new_font})
    return fonts


class Font:
    def __init__(self):
        self.order = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
                      'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
                      '.', '-', ',', ':', '+', '\'', '!', '?', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '(', ')', '/', '_', '=', '\\', '[', ']', '*', '"', '<', '>', ';']
        self.characters = []
        self.spacing = []
        self.line_height = 0
        self.space_width = 2
        self.def_spacing = 1
        self.line_spacing = 2

    def width(self, text):
        text_width = 0
        for char in text:
            if char == ' ':
                text_width += self.space_width + self.def_spacing
            else:
                text_width += self.spacing[self.order.index(char)] + self.def_spacing
        return text_width

    def height(self):
        return self.line_height

    def write(self, surf, pos, text, line_width=0, color=None):
        text = str(text)
        x_offset = 0
        y_offset = 0
        if line_width != 0:
            spaces = []
            x = 0
            for i, char in enumerate(text):
                if char == ' ':
                    spaces.append((x, i))
                    x += self.space_width + self.def_spacing
                else:
                    x += self.spacing[self.order.index(char)] + self.def_spacing
            line_offset = 0
            for i, space in enumerate(spaces):
                if (space[0] - line_offset) > line_width:
                    line_offset += spaces[i - 1][0] - line_offset
                    if i != 0:
                        text = text[:spaces[i - 1][1]] + '\n' + text[spaces[i - 1][1] + 1:]
        for char in text:
            if char not in ['\n', ' ']:
                char_image = self.characters[self.order.index(char)].copy()
                if color is not None:
                    pass # swap_color(char_image, (0, 0, 0), color)
                surf.blit(char_image, (x_offset + pos[0], y_offset + pos[1]))
                x_offset += self.spacing[self.order.index(char)] + self.def_spacing
            elif char == ' ':
                x_offset += self.space_width + self.def_spacing
            else:
                y_offset += self.line_spacing + self.line_height
                x_offset = 0
