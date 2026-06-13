import pyxel
import random


def generate_all_shapes(size, max_blocks):
    all_shapes = []

    for i in range(1, 2 ** (size * size)):
        arr = [[0] * size for _ in range(size)]
        b = i

        for y in range(size):
            for x in range(size):
                arr[y][x] = b % 2
                b //= 2

        block_count = sum(sum(row) for row in arr)

        if block_count == 0 or block_count > max_blocks:
            continue

        all_shapes.append(arr)

    return all_shapes


# テトリス7種（全回転反転状態で判定）
tetris_shapes_3x3 = [
    [[1, 1, 1], [0, 0, 0], [0, 0, 0]],
    [[1, 0, 0], [1, 0, 0], [1, 0, 0]],
    [[1, 1, 1], [0, 1, 0], [0, 0, 0]],
    [[1, 0, 0], [1, 1, 0], [1, 0, 0]],
    [[0, 1, 0], [1, 1, 1], [0, 0, 0]],
    [[0, 1, 0], [1, 1, 0], [0, 1, 0]],
    [[1, 1, 1], [1, 0, 0], [0, 0, 0]],
    [[1, 0, 0], [1, 0, 0], [1, 1, 0]],
    [[1, 0, 0], [1, 1, 1], [0, 0, 0]],
    [[0, 1, 1], [0, 1, 0], [0, 1, 0]],
    [[1, 1, 1], [0, 0, 1], [0, 0, 0]],
    [[0, 1, 0], [0, 1, 0], [1, 1, 0]],
    [[0, 0, 1], [1, 1, 1], [0, 0, 0]],
    [[1, 1, 0], [1, 0, 0], [1, 0, 0]],
    [[1, 1, 0], [1, 1, 0], [0, 0, 0]],
    [[0, 1, 1], [1, 1, 0], [0, 0, 0]],
    [[1, 1, 0], [0, 1, 1], [0, 0, 0]],
    [[0, 1, 1], [1, 1, 0], [0, 0, 0]],
]


def same_shape(a, b):
    for rot in range(4):
        for flip in [False, True]:
            tmp = [row[:] for row in a]

            # 回転
            for _ in range(rot):
                tmp = [list(reversed(col)) for col in zip(*tmp)]

            # 反転
            if flip:
                tmp = [row[::-1] for row in tmp]

            if tmp == b:
                return True

    return False


ALL_SHAPES = []
size = 3
max_blocks = 5
all_shapes = generate_all_shapes(size, max_blocks)

for shape in all_shapes:
    if any(same_shape(shape, ts) for ts in tetris_shapes_3x3):
        continue
    ALL_SHAPES.append(shape)


BOARD_WIDTH = 10
BOARD_HEIGHT = 30
FALL_SPEED = 10
SPRITE_COUNT = 8

BLOCK_SIZE = 8
BOARD_X = 16
BOARD_Y = 8

BOARD_BG_COLOR = 0       # 盤面背景色
BOARD_BORDER_COLOR = 7   # 盤面枠線色


