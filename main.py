
import tkinter as tk
import random


# =====================================================
# НАСТРОЙКИ ИГРЫ
# =====================================================

CELL = 32
TICK = 130

DIRS = [
    (0, -1),
    (0, 1),
    (-1, 0),
    (1, 0)
]

MAZE_MAP = [
    "###################",
    "#........#........#",
    "#.##.###.#.###.##.#",
    "#.................E",
    "#.##.#.##.##.#.##.#",
    "#....#..GGG..#....#",
    "####.#.#####.#.####",
    "#.................#",
    "#.##.###.#.###.##.#",
    "#........P........#",
    "###################",
]

GHOST_COLORS = [
    "#ff2a2a",
    "#ff8ad8",
    "#2affff"
]


# =====================================================
# 1. АТА-АНА КЛАСС: GAMEOBJECT
# =====================================================

class GameObject:
    """Барлық ойын объектілерінің ата-ана класы."""

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def update(self, game):
        pass

    def draw(self, canvas):
        pass


# =====================================================
# 2. CHARACTER КЛАСЫ
# =====================================================

class Character(GameObject):
    """Ойын кейіпкерлерінің ортақ класы."""

    def __init__(self, x, y):
        super().__init__(x, y)

        self.start_x = x
        self.start_y = y

        self.px = x
        self.py = y

        self.dx = 0
        self.dy = 0

    def can_move(self, dx, dy, maze):
        return not maze.is_wall(
            self.x + dx,
            self.y + dy
        )

    def remember(self):
        self.px = self.x
        self.py = self.y

    def reset(self):
        self.x = self.start_x
        self.y = self.start_y

        self.px = self.x
        self.py = self.y

        self.dx = 0
        self.dy = 0

    def update(self, game):
        pass

    def draw(self, canvas):
        pass


# =====================================================
# 3. PLAYER КЛАСЫ
# =====================================================

class Player(Character):
    """Pac-Man ойыншысының класы."""

    ANGLES = {
        (1, 0): 0,
        (0, -1): 90,
        (-1, 0): 180,
        (0, 1): 270
    }

    def __init__(self, x, y):
        super().__init__(x, y)

        self.want_dx = 0
        self.want_dy = 0

        self.face = 0
        self.mouth = True

    def set_direction(self, dx, dy):
        self.want_dx = dx
        self.want_dy = dy

    def reset(self):
        super().reset()

        self.want_dx = 0
        self.want_dy = 0

    def update(self, game):
        self.remember()

        maze = game.maze

        # Қалаған бағытқа бұрылу
        if (self.want_dx, self.want_dy) != (0, 0):
            if self.can_move(
                self.want_dx,
                self.want_dy,
                maze
            ):
                self.dx = self.want_dx
                self.dy = self.want_dy

        # Ойыншының қозғалысы
        if (self.dx, self.dy) != (0, 0):
            if self.can_move(self.dx, self.dy, maze):
                self.x += self.dx
                self.y += self.dy

                self.face = self.ANGLES[(self.dx, self.dy)]
                self.mouth = not self.mouth

    def reached_exit(self, maze):
        return (
            maze.exit.is_open()
            and maze.is_exit(self.x, self.y)
        )

    def draw(self, canvas):
        half = 45 if self.mouth else 12

        canvas.create_arc(
            self.x * CELL + 3,
            self.y * CELL + 3,
            (self.x + 1) * CELL - 3,
            (self.y + 1) * CELL - 3,
            start=self.face + half,
            extent=360 - 2 * half,
            fill="#ffe600",
            outline="#ffe600"
        )


# =====================================================
# 4. GHOST КЛАСЫ
# =====================================================

