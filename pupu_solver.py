import pygame as pg, itertools
import pygame.transform
import hashlib
import zlib
import argparse
import os
import json

VERSION = '0.1'
tiles = ['H', 'D', 'T', 'R', '1', 'S', '2', 'F']
glass = ['G']
walls = ['#', 'P']
IMAGE = b'x\x9c\xed\xd9;N\xc40\x10\x06\xe0\xff$\x9c\x80\x8a\x1a$*.@C\x1d\x8e@AG\xb77\xe0\x144[r\x128\x05\x1d\xa2^' \
        b'\xc2:;\x9a\xccx\xc6c\xc7\x8b\x10\xd9\x91\xb5J\x1c\xe3\x05\xfci\xfc\x08\xf0\x13\xaf\xf7gT\xc0\xc2\xaa\x171' \
        b'\xbc]\x8c\xc5i \xe2\xe5\xfak,\x91\x96\x8f\xb7\xb2\xf8\xb1\xdb\xdd\x88"\x1a\x9c_}T\x15\xfa\xc1g7\xa8\xd9\xd3' \
        b'\xe7{Uy\xd8\xec\xaa\xca\xf6\xf2N\x94\xf1Ku%\xd5\x8f\x9f\xc30\xf0\xff@\xba\x15\x95\xfc\x11\x1ft>\xf4V\xbd' \
        b'\xecd\x8f\xa1\x8aD\xc4\x83\x96\x10Qq<\x0f\xb0I\xf06\r\x1e\x82\xff\xb41\xfazHA\x95t\xbb\xc4\x03\xc7\x10$' \
        b'\x910\xf8$|\x0c\x0e\x89\xa2\x07\x8a8\x03\x1e>\x06,\xce\x0f\xd8\x0f:]\xd3-][\xbf\x98\x13Y\x0f8\x18\x10\xd7z' \
        b'\xd0\xfd2\xebYa\x88\x90(z\xf0\x07\xdd\x7f\x1a\xf7\x00\x9b\x04o\xa3G\xdc\xc10\xd6,\xf1\x00\x1b\x03}\x16' \
        b'\x13\x82(\xce\xbc\x00\x96\x16\xa8\xa6\xd9\x83\x85\xc1\'\xc11X$\x8a\x93B/\x0f\xc8\x91\x10\r\xf4\xb8[\x1eR' \
        b'\r\x1fk\xebK\xb3\x1e\xe0bh\xf6\xe0\xfc\xed\xd9\xbc\xd1\xe6\xc1\xc7\xe0\x90(z\x08\xae\x1b\xa9\x99\x06\xe0' \
        b'\x17\xdd\x95?M\xe8\xa1\xcfz\xa0\x9a6\x0f\x08`@\xab\x87\xaa\xf5d\x83\x87\x08\x86,\t\x8dA\x93\xf8}\x0f8\x90' \
        b'\xc8>\xf2\xb7\x15:\x1a< \x86\x01\xad\xeb\x07\xcc\'\x08q!\x9a\xd5z\x88c\xd0$N\x1eR8\xeb\x07\xd8\x99\x01j\x7f' \
        b'\x81@\xa2\xa0\x81\xb6.x\xd4N\x19\xa8I\x0e\xc2\x83\x85A\x90X\xad\x87\xf4\xc8\xc2\xd0\xdd\x03\xe6\x1bO\xfe' \
        b'\xe8\x18\x8b\x87xr8y\x88`X\xe2\xc1\xdao"\xb7\xbfH\xd1k\xa7\xd9\x86\x81\x93X\xe1z2U\x161\xa0i\xfd`\xcd\x0b' \
        b'\xe2TJ/2\xe3\x18\xa6>{\xac$\xdbR\xc4?\xdbo"\x96\x19\xd0{\xbf\x99B\'\x07\x8a8\x86\xa9\xab~\x18\xb2)bU\xe7' \
        b'Qp1,9\x8f\xd2\xf3\x85\x05@G\x1c\xc3\xd4y\xe0\xd8\xa1\xd6\x03\xd6w^\x8d\x12\x86\x85\xf9\xc1\xda_8\xf3\x05E' \
        b'\x1c\xc3\xd4s\'\x0cU$\xac(z\xf8\x9b\xef\xb3\x8a\x18\xf8\xacQ\x15\xd6\xdb\n]\xe3$\x8d8\x86\xa9\xb7\x9a\x03' \
        b'\xc9\xa0\x87\x14\xa7\xf7\xdd\xa2\x04\xd3\xc2V\xbd\xdf\x14I@l+\xe8\xf6\x1b\xc8Oq\xb3'