class App:
    def __init__(self):
        pyxel.init(160, 360, title="Test")
        pyxel.load("tetris_py.pyxres")

        # music:0 と music:1 を順番に再生するための設定
        self.bgm_list = [0, 1]
        self.bgm_index = 0

        self.reset()

        # 最初のBGMを再生
        self.play_bgm()

        pyxel.run(self.update, self.draw)

    def play_bgm(self):
        # loop=False にするのがポイント
        # True にすると music:0 だけでループして music:1 に進まない
        pyxel.playm(self.bgm_list[self.bgm_index], loop=False)

    def update_bgm(self):
        # 4チャンネルすべて止まっていたら、今のmusicが終了したと判断
        if all(pyxel.play_pos(ch) is None for ch in range(4)):
            self.bgm_index += 1

            if self.bgm_index >= len(self.bgm_list):
                self.bgm_index = 0

            self.play_bgm()

    def reset(self):
        self.board = [[None] * BOARD_WIDTH for _ in range(BOARD_HEIGHT)]
        self.current_block = self.new_block()
        self.next_block = self.new_block()
        self.fall_timer = 0
        self.score = 0
        self.game_over = False

    def is_game_over(self):
        for y in range(4):
            for x in range(BOARD_WIDTH):
                if self.board[y][x] is not None:
                    return True

        return False

    def new_block(self):
        shape = random.choice(ALL_SHAPES)

        # 上の空行を削除
        top = 0
        while top < len(shape) and all(cell == 0 for cell in shape[top]):
            top += 1

        shape2 = shape[top:]

        # 左の空列を削除
        left = 0
        while shape2 and left < len(shape2[0]) and all(row[left] == 0 for row in shape2):
            left += 1

        shape2 = [row[left:] for row in shape2]

        # ランダムスプライト割当
        sprites = []

        for row in shape2:
            sprites.append([
                random.randint(0, SPRITE_COUNT - 1) if cell else None
                for cell in row
            ])

        return {
            "shape": shape2,
            "sprites": sprites,
            "x": BOARD_WIDTH // 2 - len(shape2[0]) // 2,
            "y": -len(shape2),
        }

    def update(self):
        # BGMの終了チェック
        self.update_bgm()

        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()

        if self.game_over:
            if pyxel.btnp(pyxel.KEY_R):
                self.reset()
            return

        if pyxel.btnp(pyxel.KEY_LEFT, 10, 1) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT, 10, 1):
            self.move_block(-1, 0)
            
        if pyxel.btnp(pyxel.KEY_RIGHT, 10, 1) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT, 10, 1):
            self.move_block(1, 0)
            
        if pyxel.btnp(pyxel.KEY_DOWN, 10, 1) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_DOWN, 10, 1):
            self.move_block(0, 1)
            
        if pyxel.btnp(pyxel.KEY_UP, 10, 10) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A, 10, 1) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_B, 10, 1):
            self.rotate_block()

        self.fall_timer += 1

        if self.fall_timer >= FALL_SPEED:
            self.fall_timer = 0

            if not self.move_block(0, 1):
                self.place_block()

                if self.is_game_over():
                    self.game_over = True

    def draw(self):
        pyxel.cls(0)

        self.draw_board_area()
        self.draw_board()

        if not self.game_over:
            self.draw_block(self.current_block)

        self.draw_next_block()

        pyxel.text(16, 340, f"Score: {self.score}", 7)

        if self.game_over:
            pyxel.text(52, 160, "Game Over!", pyxel.COLOR_RED)
            pyxel.text(34, 180, "Press R to Restart", 7)

    def draw_board_area(self):
        # 盤面の枠線
        pyxel.rect(
            BOARD_X - 1,
            BOARD_Y - 1,
            BOARD_WIDTH * BLOCK_SIZE + 2,
            BOARD_HEIGHT * BLOCK_SIZE + 2,
            BOARD_BORDER_COLOR,
        )

        # 盤面の背景
        pyxel.rect(
            BOARD_X,
            BOARD_Y,
            BOARD_WIDTH * BLOCK_SIZE,
            BOARD_HEIGHT * BLOCK_SIZE,
            BOARD_BG_COLOR,
        )

    def draw_board(self):
        for y in range(BOARD_HEIGHT):
            for x in range(BOARD_WIDTH):
                spr = self.board[y][x]

                if spr is not None:
                    pyxel.blt(
                        BOARD_X + x * BLOCK_SIZE,
                        BOARD_Y + y * BLOCK_SIZE,
                        0,
                        0,
                        spr * 8,
                        8,
                        8,
                        0,
                    )

    def draw_block(self, block):
        for y, row in enumerate(block["shape"]):
            for x, cell in enumerate(row):
                if cell:
                    spr = block["sprites"][y][x]

                    pyxel.blt(
                        BOARD_X + (block["x"] + x) * BLOCK_SIZE,
                        BOARD_Y + (block["y"] + y) * BLOCK_SIZE,
                        0,
                        0,
                        spr * 8,
                        8,
                        8,
                        0,
                    )

    def draw_next_block(self):
        pyxel.text(112, 8, "Next:", 7)

        for y, row in enumerate(self.next_block["shape"]):
            for x, cell in enumerate(row):
                if cell:
                    spr = self.next_block["sprites"][y][x]

                    pyxel.blt(
                        112 + x * BLOCK_SIZE,
                        24 + y * BLOCK_SIZE,
                        0,
                        0,
                        spr * 8,
                        8,
                        8,
                        0,
                    )

    def is_valid_move(self, block, dx, dy, shape=None):
        shape = shape or block["shape"]

        for block_y, row in enumerate(shape):
            for block_x, cell in enumerate(row):
                if cell:
                    board_x = block["x"] + block_x + dx
                    board_y = block["y"] + block_y + dy

                    if (
                        board_x < 0
                        or board_x >= BOARD_WIDTH
                        or board_y >= BOARD_HEIGHT
                        or (
                            board_y >= 0
                            and self.board[board_y][board_x] is not None
                        )
                    ):
                        return False

        return True

    def move_block(self, dx, dy):
        if self.is_valid_move(self.current_block, dx, dy):
            self.current_block["x"] += dx
            self.current_block["y"] += dy
            return True

        return False

    def rotate_block(self):
        old_shape = self.current_block["shape"]

        rotated_shape = [
            [old_shape[j][i] for j in range(len(old_shape))]
            for i in range(len(old_shape[0]) - 1, -1, -1)
        ]

        old_sprites = self.current_block["sprites"]

        rotated_sprites = [
            [old_sprites[j][i] for j in range(len(old_sprites))]
            for i in range(len(old_sprites[0]) - 1, -1, -1)
        ]

        if self.is_valid_move(self.current_block, 0, 0, rotated_shape):
            self.current_block["shape"] = rotated_shape
            self.current_block["sprites"] = rotated_sprites

    def place_block(self):
        for y, row in enumerate(self.current_block["shape"]):
            for x, cell in enumerate(row):
                if cell:
                    board_x = self.current_block["x"] + x
                    board_y = self.current_block["y"] + y

                    if board_y >= 0:
                        self.board[board_y][board_x] = self.current_block["sprites"][y][x]

        new_board = []
        cleared = 0

        for row in self.board:
            if all(cell is not None for cell in row):
                cleared += 1
            else:
                new_board.append(row)

        while len(new_board) < BOARD_HEIGHT:
            new_board.insert(0, [None] * BOARD_WIDTH)

        self.board = new_board
        self.score += cleared * 100

        self.current_block = self.next_block
        self.next_block = self.new_block()

        if not self.is_valid_move(self.current_block, 0, 0):
            self.game_over = True


App()