class Ghost(Character):
    """Pac-Man-ды қуа алатын елес."""

    def __init__(self, x, y, color):
        super().__init__(x, y)

        self.color = color

    # Әдісті қайта анықтау (override)
    def can_move(self, dx, dy, maze):
        nx = self.x + dx
        ny = self.y + dy

        return (
            not maze.is_wall(nx, ny)
            and not maze.is_exit(nx, ny)
        )

    def update(self, game):
        self.remember()

        # Елестер әр үшінші қадамда қозғалады
        if game.ticks % 3 != 0:
            return

        options = [
            d for d in DIRS
            if self.can_move(d[0], d[1], game.maze)
        ]

        if not options:
            return

        # Кері бұрылмауға тырысады
        if len(options) > 1:
            back = (-self.dx, -self.dy)

            options = [
                d for d in options
                if d != back
            ] or options

        # 60% ойыншыға қарай, 40% кездейсоқ
        if random.random() < 0.6:
            best = min(
                options,
                key=lambda d: (
                    abs(self.x + d[0] - game.player.x)
                    + abs(self.y + d[1] - game.player.y)
                )
            )
        else:
            best = random.choice(options)

        self.dx, self.dy = best

        self.x += self.dx
        self.y += self.dy

    def draw(self, canvas):
        x0 = self.x * CELL + 3
        y0 = self.y * CELL + 3

        x1 = (self.x + 1) * CELL - 3
        y1 = (self.y + 1) * CELL - 3

        mid = (y0 + y1) / 2

        canvas.create_oval(
            x0, y0, x1, y1,
            fill=self.color,
            outline=""
        )

        canvas.create_rectangle(
            x0, mid, x1, y1,
            fill=self.color,
            outline=""
        )

        width = x1 - x0

        for ex in (x0 + width * 0.3, x0 + width * 0.7):

            canvas.create_oval(
                ex - 4, y0 + 7,
                ex + 4, y0 + 17,
                fill="white",
                outline=""
            )

            canvas.create_oval(
                ex - 2 + self.dx * 2,
                y0 + 10 + self.dy * 2,
                ex + 2 + self.dx * 2,
                y0 + 14 + self.dy * 2,
                fill="#1a1aa6",
                outline=""
            )


# =====================================================
# 5. WALL КЛАСЫ
# =====================================================

class Wall(GameObject):
    """Лабиринт қабырғасы."""

    def __init__(self, x, y):
        super().__init__(x, y)

    def update(self, game):
        pass

    def draw(self, canvas):
        canvas.create_rectangle(
            self.x * CELL + 1,
            self.y * CELL + 1,
            (self.x + 1) * CELL - 1,
            (self.y + 1) * CELL - 1,
            fill="#1a1aa6",
            outline="#4d4dff"
        )


# =====================================================
# 6. DOT КЛАСЫ
# =====================================================

class Dot(GameObject):
    """Жиналатын нүктелер."""

    def __init__(self, x, y):
        super().__init__(x, y)

    def update(self, game):
        pass

    def draw(self, canvas):
        cx = self.x * CELL + CELL // 2
        cy = self.y * CELL + CELL // 2

        canvas.create_oval(
            cx - 3,
            cy - 3,
            cx + 3,
            cy + 3,
            fill="#ffd9a0",
            outline=""
        )


# =====================================================
# 7. EXIT КЛАСЫ
# =====================================================

class Exit(GameObject):
    """Ойыннан шығу есігі."""

    def __init__(self, x, y):
        super().__init__(x, y)

        self.open = False

    def unlock(self):
        self.open = True

    def is_open(self):
        return self.open

    def update(self, game):
        pass

    def draw(self, canvas):
        color = "#2ecc71" if self.open else "#8b1a1a"
        text = "EXIT" if self.open else "LOCK"

        canvas.create_rectangle(
            self.x * CELL + 2,
            self.y * CELL + 2,
            (self.x + 1) * CELL - 2,
            (self.y + 1) * CELL - 2,
            fill=color,
            outline="white",
            width=2
        )

        canvas.create_text(
            self.x * CELL + CELL // 2,
            self.y * CELL + CELL // 2,
            text=text,
            fill="white",
            font=("Arial", 8, "bold")
        )


# =====================================================
# 8. MAZE КЛАСЫ
# =====================================================

class Maze:
    """Лабиринтті құру және басқару."""

    def __init__(self, layout):
        self.walls = []
        self.wall_cells = set()

        self.dots = {}

        self.exit = None

        self.player_start = (1, 1)
        self.ghost_starts = []

        self.rows = len(layout)
        self.cols = len(layout[0])

        self.objects = []

        self.build(layout)

    def build(self, layout):

        for y, row in enumerate(layout):
            for x, char in enumerate(row):

                if char == "#":
                    wall = Wall(x, y)

                    self.walls.append(wall)
                    self.wall_cells.add((x, y))
                    self.objects.append(wall)

                elif char == ".":
                    dot = Dot(x, y)

                    self.dots[(x, y)] = dot
                    self.objects.append(dot)

                elif char == "P":
                    self.player_start = (x, y)

                elif char == "G":
                    self.ghost_starts.append((x, y))

                elif char == "E":
                    self.exit = Exit(x, y)
                    self.objects.append(self.exit)

    def is_wall(self, x, y):

        if (x, y) in self.wall_cells:
            return True

        if (
            not self.exit.is_open()
            and self.is_exit(x, y)
        ):
            return True

        return False

    def is_exit(self, x, y):
        return (
            x == self.exit.x
            and y == self.exit.y
        )

    def eat_dot(self, x, y):

        dot = self.dots.pop((x, y), None)

        if dot is None:
            return False

        self.objects.remove(dot)

        # Соңғы нүкте жиналғанда есік ашылады
        if not self.dots:
            self.exit.unlock()

        return True