TITLESIZE = 40


def check_zoom(value):
    try:
        value = int(value)
        if not 0 < value <= 10:
            raise argparse.ArgumentTypeError('Value has to be greater than 0 and less than 10')
    except ValueError:
        raise argparse.ArgumentTypeError('The value has to be a number')
    return value

def read_puzzle(filename: str):
    """
    Read puzzle from file
    :param filename: Filename
    :return: width, height, puzzle as dict
    """
    ret = {}
    if not os.path.exists(filename):
        print('Puzzle does not exist')
        exit(0)
    lines = open(filename, 'r').readlines()
    lines = [line.strip() for line in lines]
    assert len(set([len(line) for line in lines])) == 1, 'Ungültiges Puzzle'
    for y, x in itertools.product(range(len(lines)), range(len(lines[0]))):
        if lines[y][x] == '.': continue
        ret[(x,y)] = lines[y][x]
    return len(lines[0]), len(lines), ret


def paint(puzzle: dict, text: str = None, movement: tuple = None):
    """
    Paint the puzzle
    :param puzzle: Puzzle
    :param text: Text to draw
    :param movement: (x,y,new_x,new_y) of the move
    :return: None
    """
    global size
    window.fill('black')

    #Paint text
    myfont = pg.font.SysFont('Arial', 12 * ZOOM)
    if text:
        text_surface = myfont.render(text, False, 'white')
        factor = TITLESIZE  / text_surface.get_height()
        text_surface = pg.transform.scale(text_surface,
                                          (text_surface.get_width() * factor, text_surface.get_height() * factor))
        window.blit(text_surface, (size[0]/2 - text_surface.get_rect().width/2,0))

    # Paint tiles
    for (x, y), tile in puzzle.items():
        if x == 5 and y == 0:
            pass
        if tile in tiles or tile in glass:
            number = tiles.index(tile)
        elif tile in walls:
            number = walls.index(tile) + 9
        else:
            continue
        window.blit(img, (x * 16 * ZOOM, y * 16 * ZOOM + TITLESIZE), (number * 16 * ZOOM, 0, 16 * ZOOM, 16 * ZOOM))

    #Paint Move direction
    if movement:
        x, y, direction = movement
        new_x = x - 1 if direction == 'L' else x + 1
        half_tile = 16 * ZOOM * 0.5
        pg.draw.line(window, 'green', (x * 16 * ZOOM + half_tile,
                                        y * 16 * ZOOM + TITLESIZE + half_tile),
                     (new_x * 16 * ZOOM + half_tile, y * 16 * ZOOM + TITLESIZE + half_tile), ZOOM)
    pg.display.flip()
    return
    while True:
        for ereignis in pg.event.get():
            if ereignis.type == pg.QUIT or ereignis.type == pg.KEYDOWN and ereignis.key == pg.K_ESCAPE: quit()
            if ereignis.type == pg.QUIT or ereignis.type == pg.KEYDOWN and ereignis.key == pg.K_RETURN: return


def gen_hash(puzzle: dict) -> str:
    """
    Generate MD5 of the puzzle
    :param puzzle: Puzzle
    :return: MD5
    """
    puzzle = dict(sorted(puzzle.items()))
    return hashlib.md5(str(puzzle).encode()).hexdigest()


def gen_move_string(x: int, y: int, direction: str) -> str:
    """
    Generate string that represents the move
    :param x: X-pos
    :param y: Y-Pos
    :param direction: Direction to move ('R'/'L')
    :return: Generated string
    """
    ret = f'{x:02}{y:02}{direction}'
    return ret


