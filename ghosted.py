import pygame as pg
from pygame.locals import *
import random
from pygame.math import Vector2
import time
import os
import json

pg.init()
w = 1024
h = 768
screen = pg.display.set_mode((w, h))
delta_time = 0.0
gravity = 650
FPS = 120

kello = pg.time.Clock()

running = True
in_logo = True

fontti = pg.font.SysFont("System", 32)
logo_font = pg.font.SysFont("Impact", 72)
logo_text = logo_font.render("~ GHOSTED ~", True, (255, 255, 255))
gameover_font = pg.font.SysFont("Impact", 48)
gameover_text = gameover_font.render("YOU DIED", True, (255, 0, 0))
gameover_text2 = fontti.render("Press spacebar for new game...", True, (255, 255, 255))
highscore_text = gameover_font.render("HIGH SCORES", True, (255, 255, 255))
instruction_text = fontti.render(
    "Arrows to move, spacebar to start the game...", True, (255, 255, 255)
)


class HighScore:
    def __init__(self):
        self.highscore_file = "highscores.txt"
        self.scores = self.load_from_file()
        self.surfaces = [[]]
        self.hs_font = pg.font.SysFont("System", 32)
        self.input_text = ""
        self.in_hs = False
        self.in_typing = False
        self.into_hs_counter = 700

    def load_from_file(self):
        if os.path.isfile(self.highscore_file):
            with open(self.highscore_file, "r") as hsf:
                scores = json.load(hsf)
            hsf.close()
            if type(scores) is list:
                self.scores = scores
            else:
                self.default_scores()
        else:
            self.default_scores()

        return self.scores

    def default_scores(self):
        self.scores = [
            {"shS": 30},
            {"shS": 25},
            {"shS": 20},
            {"shS": 15},
            {"shS": 10},
        ]
        return True

    def save_to_file(self):
        with open(self.highscore_file, "w") as hsf:
            json.dump(self.scores, hsf)
        hsf.close()

    def restart(self):
        self.input_text = ""
        self.in_hs = False
        self.in_typing = False
        self.into_hs_counter = 700

    def draw(self):
        center_text(highscore_text, 100)
        i = 0
        for unit in self.scores:
            for k, v in unit.items():
                user = str(k)
                score = str(v)
                playersurf = self.hs_font.render(user, True, (255, 255, 255))
                scoresurf = self.hs_font.render(score, True, (255, 255, 255))
                usize = self.hs_font.size(user)
                ssize = self.hs_font.size(score)
                screen.blit(
                    playersurf, (w // 2 - 175, h // 10 + 150 + (usize[1] + 50 * i))
                )
                screen.blit(
                    scoresurf,
                    (w // 2 + (175 - ssize[0]), h // 10 + 150 + (ssize[1] + 50 * i)),
                )
                i += 1

    def draw_input(self, color: tuple = (10, 10, 10)):
        font = pg.font.SysFont("System", 20)
        size_surf = font.render("MMMMMMMMMM", True, (0, 0, 0))
        font_w = size_surf.get_width()
        font_h = size_surf.get_height()
        rect_w = font_w + 20
        rect_h = font_h + 20
        text_surface = font.render(self.input_text, True, (255, 255, 255))
        alpha_surface = pg.Surface((rect_w, rect_h))
        outer_rect = pg.Rect(0, 0, rect_w, rect_h)
        input_rect = pg.Rect(5, 5, rect_w - 10, rect_h - 10)
        pg.draw.rect(alpha_surface, (255, 255, 255), outer_rect)
        pg.draw.rect(alpha_surface, color, input_rect)
        alpha_surface.set_alpha(160)
        input_x = w / 2 - text_surface.get_width() / 2
        blit_x = w / 2 - alpha_surface.get_width() / 2
        blit_y = h - alpha_surface.get_height() / 2 - 200
        font_surface = font.render("Please enter your name:", True, (255, 255, 255))
        text_blit_x = w / 2 - font_surface.get_width() / 2
        screen.blit(font_surface, (text_blit_x, blit_y - 50))
        screen.blit(alpha_surface, (blit_x, blit_y))
        screen.blit(text_surface, (input_x, blit_y + 8))

    def check_scores(self):
        for unit in self.scores:
            for k, v in unit.items():
                player = k
                score = v
                if p.pisteet >= score and not p.scored:
                    return True
        return False

    def fix_scores(self):
        fixed = False
        newlist = []
        for unit in self.scores:
            for k, v in unit.items():
                player = k
                score = v
                if p.pisteet >= score and not fixed:
                    newlist.append({p.name: p.pisteet})
                    newlist.append({k: v})
                    fixed = True
                else:
                    newlist.append({k: v})

        if fixed:
            newlist.pop()

        self.scores = newlist
        return fixed

    def hijack_keys(self, event):
        if not p.scored:
            if event.type == KEYDOWN:
                if event.key == K_RETURN:
                    if self.input_text != "":
                        p.name = self.input_text
                        if self.fix_scores():
                            p.scored = True
                            self.save_to_file()
                elif event.key == K_BACKSPACE:
                    self.input_text = self.input_text[:-1]

                else:
                    if len(self.input_text) < 10:
                        self.input_text += e.unicode
        else:
            self.in_typing = False


highscores = HighScore()


class Taso:
    def __init__(self):
        self.n = 1
        self.time = 30
        self.ghost_interval = random.randint(500, 1000) * ((100 - self.n) / 100)
        self.coin_interval = max([200 - self.n * 20, 50])
        self.ghost_speed = 1
        self.levelup_req = 10
        self.collected = 0
        self.toss_power = 200
        self.t_color_1 = (52, 46, 68)
        self.t_color_2 = (73, 67, 82)
        self.tile = pg.Surface((64, 64))
        self.tiles = []
        self.update_tiles()

    def update_tiles(self):
        pg.draw.rect(self.tile, self.t_color_1, (0, 0, 32, 32))
        pg.draw.rect(self.tile, self.t_color_2, (4, 4, 24, 24))
        pg.draw.rect(self.tile, self.t_color_2, (32, 0, 32, 32))
        pg.draw.rect(self.tile, self.t_color_1, (36, 4, 24, 24))
        pg.draw.rect(self.tile, self.t_color_2, (0, 32, 32, 32))
        pg.draw.rect(self.tile, self.t_color_1, (4, 36, 24, 24))
        pg.draw.rect(self.tile, self.t_color_1, (32, 32, 32, 32))
        pg.draw.rect(self.tile, self.t_color_2, (36, 36, 24, 24))
        self.tile.set_alpha(127)

        _, _, tile_width, tile_height = self.tile.get_rect()

        for i in range(w // tile_width + 1):
            for j in range(h // tile_height + 1):
                pos = (i * tile_width, j * tile_height)
                self.tiles.append(pos)

    def up(self):
        self.t_color_1 = (
            random.randint(0, 127),
            random.randint(0, 127),
            random.randint(0, 127),
        )
        self.t_color_2 = (
            random.randint(0, 127),
            random.randint(0, 127),
            random.randint(0, 127),
        )
        self.n += 1
        self.toss_power += 100
        self.ghost_interval = random.randint(500, 1000) * ((100 - self.n * 10) / 100)
        self.coin_interval = max([200 - self.n * 20, 50])
        self.ghost_speed += 0.8
        self.levelup_req += 5
        self.collected = 0
        self.time = 30
        self.update_tiles()


level = Taso()
cointoss_countdown = level.coin_interval
vihu_countdown = level.ghost_interval
ennen = time.time()


class Pelaaja(pg.sprite.Sprite):
    GRAVITY = 1

    def __init__(self, x, y):
        super().__init__()
        self.sprite = pg.image.load("robo.png")
        self.mask = pg.mask.from_surface(self.sprite)
        self.rect = self.sprite.get_rect()
        self.w = self.sprite.get_width()
        self.h = self.sprite.get_height()
        self.name = ""
        self.x_vel = 0
        self.y_vel = 0
        self.rect.x = x
        self.rect.y = y
        self.max_x = screen.get_width() - self.sprite.get_width()
        self.max_y = screen.get_height() - self.sprite.get_height()
        self.pisteet = 0
        self.jump_c = 0
        self.fall_c = 0
        self.alive = True
        self.scored = False

    def jump(self):
        self.jump_c += 1
        self.y_vel = -self.GRAVITY * 6

    def landed(self):
        self.fall_c = 0
        self.y_vel = 0
        self.jump_c = 0

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def move_left(self, vel):
        self.x_vel = -vel

    def move_right(self, vel):
        self.x_vel = vel

    def collide(self, rect):
        return self.rect.colliderect(rect)

    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pg.mask.from_surface(self.sprite)
        self.y_vel += min(1, (self.fall_c / FPS) * self.GRAVITY)
        self.move(self.x_vel, self.y_vel)
        self.fall_c += 1
        if self.rect.y + self.h >= h:
            self.rect.y = h - self.h
            self.landed()

    def draw(self):
        screen.blit(self.sprite, (self.rect.x, self.rect.y))


class Vihu(pg.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.sprite = pg.image.load("hirvio.png")
        self.sprite.set_alpha(127)
        self.mask = pg.mask.from_surface(self.sprite)
        self.whiteghost = self.mask.to_surface(unsetcolor=(0, 0, 0, 0))
        self.whiteghost.set_alpha(30)
        self.ghost = random.choice([self.sprite, self.whiteghost])
        self.rect = self.sprite.get_rect()
        self.w = self.sprite.get_width()
        self.h = self.sprite.get_height()
        self.rect.x = x
        self.rect.y = y
        self.nopeus = level.ghost_speed
        if self.rect.x > w:
            self.ghost = pg.transform.flip(self.ghost, flip_x=True, flip_y=False)
            self.suunta = -1
        else:
            self.suunta = 1

    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pg.mask.from_surface(self.sprite)
        self.rect.x += round(self.suunta * level.ghost_speed)
        if self.rect.x > w + 100 or self.rect.x < -100:
            vihut.remove(self)
        if p.alive:
            if pg.sprite.collide_mask(self, p):
                game_over()

    def draw(self):
        screen.blit(self.ghost, (self.rect.x, self.rect.y))


class Portti:
    def __init__(self, x: int = 0, y: int = 0):
        self.sprite = pg.image.load("ovi.png")
        self.rect = self.sprite.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.mask = pg.Surface((0, 0))

    def spawn(self):
        self.rect.x = random.randint(
            0 + self.sprite.get_width(), w - self.sprite.get_width()
        )
        self.rect.y = h - self.sprite.get_height()
        portit.append(self)

    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pg.mask.from_surface(self.sprite)
        if pg.sprite.collide_mask(self, p):
            level.up()
            portit.remove(self)
            flashes.append(Flash(100, (60, 60, 255)))

    def draw(self):
        screen.blit(self.sprite, (self.rect.x, self.rect.y))


class Flash:
    def __init__(self, timer: int = 4, color: tuple = (255, 255, 255)):
        self.time = timer
        self.color = color
        self.image = pg.Surface((w, h))
        self.image.fill(self.color)
        self.opa = 255
        self.opach = 255 // timer

    def update(self):
        self.time -= 1
        self.opa -= self.opach
        self.image.set_alpha(self.opa)
        if self.time <= 0:
            flashes.remove(self)

    def draw(self):
        screen.blit(self.image, (0, 0))


class Raha:
    def __init__(
        self,
        position: Vector2,
        velocity: Vector2 = Vector2(0, 0),
        radius: float = 20,
        image: pg.Surface = None,
    ):
        self.sprite = image
        if self.sprite is None:
            self.sprite = pg.image.load("kolikko.png")
        self.position = position.copy()
        self.velocity = velocity.copy()
        self.radius = radius
        self.diameter = radius * 2.0
        self.rect = self.sprite.get_rect()
        self.rect.x = self.position.x - self.radius
        self.rect.y = self.position.y - self.radius
        self.life = 1000
        self.blink = False
        self.mask = pg.Surface((0, 0))

    def update(self):
        self.velocity.y += delta_time * gravity
        self.position += self.velocity * delta_time
        self.life -= 1
        self.rect.x = self.position.x - self.radius
        self.rect.y = self.position.y - self.radius
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pg.mask.from_surface(self.sprite)
        self.screen_collide()
        self.player_collide()

    def draw(self):
        top_left_position = Vector2(
            self.position.x - self.radius, self.position.y - self.radius
        )
        if (self.blink and not self.life % 3) or not self.blink:
            screen.blit(self.sprite, (top_left_position.x, top_left_position.y))

    def screen_collide(self):
        if self.position.x < self.radius or self.position.x > w - self.radius:
            self.velocity.x = -self.velocity.x
        if self.position.y < self.radius or self.position.y > h - self.radius:
            self.velocity.y = -self.velocity.y * 0.99

    def player_collide(self):
        if p.alive:
            if pg.sprite.collide_mask(self, p):
                p.pisteet += 1
                level.collected += 1
                rahat.remove(self)


def game_over():
    p.alive = False
    p.x_vel = 0
    p.y_vel = 0
    p.sprite = pg.transform.flip(p.sprite, flip_x=False, flip_y=True)


def logo():
    screen.blit(
        logo_text,
        (w // 2 - logo_text.get_width() // 2, h // 2 - logo_text.get_height() // 2),
    )
    screen.blit(instruction_text, (w // 2 - instruction_text.get_width() // 2, h - 100))


def hall_of_fame():
    highscores.draw()
    if highscores.check_scores():
        highscores.in_typing = True
        highscores.draw_input()
    else:
        highscores.in_typing = False


def start_game():
    global in_logo
    in_logo = False


def restart():
    rahat.clear()
    vihut.clear()
    portit.clear()
    flashes.clear()
    highscores.restart()
    level.__init__()
    p.__init__(320, 680)
    flashes.append(Flash(100, (100, 255, 100)))


def center_text(text: pg.Surface, y: int):
    screen.blit(text, (w // 2 - text.get_width() // 2, y))


rahat = []
vihut = []
portit = []
flashes = []

p = Pelaaja(320, 680)
gate = Portti()

while running:
    for e in pg.event.get():
        if e.type == QUIT or (e.type == KEYDOWN and e.key == K_ESCAPE):
            running = False
        elif e.type == KEYDOWN:
            if highscores.in_hs:
                highscores.hijack_keys(e)

            if e.key == K_SPACE and not highscores.in_typing:
                if in_logo:
                    start_game()
                if highscores.in_hs:
                    restart()

        if e.type == KEYUP and p.alive:
            p.x_vel = 0
        if e.type == KEYDOWN and p.alive:
            if e.key == K_UP:
                p.jump()

    key = pg.key.get_pressed()

    if p.alive and not in_logo and not highscores.in_hs:
        if key[K_LEFT]:
            p.move_left(2)
        if key[K_RIGHT]:
            p.move_right(2)

    screen.fill((20, 20, 40))

    objects = [p, *portit, *rahat, *vihut, *flashes]

    if in_logo:
        logo()
    elif highscores.in_hs:
        hall_of_fame()
        if not highscores.in_typing:
            center_text(gameover_text2, h - 150)
    else:
        if cointoss_countdown < 1:
            rahat.append(
                Raha(
                    Vector2(w / 2, h / 2),
                    Vector2(random.random() * 2.0 - 1.0, random.random() * 2.0 - 1.0)
                    * level.toss_power,
                )
            )
            cointoss_countdown = level.coin_interval

        if vihu_countdown < 1:
            vihut.append(
                Vihu(
                    random.choice(
                        [random.randint(-99, -50), random.randint(w + 50, w + 99)]
                    ),
                    680,
                )
            )
            vihu_countdown = level.ghost_interval

        vihu_countdown -= 1
        cointoss_countdown -= 1

        for t in level.tiles:
            screen.blit(level.tile, t)

        for o in objects:
            o.update()
            if hasattr(o, "life"):
                if o.life < 200:
                    o.blink = True
                if o.life < 0:
                    rahat.remove(o)
            o.draw()

        teksti = fontti.render(f"Points: {p.pisteet}", True, (255, 0, 0))
        teksti2 = fontti.render(f"Level: {level.n}", True, (255, 0, 0))
        teksti3 = fontti.render(f"Time: {level.time}", True, (255, 0, 0))
        teksti4 = fontti.render(
            f"Coins to level up: {level.levelup_req - level.collected}",
            True,
            (255, 0, 0),
        )
        screen.blit(teksti, (10, 10))
        center_text(teksti2, 10)
        screen.blit(teksti3, (w - teksti3.get_width() - 10, 10))
        center_text(teksti4, 35)

        # Main alive loop

        if p.alive:
            nyt = time.time()
            if nyt > ennen + 1:
                ennen = time.time()
                level.time -= 1
                if level.time <= 0:
                    game_over()

            if level.collected >= level.levelup_req:
                if len(portit) < 1:
                    flashes.append(Flash())
                    gate.spawn()
        else:
            screen.blit(
                gameover_text,
                (
                    w // 2 - gameover_text.get_width() // 2,
                    h // 2 - gameover_text.get_height() // 2,
                ),
            )
            highscores.into_hs_counter -= 1
            if highscores.into_hs_counter <= 0:
                highscores.in_hs = True

    pg.display.flip()
    delta_time = 0.001 * kello.tick(FPS)

pg.quit()
exit()
