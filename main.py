from game import Game

g = Game()

def test():
    while 1:
        if not g.update(): break

if __name__ == '__main__':
    test()