def fall(puzzle: dict):
    """
    Let fall all parts
    :param puzzle: Puzzle
    :return: New puzzle
    """
    movable_tiles = tiles + glass
    fallen = False
    newpuzz = puzzle.copy()
    for y,x in itertools.product(range(height-1, -1, -1), range(width)):
        # If pos is a hole
        if not (x,y) in newpuzz:
            # Look from down to up if there is a tile flying
            for temp_y in range(y-1, -1, -1):
                # If there is a part, let it fall down
                if newpuzz.get((x,temp_y), ' ') in movable_tiles:
                    newpuzz[(x,y)] = newpuzz.pop((x,temp_y))
                    fallen = True
                    break
                # If there is a wall, stop. Otherwise tiles will fall through the wall
                if newpuzz.get((x,temp_y), ' ') in walls:
                    break
    return newpuzz, fallen


def delete(puzzle: dict):
    """
    Delete neighbours
    :param puzzle: Puzzle
    :return: New puzzle
    """
    deleted = False
    newpuzz = puzzle.copy()
    deletable = []
    # Collect all deletable tiles
    for (x,y), tile in newpuzz.items():
        # If it is a deletable tile
        if tile in tiles:
            if (newpuzz.get((x-1,y), " ") == tile or
                newpuzz.get((x+1,y), " ") == tile or
                newpuzz.get((x,y-1), " ") == tile or
                newpuzz.get((x,y+1), " ") == tile):
                deletable.append((x,y))
                deleted = True

    # Now apply delete
    for d in deletable:
        newpuzz.pop(d)
    return newpuzz, deleted


def fall_and_delete(puzzle: dict) -> dict:
    """
    Let fall all possible parts and delete neighbours
    :param puzzle: Puzzle
    :return: New puzzle
    """
    newpuzz = puzzle.copy()
    newpuzz, _ = fall(newpuzz)
    deleted = True
    fallen = True
    while deleted or fallen:
        newpuzz, deleted = delete(newpuzz)
        if not deleted: break
        newpuzz, fallen = fall(newpuzz)
    return newpuzz


def check(puzzle: dict):
    """
    Check if puzzle is won or loosed
    :param puzzle: Puzzle
    :return: win, loose
    """
    game_tiles = [t for t in puzzle.values()]
    won = True
    loose = False
    for t in tiles:
        if game_tiles.count(t) > 0: won = False
        if game_tiles.count(t) == 1: loose = True
        if won == False or loose == True: break
    return won, loose


def show_solution(puzzle: dict, solutions: list):
    """
    Show the given solution
    :param puzzle: Puzzle
    :param solutions: List of solution moves
    :return: None
    """
    newpuzz = puzzle.copy()
    newsolutions_text = []
    screens = [puzzle]
    temp_solutions = solutions.copy()
    paint(newpuzz)
    for (x,y,direction) in solutions:
        if direction == 'L':
            new_x = x - 1
        else:
            new_x = x + 1
        newpuzz[(new_x, y)] = newpuzz.pop((x,y))
        newpuzz = fall_and_delete(newpuzz)
        screencopy = newpuzz.copy()
        screens.append(screencopy)
        newsolutions_text.append(f'X:{x + 1} / Y:{y + 1} {direction}')
    newsolutions_text.append('')
    temp_solutions.append((-1, 0, 'L'))

    screen_num = 0
    while True:
        paint(screens[screen_num], newsolutions_text[screen_num], temp_solutions[screen_num])
        for ereignis in pg.event.get():
            if ereignis.type == pg.QUIT or ereignis.type == pg.KEYDOWN and ereignis.key == pg.K_ESCAPE: quit()
            if ereignis.type == pg.KEYDOWN and ereignis.key == pg.K_RIGHT:
                if screen_num < len(screens)-1: screen_num += 1
            if ereignis.type == pg.KEYDOWN and ereignis.key == pg.K_LEFT:
                if screen_num > 0: screen_num -= 1


