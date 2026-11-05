"""Игра «Змейка»."""

from random import choice, randint

import pygame as pg

SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Константа для центра экрана (исправлено)
CENTER_X = (GRID_WIDTH // 2) * GRID_SIZE
CENTER_Y = (GRID_HEIGHT // 2) * GRID_SIZE

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

BOARD_BACKGROUND_COLOR = (0, 0, 0)
BORDER_COLOR = (93, 216, 228)
APPLE_COLOR = (255, 0, 0)
SNAKE_COLOR = (0, 255, 0)

SPEED = 20

KEY_DIRECTIONS = {
    pg.K_UP: UP,
    pg.K_DOWN: DOWN,
    pg.K_LEFT: LEFT,
    pg.K_RIGHT: RIGHT,
}

# Множество всех возможных ячеек на поле (для быстрого поиска свободных)
ALL_CELLS = set(
    (x * GRID_SIZE, y * GRID_SIZE)
    for x in range(GRID_WIDTH)
    for y in range(GRID_HEIGHT)
)

screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pg.display.set_caption('Змейка')
clock = pg.time.Clock()


class GameObject:
    """Базовый класс игровых объектов."""

    def __init__(self, body_color=None, position=(CENTER_X, CENTER_Y)):
        """Создать объект с заданным цветом и позицией."""
        self.position = position
        self.body_color = body_color

    def draw_cell(self, position, color=None, border_color=BORDER_COLOR):
        """Закрасить ячейку и обвести границей (метод перенесен сюда)."""
        if color is None:
            color = self.body_color
        rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, color, rect)
        if border_color:
            pg.draw.rect(screen, border_color, rect, 1)

    def draw(self):
        """Отрисовать объект (должен быть переопределен)."""
        raise NotImplementedError('Метод draw должен быть реализован в дочернем классе')


class Apple(GameObject):
    """Яблоко, которое съедает змейка."""

    def __init__(self, occupied=(), body_color=APPLE_COLOR):
        """Создать яблоко в свободной ячейке."""
        super().__init__(body_color)
        self.randomize_position(occupied)

    def randomize_position(self, occupied=()):
        """Выбрать случайную свободную ячейку."""
        free_cells = tuple(ALL_CELLS - set(occupied))
        if free_cells:
            self.position = choice(free_cells)

    def draw(self):
        """Отрисовать яблоко."""
        self.draw_cell(self.position)


class Snake(GameObject):
    """Змейка, которой управляет игрок."""

    def __init__(self, body_color=SNAKE_COLOR):
        """Создать змейку и сбросить её в начальное состояние."""
        super().__init__(body_color)
        self.reset()

    def get_head_position(self):
        """Вернуть координаты головы."""
        return self.positions[0]

    def update_direction(self, new_direction):
        """Применить новое направление (исправлено: параметр вместо атрибута)."""
        if new_direction:
            dir_x, dir_y = self.direction
            if new_direction != (-dir_x, -dir_y):
                self.direction = new_direction

    def move(self):
        """Сдвинуть змейку."""
        head_x, head_y = self.get_head_position()
        dir_x, dir_y = self.direction
        new_head = (
            (head_x + dir_x * GRID_SIZE) % SCREEN_WIDTH,
            (head_y + dir_y * GRID_SIZE) % SCREEN_HEIGHT,
        )
        self.positions.insert(0, new_head)
        # Убираем последний элемент (без проверки длины)
        self.last = self.positions.pop()

    def draw(self):
        """Отрисовать голову и стереть хвост (без лишнего цикла)."""
        self.draw_cell(self.positions[0])
        if self.last:
            self.draw_cell(self.last, BOARD_BACKGROUND_COLOR, None)

    def reset(self):
        """Вернуть змейку в начальное состояние (исправлено: случайное направление)."""
        self.length = 1
        self.positions = [self.position]
        # При перезапуске (после смерти) направление случайное
        self.direction = choice([UP, DOWN, LEFT, RIGHT])
        self.last = None


def handle_keys(snake):
    """Обработать нажатия клавиш."""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            raise SystemExit
        if event.type == pg.KEYDOWN:
            new_direction = KEY_DIRECTIONS.get(event.key)
            if new_direction:
                snake.update_direction(new_direction)


def main():
    """Запустить игру."""
    pg.init()
    snake = Snake()
    apple = Apple(occupied=snake.positions)  # Передаем занятые позиции (исправлено)
    screen.fill(BOARD_BACKGROUND_COLOR)

    # При старте игры змейка должна двигаться вправо
    snake.direction = RIGHT

    while True:
        clock.tick(SPEED)
        handle_keys(snake)
        snake.move()

        head = snake.get_head_position()

        if head == apple.position:
            # Если яблоко съедено, возвращаем хвост обратно (удлиняем змейку)
            if snake.last:
                snake.positions.append(snake.last)
                snake.last = None
            apple.randomize_position(snake.positions)
        elif head in snake.positions[1:]:
            snake.reset()
            screen.fill(BOARD_BACKGROUND_COLOR)
            apple.randomize_position(snake.positions)

        snake.draw()
        apple.draw()
        pg.display.update()


if __name__ == '__main__':
    main()