# =====================================================
# 9. GAME КЛАСЫ
# =====================================================

class Game:
    """Ойынның негізгі басқару класы."""

    def __init__(self, root):
        self.root = root

        root.title("Pacman - URBAN")
        root.resizable(False, False)

        self.info = tk.Label(
            root,
            font=("Arial", 14, "bold"),
            bg="black",
            fg="white",
            anchor="w",
            padx=10
        )

        self.info.pack(fill="x")

        maze = Maze(MAZE_MAP)

        self.canvas = tk.Canvas(
            root,
            width=maze.cols * CELL,
            height=maze.rows * CELL,
            bg="black",
            highlightthickness=0
        )

        self.canvas.pack()

        root.bind("<Key>", self.on_key)

        self.new_game()
        self.tick()

    def new_game(self):

        self.maze = Maze(MAZE_MAP)

        self.player = Player(
            *self.maze.player_start
        )

        self.ghosts = [
            Ghost(
                x,
                y,
                GHOST_COLORS[i % len(GHOST_COLORS)]
            )
            for i, (x, y) in enumerate(
                self.maze.ghost_starts
            )
        ]

        # Әртүрлі объектілер бір тізімде сақталады
        self.objects = self.maze.objects

        self.objects.append(self.player)
        self.objects.extend(self.ghosts)

        self.score = 0
        self.lives = 3
        self.ticks = 0

        self.state = "play"

    def on_key(self, event):

        keys = {
            "Up": (0, -1),
            "Down": (0, 1),
            "Left": (-1, 0),
            "Right": (1, 0)
        }

        if event.keysym in keys:

            if self.state == "play":
                self.player.set_direction(
                    *keys[event.keysym]
                )

        elif event.keysym in ("r", "R"):

            self.new_game()
            self.draw()

    def check_collision(self):

        p = self.player

        for ghost in self.ghosts:

            # Бір ұяшықта кездесу
            if (ghost.x, ghost.y) == (p.x, p.y):
                return True

            # Бір-бірінің орнын ауыстырып өту
            if (
                (ghost.x, ghost.y) == (p.px, p.py)
                and
                (p.x, p.y) == (ghost.px, ghost.py)
            ):
                return True

        return False

    def lose_life(self):

        self.lives -= 1

        if self.lives <= 0:
            self.state = "lost"

        else:
            self.player.reset()

            for ghost in self.ghosts:
                ghost.reset()

    def tick(self):

        if self.state == "play":

            self.ticks += 1

            # Полиморфизм:
            # Әр объект өзінің update әдісін орындайды
            for obj in self.objects:
                obj.update(self)

            # Нүктелерді жинау
            if self.maze.eat_dot(
                self.player.x,
                self.player.y
            ):
                self.score += 10

            # Жеңу шарты
            if self.player.reached_exit(self.maze):
                self.state = "won"

            # Жеңілу шарты
            elif self.check_collision():
                self.lose_life()

        self.draw()

        self.root.after(TICK, self.tick)

    def draw(self):

        self.canvas.delete("all")

        # Барлық объектілер бір циклмен салынады
        for obj in self.objects:
            obj.draw(self.canvas)

        if self.maze.exit.is_open():
            hint = "ШЫҒУ АШЫЛДЫ! Қаш!"
        else:
            hint = f"Қалған нүкте: {len(self.maze.dots)}"

        self.info.config(
            text=(
                f"Ұпай: {self.score}   "
                f"Жан: {'♥ ' * self.lives}   "
                f"{hint}"
            )
        )

        # Ойынның аяқталу экраны
        if self.state in ("won", "lost"):

            width = self.maze.cols * CELL
            height = self.maze.rows * CELL

            if self.state == "won":
                title = "Жеңіс! Сіз қашып шықтыңыз!"
                color = "#27ae60"

            else:
                title = "Ойын аяқталды!"
                color = "#c0392b"

            self.canvas.create_rectangle(
                width // 2 - 200,
                height // 2 - 50,
                width // 2 + 200,
                height // 2 + 50,
                fill="white",
                outline=color,
                width=3
            )

            self.canvas.create_text(
                width // 2,
                height // 2 - 12,
                text=title,
                font=("Arial", 16, "bold"),
                fill=color
            )

            self.canvas.create_text(
                width // 2,
                height // 2 + 20,
                text="Қайта ойнау үшін R басыңыз",
                font=("Arial", 11),
                fill="#555"
            )


# =====================================================
# ОЙЫНДЫ ІСКЕ ҚОСУ
# =====================================================

if __name__ == "__main__":

    root = tk.Tk()

    game = Game(root)

    root.mainloop()
