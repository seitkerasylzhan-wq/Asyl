import pygame, sys
from pygame.locals import *
import random, time
import os

pygame.init()

# --- Путь к папке с игрой ---
BASE_DIR = os.path.dirname(__file__)

FPS = 60
FramePerSec = pygame.time.Clock()

# --- Цвета ---
RED    = (255, 0, 0)
BLACK  = (0, 0, 0)
WHITE  = (255, 255, 255)
YELLOW = (255, 255, 0)

# --- Экран ---
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 800

# --- Игровые переменные ---
SPEED = 5
MONEY_SCORE = 0
LEVEL = 1

DISPLAYSURF = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Racer")

# --- Фон и иконка монеты (ИСПРАВЛЕНО) ---
background = pygame.transform.scale(
    pygame.image.load(os.path.join(BASE_DIR, "animatedstreet.png")),
    (SCREEN_WIDTH, SCREEN_HEIGHT)
)

moneta_img = pygame.transform.scale(
    pygame.image.load(os.path.join(BASE_DIR, "money.png")),
    (30, 30)
)

font_small = pygame.font.SysFont("Verdana", 20)
font_big = pygame.font.SysFont("Verdana", 60)

# --- ВРАГ (создаём заранее чтобы Coin мог проверять collision) ---
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.transform.scale(
            pygame.image.load(os.path.join(BASE_DIR, "enemy.png")),
            (60, 120)
        )
        self.rect = self.image.get_rect()
        self.respawn()

    def respawn(self):
        self.rect.center = (random.randint(40, SCREEN_WIDTH-40), 0)

    def move(self):
        self.rect.move_ip(0, SPEED)
        if self.rect.top > SCREEN_HEIGHT:
            self.respawn()

# --- МОНЕТА ---
class Coin(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.transform.scale(
            pygame.image.load(os.path.join(BASE_DIR, "money.png")),
            (30, 30)
        )
        self.rect = self.image.get_rect()
        self.respawn()

    # не спавнится на враге
    def respawn(self):
        while True:
            x = random.randint(40, SCREEN_WIDTH - 40)
            self.rect.center = (x, 0)
            if not self.rect.colliderect(E1.rect):
                break

    def move(self):
        self.rect.move_ip(0, SPEED)
        if self.rect.top > SCREEN_HEIGHT:
            self.respawn()

# --- ИГРОК ---
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.transform.scale(
    pygame.image.load(os.path.join(BASE_DIR, "player.png")),
    (60, 120)
)
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH//2, SCREEN_HEIGHT - 100)

    def move(self):
        keys = pygame.key.get_pressed()

        # границы экрана
        if self.rect.left > 0 and keys[K_LEFT]:
            self.rect.move_ip(-5, 0)

        if self.rect.right < SCREEN_WIDTH and keys[K_RIGHT]:
            self.rect.move_ip(5, 0)

# --- ОБЪЕКТЫ ---
P1 = Player()
E1 = Enemy()
M1 = Coin()

enemies = pygame.sprite.Group(E1)
money_group = pygame.sprite.Group(M1)
all_sprites = pygame.sprite.Group(P1, E1, M1)

# --- УРОВНИ ---
def update_level():
    global LEVEL, SPEED
    LEVEL = MONEY_SCORE // 3 + 1
    SPEED = 5 + (LEVEL - 1) * 2

# --- GAME LOOP ---
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    DISPLAYSURF.blit(background, (0,0))

    # --- UI ---
    score_text = font_small.render(f"Score: {MONEY_SCORE}", True, YELLOW)
    level_text = font_small.render(f"Level: {LEVEL}", True, WHITE)

    DISPLAYSURF.blit(moneta_img, (10, 10))
    DISPLAYSURF.blit(score_text, (45, 13))
    DISPLAYSURF.blit(level_text, (10, 40))

    # --- движение ---
    for entity in all_sprites:
        DISPLAYSURF.blit(entity.image, entity.rect)
        entity.move()

    # --- сбор монеты ---
    if pygame.sprite.spritecollideany(P1, money_group):
        MONEY_SCORE += 1
        M1.respawn()

    # --- уровень ---
    update_level()

    # --- столкновение ---
    if pygame.sprite.spritecollideany(P1, enemies):
        try:
            pygame.mixer.Sound(os.path.join(BASE_DIR, "crash.wav")).play()
        except:
            pass

        time.sleep(0.5)
        DISPLAYSURF.fill(RED)

        game_over = font_big.render("Game Over", True, BLACK)
        DISPLAYSURF.blit(game_over, (SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 - 50))

        pygame.display.update()
        time.sleep(2)
        pygame.quit()
        sys.exit()

    pygame.display.update()
    FramePerSec.tick(FPS)