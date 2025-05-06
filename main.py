import pygame
from pygame import mixer
from pygame.locals import *
import random
import os
import serial
import time

arduino = serial.Serial('COM5', 9600)
time.sleep(2)  # Așteapta ca arduino sa se reseteze

def led_menu():
    arduino.write(b'M')

def led_alive():
    arduino.write(b'A')

def led_dead():
    arduino.write(b'D')

def led_close():
    arduino.write(b'I')

pygame.init()
pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()

# Definim FPS
clock = pygame.time.Clock()
fps = 60

screen_width = 728
screen_height = 1000

# Incarcare imagine de fundal
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Space Invaders')

# Definim fonturile
font30 = pygame.font.SysFont('Constantia', 30)
font40 = pygame.font.SysFont('Constantia', 40)

# Incarcarea sunetelor
explosion_fx = pygame.mixer.Sound("img/explosion.wav")
explosion_fx.set_volume(0.25)

explosion2_fx = pygame.mixer.Sound("img/explosion2.wav")
explosion2_fx.set_volume(0.25)

laser_fx = pygame.mixer.Sound("img/laser.wav")
laser_fx.set_volume(0.25)

# Incarcarea muzicii de fundal pentru meniu
pygame.mixer.music.load("img/ufo.wav")

# Definirea variabilelor
rows = 5
cols = 6
alien_cooldown = 1000  # Cooldown pentru gloantele extraterestrilor
last_alien_shot = pygame.time.get_ticks()
countdown = 3
last_count = pygame.time.get_ticks()
game_over = 0  # 0 = in joc, 1 = castigator, -1 = pierdut
in_main_menu = True
level = 1
max_levels = 5
score = 0
selected_difficulty = 0  # 0 = easy, 1 = medium, 2 = hard
difficulty_names = ["Easy", "Medium", "Hard"]
high_scores = [0, 0, 0]
sound_enabled = True
selected_ship = 0
ship_names = ["Spaceship", "Spaceship1", "Spaceship2"]
ship_images = ["spaceship.png", "spaceship1.png", "spaceship2.png"]
current_led_state = None

# Incarca highscore-urile din fisiere
for i, difficulty in enumerate(["easy", "medium", "hard"]):
    filename = f"highscore_{difficulty}.txt"
    if os.path.exists(filename):
        with open(filename, "r") as f:
            high_scores[i] = int(f.read())

# Definim culorile
red = (255, 0, 0)
green = (0, 255, 0)
white = (255, 255, 255)

# Incarcare fundal
dbg = pygame.image.load("img/bg.png")

def draw_bg():
    screen.blit(dbg, (0, 0))

# Functie pentru text
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

