import pygame, random, math

from settings import *
from colors import *

# PyGame Setup
pygame.init()

if FULLSCREEN:
    SCREEN = pygame.display.set_mode(RESOLUTION, pygame.FULLSCREEN)
else:
    SCREEN = pygame.display.set_mode(RESOLUTION)

pygame.display.set_caption(WINDOW_NAME)
clock = pygame.time.Clock()
delta_time = 0

score = [0, 0]
minecraft = pygame.font.Font("minecraft.ttf", 100)

hit_sfx = pygame.mixer.Sound("hitting.mp3")
win_sfx = pygame.mixer.Sound("win.mp3")
lose_sfx = pygame.mixer.Sound("lose.mp3")


def normalize(vector: tuple):
    magnitude = math.sqrt(sum(component**2 for component in vector))

    if magnitude == 0:
        raise ValueError("Cannot normalize a zero vector")

    normalized_vector = tuple(component / magnitude for component in vector)

    return normalized_vector


class Paddle:
    def __init__(self, start_pos, max_speed, color, size_x, size_y):
        self.x, self.y = start_pos
        self.max_speed = max_speed
        self.color = color
        self.size_x = size_x
        self.size_y = size_y
        self.speed = 0

    def move(self, direction="down"):
        if direction == "down":
            self.y += self.max_speed
        if direction == "up":
            self.y -= self.max_speed

        if self.y < 0:
            self.y = 0
        if self.y > HEIGHT - self.size_y:
            self.y = HEIGHT - self.size_y

    def ai(self, ball: object):
        if ball.speed_x > 0:
            if (
                ball.y
                + ball.size
                + random.randrange(-10000, 10000) / ((DIFFICULTY // 2 + 50) * 1.5)
                > self.y + self.size_y // 2
            ):
                self.move("down")
            if (
                ball.y
                + ball.size
                + random.randrange(-10000, 10000) / ((DIFFICULTY // 2 + 50) * 1.5)
                < self.y + self.size_y // 2
            ):
                self.move("up")
        else:
            if self.y + self.size_y // 2 > HEIGHT // 2:
                self.move("up")
            if self.y + self.size_y // 2 < HEIGHT // 2:
                self.move("down")

    def draw(self):
        pygame.draw.rect(
            SCREEN, self.color, pygame.Rect(self.x, self.y, self.size_x, self.size_y)
        )


class Ball:
    def __init__(self, start_pos, max_speed, color, size):
        self.start_pos = start_pos
        self.x, self.y = start_pos
        self.pos = (self.x, self.y)
        self.max_speed = max_speed
        self.color = color
        self.size = size

        self.speed_x = 0
        self.speed_y = 0

    def launch(self):
        x = random.randrange(-1000, 1000)
        y = random.randrange(-1000, 1000)

        direction_vector = normalize((x, y))

        self.speed_x = direction_vector[0] * self.max_speed
        self.speed_y = direction_vector[1] * self.max_speed

    def update_pos(self):
        self.x += self.speed_x
        self.y += self.speed_y

    def lose(self, side):
        score[side] += 1
        self.x, self.y = self.start_pos
        self.launch()

        if side == 0:
            lose_sfx.play()
        if side == 1:
            win_sfx.play()

    def collide(self, occasion: str):
        if occasion == "paddle1":
            x = random.randrange(1, 1000)
            y = random.randrange(-1000, 1000)

            direction_vector = normalize((x, y))

            self.speed_x = direction_vector[0] * self.max_speed
            self.speed_y = direction_vector[1] * self.max_speed
        if occasion == "paddle2":
            x = random.randrange(-1000, -1)
            y = random.randrange(-1000, 1000)

            direction_vector = normalize((x, y))

            self.speed_x = direction_vector[0] * self.max_speed
            self.speed_y = direction_vector[1] * self.max_speed
        if occasion == "boundary":
            self.speed_y = -self.speed_y

        hit_sfx.play()

    def detect_collisions(self, paddles: list):
        for i in range(len(paddles)):
            if (
                self.x <= paddles[i].x + paddles[i].size_x
                and self.x + self.size / 2 >= paddles[i].x
            ):
                if (
                    self.y < paddles[i].y + paddles[i].size_y
                    and self.y + self.size * 2 > paddles[i].y
                ):
                    self.collide(f"paddle{i+1}")
                else:
                    self.lose(i)
                    break

        if self.y < 0 or self.y + self.size * 2 > HEIGHT:
            self.collide("boundary")

    def update(self, paddles):
        self.detect_collisions(paddles)
        self.update_pos()

    def draw(self):
        self.pos = (self.x, self.y)
        pygame.draw.circle(SCREEN, self.color, self.pos, self.size)


class Text:
    def __init__(
        self,
        text,
        font,
        color,
        position,
        anti_aliasing,
        background=False,
        bg_color=(0, 0, 0),
    ):
        self.text = text
        self.font = font
        self.color = color
        self.position = position
        self.anti_aliasing = anti_aliasing
        self.background = background
        self.bg_color = bg_color

    def draw(self, pos):
        if not self.background:
            self.text = self.font.render(self.text, self.anti_aliasing, self.color)
        elif self.background:
            self.text = self.font.render(
                self.text, self.anti_aliasing, self.color, self.bg_color
            )

        self.text_rect = self.text.get_rect()

        if pos.lower() == "center":
            self.text_rect.center = (self.position[0], self.position[1])
        if pos.lower() == "bottom":
            self.text_rect.bottom = (self.position[0], self.position[1])
        if pos.lower() == "bottomleft":
            self.text_rect.bottomleft = (self.position[0], self.position[1])
        if pos.lower() == "bottomright":
            self.text_rect.bottomright = (self.position[0], self.position[1])
        if pos.lower() == "midbottom":
            self.text_rect.midbottom = (self.position[0], self.position[1])
        if pos.lower() == "midleft":
            self.text_rect.midleft = (self.position[0], self.position[1])
        if pos.lower() == "midright":
            self.text_rect.midright = (self.position[0], self.position[1])
        if pos.lower() == "midtop":
            self.text_rect.midtop = (self.position[0], self.position[1])
        if pos.lower() == "top":
            self.text_rect.top = (self.position[0], self.position[1])
        if pos.lower() == "topleft":
            self.text_rect.topleft = (self.position[0], self.position[1])
        if pos.lower() == "topright":
            self.text_rect.topright = (self.position[0], self.position[1])
        if pos.lower() == "left":
            self.text_rect.left = (self.position[0], self.position[1])
        if pos.lower() == "right":
            self.text_rect.right = (self.position[0], self.position[1])

        SCREEN.blit(self.text, self.text_rect)


ball = Ball((WIDTH // 2 - 10, HEIGHT // 2 - 10), 6, WHITE, 10)
ball.launch()
paddle1 = Paddle((50, HEIGHT // 2 - 100), 5, WHITE, 20, 200)
paddle2 = Paddle((WIDTH - 60, HEIGHT // 2 - 100), 5, WHITE, 20, 200)
paddles = [paddle1, paddle2]


def draw():
    SCREEN.fill(BLACK)

    for paddle in paddles:
        paddle.draw()

    ball.draw()

    score_text = Text(
        f"{score[1]} : {score[0]}", minecraft, WHITE, (WIDTH // 2, 100), True
    )
    score_text.draw("center")

    pygame.display.flip()


def main():
    global delta_time
    global ipt

    running = True
    ipt = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN:
                    ipt -= 1
                if event.key == pygame.K_UP:
                    ipt += 1
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_DOWN:
                    ipt = 1
                if event.key == pygame.K_UP:
                    ipt = -1

        if ipt > 1:
            ipt = 1
        if ipt < -1:
            ipt = -1

        if ipt > 0:
            paddle1.move("down")
        if ipt < 0:
            paddle1.move("up")

        paddle2.ai(ball)
        ball.update(paddles)

        draw()
        delta_time = 1 / clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
