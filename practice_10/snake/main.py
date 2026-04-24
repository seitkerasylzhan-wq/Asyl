import pygame
import random

# --- Инициализация ---
pygame.init()

# Размер окна
width = 600
height = 400
block_size = 20

screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Snake Game")

clock = pygame.time.Clock()

# Цвета
white = (255, 255, 255)
green = (0, 255, 0)
red = (255, 0, 0)
black = (0, 0, 0)

# --- Начальные параметры ---
snake_pos = [100, 100]
snake_body = [[100, 100], [80, 100], [60, 100]]

direction = [block_size, 0]  # движение вправо

score = 0
level = 1

# --- Генерация еды ---
def generate_food():
    while True:
        x = random.randrange(0, width, block_size)
        y = random.randrange(0, height, block_size)
        if [x, y] not in snake_body:
            return [x, y]

food_pos = generate_food()

# --- Обновление уровня ---
def update_level():
    global level
    level = score // 3 + 1  # каждые 3 очка = новый уровень

# --- Скорость ---
def get_speed():
    return 5 + (level - 1) * 2

# --- Текст ---
font = pygame.font.SysFont("Arial", 25)

def draw_info():
    score_text = font.render(f"Score: {score}", True, white)
    level_text = font.render(f"Level: {level}", True, white)
    screen.blit(score_text, (10, 10))
    screen.blit(level_text, (10, 40))

# --- Game Over ---
def game_over():
    screen.fill(black)
    text = font.render("GAME OVER", True, red)
    screen.blit(text, (width // 2 - 80, height // 2))
    pygame.display.flip()
    pygame.time.delay(2000)
    pygame.quit()
    quit()

# --- Главный цикл ---
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Управление
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                direction = [0, -block_size]
            elif event.key == pygame.K_DOWN:
                direction = [0, block_size]
            elif event.key == pygame.K_LEFT:
                direction = [-block_size, 0]
            elif event.key == pygame.K_RIGHT:
                direction = [block_size, 0]

    # --- Движение змейки ---
    snake_pos[0] += direction[0]
    snake_pos[1] += direction[1]

    # --- Проверка столкновения со стеной ---
    if snake_pos[0] < 0 or snake_pos[0] >= width or \
       snake_pos[1] < 0 or snake_pos[1] >= height:
        game_over()

    # --- Проверка столкновения с собой ---
    if snake_pos in snake_body[1:]:
        game_over()

    # Добавляем новую голову
    snake_body.insert(0, list(snake_pos))

    # --- Проверка еды ---
    if snake_pos == food_pos:
        score += 1
        food_pos = generate_food()
    else:
        snake_body.pop()

    # --- Обновляем уровень ---
    update_level()

    # --- Отрисовка ---
    screen.fill(black)

    # Рисуем змейку
    for block in snake_body:
        pygame.draw.rect(screen, green, (block[0], block[1], block_size, block_size))

    # Рисуем еду
    pygame.draw.rect(screen, red, (food_pos[0], food_pos[1], block_size, block_size))

    # Текст
    draw_info()

    pygame.display.flip()

    # Скорость
    clock.tick(get_speed())

pygame.quit()