# Functie pentru afisarea meniului principal
def draw_main_menu():
    draw_bg()
    draw_text("SPACE INVADERS", font40, white, int(screen_width / 2 - 150), screen_height // 2 - 200)
    draw_text("Selecteaza dificultatea cu sagetile stanga/dreapta", font30, white, int(screen_width / 2 - 260),
              screen_height // 2 - 80)
    draw_text(f"Dificultate: {difficulty_names[selected_difficulty]}", font30, white, int(screen_width / 2 - 130),
              screen_height // 2 - 40)
    draw_text(f"Highscore: {high_scores[selected_difficulty]}", font30, white, int(screen_width / 2 - 130),
              screen_height // 2 - 10)

    # Meniu selecție navă - Afișăm imaginea navei în loc de nume
    draw_text("Selecteaza nava cu sagetile sus/jos", font30, white, int(screen_width / 2 - 220),
              screen_height // 2 + 30)
    # Încărcăm și afișăm imaginea navei selectate
    ship_image = pygame.image.load(f"img/{ship_images[selected_ship]}")
    # Scalăm imaginea dacă este prea mare (opțional, ajustăm dimensiunile după nevoie)
    ship_image = pygame.transform.scale(ship_image, (50, 50))  # Ajustăm dimensiunea imaginii
    screen.blit(ship_image, (int(screen_width / 2 - 25), screen_height // 2 + 60))  # Centrat orizontal

    # Meniu sunet
    draw_text("Apasa S pentru a activa/dezactiva sunetul", font30, white, int(screen_width / 2 - 260),
              screen_height // 2 + 90)
    draw_text(f"Sunet: {'Pornit' if sound_enabled else 'Oprit'}", font30, white, int(screen_width / 2 - 130),
              screen_height // 2 + 120)
    draw_text("Apasa ENTER pentru a incepe", font30, white, int(screen_width / 2 - 170), screen_height // 2 + 160)
    draw_text("Apasa R pentru a reseta Highscore", font30, white, int(screen_width / 2 - 200), screen_height // 2 + 190)

# Cream clasa navei spatiale
class Spaceship(pygame.sprite.Sprite):
    def __init__(self, x, y, health, ship_image):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(f"img/{ship_image}")
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.health_start = health
        self.health_remaining = health
        self.last_shot = pygame.time.get_ticks()
        self.triple_shot = False
        self.triple_shot_timer = 0

    def update(self):
        global game_over

        # Viteza de miscare
        speed = 3
        cooldown = 300  # Cooldown pentru foc

        # Verificam dacă triple shot a expirat (dureaza 5 secunde)
        if self.triple_shot and pygame.time.get_ticks() - self.triple_shot_timer > 5000:
            self.triple_shot = False

        # Controlul navei
        key = pygame.key.get_pressed()
        if key[pygame.K_a] and self.rect.left > 0:
            self.rect.x -= speed
        if key[pygame.K_d] and self.rect.right < screen_width:
            self.rect.x += speed

        # Tragere
        time_now = pygame.time.get_ticks()
        if key[pygame.K_SPACE] and time_now - self.last_shot > cooldown:
            if sound_enabled:
                laser_fx.play()
            if self.triple_shot:
                bullet_left = Bullets(self.rect.centerx - 15, self.rect.top, -2, -5)
                bullet_center = Bullets(self.rect.centerx, self.rect.top, 0, -5)
                bullet_right = Bullets(self.rect.centerx + 15, self.rect.top, 2, -5)
                bullet_group.add(bullet_left, bullet_center, bullet_right)
            else:
                bullet = Bullets(self.rect.centerx, self.rect.top, 0, -5)
                bullet_group.add(bullet)
            self.last_shot = time_now

        self.mask = pygame.mask.from_surface(self.image)

        # Bara viata
        pygame.draw.rect(screen, red, (self.rect.x, (self.rect.bottom + 10), self.rect.width, 15))
        if self.health_remaining > 0:
            pygame.draw.rect(screen, green, (
            self.rect.x, (self.rect.bottom + 10), int(self.rect.width * (self.health_remaining / self.health_start)),
            15))
        elif self.health_remaining <= 0:
            explosion = Explosion(self.rect.centerx, self.rect.centery, 3)
            explosion_group.add(explosion)
            self.kill()
            game_over = -1
        return game_over

# Cream clasa munitiei
class Bullets(pygame.sprite.Sprite):
    def __init__(self, x, y, speed_x=0, speed_y=-5):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/bullet.png")
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.speed_x = speed_x
        self.speed_y = speed_y

    def update(self):
        global score
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        if self.rect.bottom < 0:
            self.kill()
        if pygame.sprite.spritecollide(self, alien_group, True):
            self.kill()
            score += 10
            if sound_enabled:
                explosion_fx.play()
            explosion = Explosion(self.rect.centerx, self.rect.centery, 2)
            explosion_group.add(explosion)

# Cream clasa extraterestrilor
class Aliens(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/alien" + str(random.randint(1, 5)) + ".png")
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.move_counter = 0
        self.move_direction = 1
        self.speed = 1 if selected_difficulty == 0 else 2 if selected_difficulty == 1 else 3

    def update(self):
        self.rect.x += self.move_direction * self.speed
        self.move_counter += self.speed
        if abs(self.move_counter) > 75:
            self.move_direction *= -1
            self.move_counter *= self.move_direction

# Cream clasa munitie extraterestri
class Alien_Bullets(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/alien_bullet.png")
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        alien_bullet_group.add(self)

    def update(self):
        self.rect.y += 2
        if self.rect.top > screen_height:
            self.kill()
        if pygame.sprite.spritecollide(self, spaceship_group, False, pygame.sprite.collide_mask):
            self.kill()
            if sound_enabled:
                explosion2_fx.play()
            spaceship.health_remaining -= 1
            explosion = Explosion(self.rect.centerx, self.rect.centery, 1)
            explosion_group.add(explosion)

# Cream clasa pentru explozii
class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, size):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range(1, 6):
            img = pygame.image.load(f"img/exp{num}.png")
            if size == 1:
                img = pygame.transform.scale(img, (20, 20))
            if size == 2:
                img = pygame.transform.scale(img, (40, 40))
            if size == 3:
                img = pygame.transform.scale(img, (160, 160))
            self.images.append(img)
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.counter = 0

    def update(self):
        explosion_speed = 3
        self.counter += 1
        if self.counter >= explosion_speed and self.index < len(self.images) - 1:
            self.counter = 0
            self.index += 1
            self.image = self.images[self.index]
        if self.index >= len(self.images) - 1 and self.counter >= explosion_speed:
            self.kill()

# Clasa pentru power-up-uri
class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, type):
        pygame.sprite.Sprite.__init__(self)
        self.type = type
        if self.type == "triple_shot":
            self.image = pygame.image.load("img/powerup_shot.png")
        elif self.type == "heal":
            self.image = pygame.image.load("img/powerup_heal.png")
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

    def update(self):
        self.rect.y += 2
        if self.rect.top > screen_height:
            self.kill()
        if pygame.sprite.spritecollide(self, spaceship_group, False):
            if self.type == "triple_shot":
                spaceship.triple_shot = True
                spaceship.triple_shot_timer = pygame.time.get_ticks()
            elif self.type == "heal":
                spaceship.health_remaining = min(spaceship.health_start, spaceship.health_remaining + 1)
            self.kill()

# Cream grupuri pentru sprite-uri
spaceship_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
alien_group = pygame.sprite.Group()
alien_bullet_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
powerup_group = pygame.sprite.Group()

# Functie care creeaza extraterestri
def create_aliens():
    initial_y = 100 + (level - 1) * 50
    for row in range(rows):
        for item in range(cols):
            alien = Aliens(100 + item * 100, initial_y + row * 70)
            alien_group.add(alien)

# Resetarea jocului
def reset_game():
    global spaceship, countdown, last_count, game_over, score, level, alien_cooldown
    bullet_group.empty()
    alien_group.empty()
    alien_bullet_group.empty()
    explosion_group.empty()
    powerup_group.empty()
    spaceship_group.empty()
    spaceship = Spaceship(int(screen_width / 2), screen_height - 100, 3, ship_images[selected_ship])
    spaceship_group.add(spaceship)
    create_aliens()
    countdown = 3
    last_count = pygame.time.get_ticks()
    game_over = 0
    score = 0
    level = 1
    alien_cooldown = 1000 if selected_difficulty == 0 else 750 if selected_difficulty == 1 else 500
    pygame.mixer.music.stop()  # Oprește muzica la începerea jocului

# Cream jucatorul
spaceship = Spaceship(int(screen_width / 2), screen_height - 100, 3, ship_images[selected_ship])
spaceship_group.add(spaceship)
create_aliens()

# Loop-ul jocului
run = True
last_powerup_spawn = pygame.time.get_ticks()
music_started = False  # Urmareste daca muzica a inceput in meniu
while run:
    clock.tick(fps)
    draw_bg()

    if in_main_menu:
        # Incepe muzica
        if not music_started:
            pygame.mixer.music.set_volume(0.5 if sound_enabled else 0)
            pygame.mixer.music.play(-1)  # -1 pentru buclă infinită
            music_started = True
            # Set LED to blue for menu
            if current_led_state != "menu":
                led_menu()
                current_led_state = "menu"

        draw_main_menu()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                led_close()  # stinge led-ul
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and selected_difficulty > 0:
                    selected_difficulty -= 1
                if event.key == pygame.K_RIGHT and selected_difficulty < 2:
                    selected_difficulty += 1
                if event.key == pygame.K_UP and selected_ship > 0:
                    selected_ship -= 1
                if event.key == pygame.K_DOWN and selected_ship < 2:
                    selected_ship += 1
                if event.key == pygame.K_s:
                    sound_enabled = not sound_enabled
                    if sound_enabled:
                        explosion_fx.set_volume(0.25)
                        explosion2_fx.set_volume(0.25)
                        laser_fx.set_volume(0.25)
                        pygame.mixer.music.set_volume(0.5)  # Unmute la muzica
                    else:
                        explosion_fx.set_volume(0)
                        explosion2_fx.set_volume(0)
                        laser_fx.set_volume(0)
                        pygame.mixer.music.set_volume(0)  # Mute la muzica
                if event.key == pygame.K_r:
                    high_scores[selected_difficulty] = 0
                    with open(f"highscore_{difficulty_names[selected_difficulty].lower()}.txt", "w") as f:
                        f.write(str(high_scores[selected_difficulty]))
                if event.key == pygame.K_RETURN:
                    in_main_menu = False
                    music_started = False  # reseteaza muzica in momentul in care intram din nou in meniu
                    reset_game()
    else:
        # Spawn power-up la fiecare 10 secunde
        if pygame.time.get_ticks() - last_powerup_spawn > 10000:
            power_type = random.choice(["triple_shot", "heal"])
            powerup = PowerUp(random.randint(50, screen_width - 50), 0, power_type)
            powerup_group.add(powerup)
            last_powerup_spawn = pygame.time.get_ticks()

        if countdown == 0:
            time_now = pygame.time.get_ticks()
            if time_now - last_alien_shot > alien_cooldown and len(alien_group) > 0:
                attacking_alien = random.choice(alien_group.sprites())
                alien_bullet = Alien_Bullets(attacking_alien.rect.centerx, attacking_alien.rect.bottom)
                alien_bullet_group.add(alien_bullet)
                last_alien_shot = time_now

            if len(alien_group) == 0 and level <= max_levels:
                level += 1
                if level > max_levels:
                    game_over = 1
                    # se face led-ul rosu cand termini nivelele
                    if current_led_state != "dead":
                        led_dead()
                        current_led_state = "dead"
                else:
                    bullet_group.empty()
                    alien_group.empty()
                    alien_bullet_group.empty()
                    explosion_group.empty()
                    spaceship_group.empty()
                    spaceship = Spaceship(int(screen_width / 2), screen_height - 100, 3, ship_images[selected_ship])
                    spaceship_group.add(spaceship)
                    create_aliens()
                    countdown = 3
                    last_count = pygame.time.get_ticks()

            if game_over == 0:
                game_over = spaceship.update()
                # led-u se face verde cat jucatorul e in viata
                if spaceship.health_remaining > 0 and current_led_state != "alive":
                    led_alive()
                    current_led_state = "alive"
                bullet_group.update()
                alien_group.update()
                alien_bullet_group.update()
                powerup_group.update()
            else:
                if game_over == -1:
                    draw_text('Extraterestii au invadat pamantul!', font40, white, int(screen_width / 2 - 270),
                              int(screen_height / 2 - 50))
                    if score > high_scores[selected_difficulty]:
                        high_scores[selected_difficulty] = score
                        with open(f"highscore_{difficulty_names[selected_difficulty].lower()}.txt", "w") as f:
                            f.write(str(high_scores[selected_difficulty]))
                    draw_text("Apasa ENTER pentru a te intoarce la meniu", font30, white, screen_width // 2 - 270,
                              screen_height // 2 + 100)
                    # led-ul se face rosu cand mori
                    if current_led_state != "dead":
                        led_dead()
                        current_led_state = "dead"
                if game_over == 1:
                    draw_text('Pamantul a fost salvat!', font40, white, int(screen_width / 2 - 180),
                              int(screen_height / 2 - 50))
                    if score > high_scores[selected_difficulty]:
                        high_scores[selected_difficulty] = score
                        with open(f"highscore_{difficulty_names[selected_difficulty].lower()}.txt", "w") as f:
                            f.write(str(high_scores[selected_difficulty]))
                    draw_text("Apasa ENTER pentru a te intoarce la meniu", font30, white, screen_width // 2 - 270,
                              screen_height // 2 + 100)
                    # led-ul se face rosu cand se termina nivelelele
        else:
            if countdown == 3:
                draw_text('Toata lumea la nava!', font40, white, int(screen_width / 2 - 170),
                          int(screen_height / 2 + 50))
            elif countdown == 2:
                draw_text('Fiti gata de atac!', font40, white, int(screen_width / 2 - 150), int(screen_height / 2 + 50))
            elif countdown == 1:
                draw_text('La lupta!', font40, white, int(screen_width / 2 - 80), int(screen_height / 2 + 50))
            draw_text(str(countdown), font40, white, int(screen_width / 2 - 10), int(screen_height / 2 + 100))

            count_timer = pygame.time.get_ticks()
            if count_timer - last_count > 1000:
                countdown -= 1
                last_count = count_timer

        draw_text(f"Score: {score}", font30, white, screen_width - 180, 10)
        draw_text(f"HighScore: {high_scores[selected_difficulty]}", font30, white, 10, 10)
        draw_text(f"Level: {level}", font30, white, screen_width // 2 - 50, 10)

        explosion_group.update()
        spaceship_group.draw(screen)
        bullet_group.draw(screen)
        spaceship_group.update()
        alien_group.draw(screen)
        alien_bullet_group.draw(screen)
        explosion_group.draw(screen)
        powerup_group.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                led_close()  # Inchide led-ul
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:  # Opreste sunetul in timpul jocului
                    sound_enabled = not sound_enabled
                    if sound_enabled:
                        explosion_fx.set_volume(0.25)
                        explosion2_fx.set_volume(0.25)
                        laser_fx.set_volume(0.25)
                    else:
                        explosion_fx.set_volume(0)
                        explosion2_fx.set_volume(0)
                        laser_fx.set_volume(0)
                if (game_over == -1 or game_over == 1) and event.key == pygame.K_RETURN:
                    in_main_menu = True


    pygame.display.update()

led_close()
arduino.close()
pygame.quit()