def solve(puzzle: dict, all_solutions: bool = False, debug: bool = False):
    """
    Solve the puzzle
    :param puzzle: Puzzle
    :param all_solutions: Return all possible solutions?
    :param debug: Show debug
    :return: number of tries, [list of solutions]
    """
    queue = [[puzzle, []]]
    hashes = {gen_hash(puzzle): []}
    solutions = []
    while queue:
        puzz, moves = queue.pop()
        for (x,y), tile in puzz.items():
            for ereignis in pg.event.get():
                if ereignis.type == pg.QUIT or ereignis.type == pg.KEYDOWN and ereignis.key == pg.K_ESCAPE: quit()
            if tile in tiles or tile in glass:
                for diff_x, direction in [(-1, 'L'), (1, 'R')]:
                    # Step left
                    if not (x + diff_x,y) in puzz:
                        newpuzz = puzz.copy()
                        newpuzz[(x + diff_x,y)] = newpuzz.pop((x,y))
                        newhash = gen_hash(newpuzz)
                        newmoves = moves.copy()
                        newmoves.append((x, y, direction))
                        if newhash in hashes:
                            # If old hash was reached with more moves, delete it
                            if len(newmoves) < len(hashes[newhash]): del hashes[newhash]
                        if not newhash in hashes:
                            newpuzz = fall_and_delete(newpuzz)
                            won, loosed = check(newpuzz)
                            if won:
                                solutions.append(newmoves)
                                if all_solutions:
                                    continue
                                else:
                                    return len(hashes), [newmoves]
                            if not loosed:
                                hashes[newhash] = moves
                                queue.append([newpuzz, newmoves])
                                if debug: paint(newpuzz, f'{str(len(queue))}/{len(hashes)}')
    return len(hashes), solutions


def get_best_solution(solutions: list[list]) -> list:
    counts = [len(s) for s in solutions]
    return solutions[counts.index(min(counts))]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=f'Solver for PUPU-puzzles v{VERSION}. Written by 64erGrufti in Nov. 2024.\n'
                                                 'The file has to be in the format:\n'
                                                 'PPPPPPP\n'
                                                 'P#..2#P\n'
                                                 'P#.2R#P\n'
                                                 'P#.R##P\n'
                                                 'PPPPPPP\n\n'
                                                 'With tiles:\n'
                                                 '.: Empty      H: Heart    D: Diamond\n'
                                                 'T: Triangle   R: Ring     1: Cross#1\n'
                                                 'S: Sandglass  2: Cross#2  F: Frame\n'
                                                 'G: Glass      #: Wall     P: Pattern\n\n'
                                                 'Navigate with cursor right and left through the solution. ESC to exit',
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('puzzle', help='Textfile with puzzle')
    parser.add_argument('-z', metavar='FACTOR', type=check_zoom, default=5, help='Set zoom factor (default: 5)')
    parser.add_argument('-s', metavar='FILE', help='Display already calculated solution')
    parser.add_argument('-d', action='store_true', default=False, help='debug')
    parser.add_argument('-f', action='store_true', default=False,
                        help='Show the first found solution\n(otherwise the shortest of all possible solutions is shown)')
    args = parser.parse_args()

    ZOOM = args.z
    width, height, puzz = read_puzzle(args.puzzle)

    pg.init()
    pg.display.set_caption(f'PUPU solver v{VERSION}')
    pg.font.init()
    img = pg.image.fromstring(zlib.decompress(IMAGE), (176,16), "RGB")
    img = pygame.transform.scale_by(img, ZOOM)

    size = width * 16 * ZOOM, height * 16 * ZOOM + TITLESIZE
    window = pg.display.set_mode(size)

    if not args.s:
        tries, solutions = solve(puzz, not args.f, args.d)
    else:
        if not os.path.exists(args.s):
            print('Solution file does not exist')
            exit(0)
        solutions = [json.loads(open(args.s, 'r').read())]

    if len(solutions) == 0:
        print('Sorry, no solutions possible')
    else:
        solution = get_best_solution(solutions)
        # If solution was not given, save it
        if not args.s:
            outputname = list(os.path.splitext(args.puzzle))
            outputname[-1] = '.sol'
            open(''.join(outputname), 'w').write(json.dumps(solution))
        show_solution(puzz, solution)


