import random
import pygame
from pygame import mixer
import button

pygame.init()

# Game Clock
clock = pygame.time.Clock()
FPS = 60


# Game Window
bottom_panel = 250
screen_width = 1080
screen_height = 920

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Dungeon Delver')

# Define Game Variables
current_fighter = 1
total_fighters = 3
action_cooldown = 0
action_wait_time = 90
attack = False
potion = False
potion_effect = 15
enemy_potion_effect = 10
clicked = False
game_over = 0


# Define fonts
font = pygame.font.SysFont("Times New Roman", 26)

# Define Colors
red = (255, 0, 0)
green = (0, 255, 0)


# Load images
# Background
background_img = pygame.image.load('Assets/Battle_Battleground/1.png').convert_alpha()
bg_rect = background_img.get_rect()
potion_img = pygame.image.load('Assets/Icons/Potion.png').convert_alpha()

reset_img = pygame.image.load('Assets/Icons/Reset.png').convert_alpha()
victory_img = pygame.image.load('Assets/Icons/Victory.png').convert_alpha()
game_over_img = pygame.image.load('Assets/Icons/Game_Over.png').convert_alpha()

# Cursor Image
sword_img = pygame.image.load('Assets/Icons/sword.png').convert_alpha()

# Main UI
player_UI = pygame.image.load('Assets/Battle_UI/1.png').convert_alpha()
enemy_UI = pygame.image.load('Assets/Battle_UI/1.png').convert_alpha()

# Music
mixer.init()
mixer.music.load('Assets/Music/Background.ogg')
mixer.music.play()


def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


def draw_bg():
    screen.blit(background_img, bg_rect)


def draw_UI():
    screen.blit(player_UI, (0, screen_height - 900))
    screen.blit(enemy_UI, (630, screen_height - 900))
    draw_text(f'{warrior.name} HP: {warrior.hp}', font, red, 50, screen_height - 860)
    draw_text(f'{skeleton_1.name} HP: {skeleton_1.hp}', font, red, 680, screen_height - 860)
    draw_text(f'{skeleton_2.name} HP: {skeleton_2.hp}', font, red, 880, screen_height - 860)


class Fighter():
    def __init__(self, x, y, name, max_hp, strength, potions, scale):
        self.name = name
        self.max_hp = max_hp
        self.hp = max_hp
        self.strength = strength
        self.start_potions = potions
        self.potions = potions
        self.alive = True
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()
        temp_list = []
        for i in range(4):
            img = pygame.image.load(f'Assets/{self.name}/Idle/{i}.png')
            img = pygame.transform.scale(img, (img.get_width() * 3, img.get_height() * 3))
            temp_list.append(img)
        self.animation_list.append(temp_list)
        temp_list = []
        for i in range(7):
            img = pygame.image.load(f'Assets/{self.name}/Attack/{i}.png')
            img = pygame.transform.scale(img, (img.get_width() * 3, img.get_height() * 3))
            temp_list.append(img)
        self.animation_list.append(temp_list)
        temp_list = []
        for i in range(4):
            img = pygame.image.load(f'Assets/{self.name}/Hit/{i}.png')
            img = pygame.transform.scale(img, (img.get_width() * 3, img.get_height() * 3))
            temp_list.append(img)
        self.animation_list.append(temp_list)
        temp_list = []
        for i in range(6):
            img = pygame.image.load(f'Assets/{self.name}/Death/{i}.png')
            img = pygame.transform.scale(img, (img.get_width() * 3, img.get_height() * 3))
            temp_list.append(img)
        self.animation_list.append(temp_list)
        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self):
        animation_cooldown = 100
        # handle animation
        # update image
        self.image = self.animation_list[self.action][self.frame_index]
        # check if enough time has passed since the last update
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        # if the animation has run out then reset back to the start
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.idle()

    def idle(self):
        self.action = 0
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()

    def attack(self, target):
        rand = random.randint(-5, 5)
        damage = self.strength + rand
        target.hp -= damage
        target.hurt()
        if target.hp < 1:
            target.hp = 0
            target.alive = False
            target.death()
        damage_text = DamageText(target.rect.centerx, target.rect.centery, str(damage), red)
        damage_text_group.add(damage_text)
        self.action = 1
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()

    def hurt(self):
        self.action = 2
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()

    def death(self):
        self.action = 3
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()

    def reset(self):
        self.alive = True
        self.hp = self.max_hp
        self.potions = self.start_potions
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()

    def draw(self):
        screen.blit(self.image, self.rect)


class Health_Bar():
    def __init__(self, x, y, hp, max_hp):
        self.x = x
        self.y = y
        self.hp = hp
        self.max_hp = max_hp

    def draw(self, hp):
        self.hp = hp
        ratio = self.hp / self.max_hp
        pygame.draw.rect(screen, red, (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, green, (self.x, self.y, 150 * ratio, 20))


class DamageText(pygame.sprite.Sprite):
    def __init__(self, x, y, damage, color):
        pygame.sprite.Sprite.__init__(self)
        self.image = font.render(damage, True, color)
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.counter = 0

    def update(self):
        self.rect.y -= 1
        self.counter += 1
        if self.counter > 30:
            self.kill()


damage_text_group = pygame.sprite.Group()

warrior = Fighter(380, 750, 'Player', 45, 13, 3, 5)

skeleton_1 = Fighter(650, 700, 'Enemy', 20, 7, 1, 5)
skeleton_2 = Fighter(875, 700, 'Enemy', 20, 6, 1, 5)

enemy_list = [skeleton_1, skeleton_2]

player_health_bar = Health_Bar(50, screen_height - 825, warrior.hp, warrior.max_hp)
enemy_1_health_bar = Health_Bar(680, screen_height - 825, skeleton_1.hp, skeleton_1.max_hp)
enemy_2_health_bar = Health_Bar(880, screen_height - 825, skeleton_2.hp, skeleton_2.max_hp)

potion_button = button.Button(screen, 250, screen_height - 855, potion_img, 64, 64)
reset_button = button.Button(screen, 490, 270, reset_img, 120, 120)

run = True
while run:
    clock.tick(FPS)
    # Draw Background
    draw_bg()
    draw_UI()
    player_health_bar.draw(warrior.hp)
    enemy_1_health_bar.draw(skeleton_1.hp)
    enemy_2_health_bar.draw(skeleton_2.hp)

    warrior.update()
    warrior.draw()
    for enemy in enemy_list:
        enemy.update()
        enemy.draw()

    damage_text_group.update()
    damage_text_group.draw(screen)

    attack = False
    potion = False
    target = None

    pygame.mouse.set_visible(True)
    pos = pygame.mouse.get_pos()

    for count, enemy in enumerate(enemy_list):
        if enemy.rect.collidepoint(pos):
            pygame.mouse.set_visible(False)
            screen.blit(sword_img, pos)
            if clicked and enemy.alive == True:
                attack = True
                target = enemy_list[count]

    if potion_button.draw():
        potion = True

    draw_text(str(warrior.potions), font, red, 325, screen_height - 855)

    if game_over == 0:
        if warrior.alive:
            if current_fighter == 1:
                action_cooldown += 1
                if action_cooldown >= action_wait_time:
                    if attack == True and target != None:
                        warrior.attack(target)
                        current_fighter += 1
                        action_cooldown = 0

                    if potion == True:
                        if warrior.potions > 0:
                            if warrior.max_hp - warrior.hp > potion_effect:
                                heal_amount = potion_effect
                            else:
                                heal_amount = warrior.max_hp - warrior.hp
                            warrior.hp += heal_amount
                            warrior.potions -= 1
                            damage_text = DamageText(warrior.rect.centerx, warrior.rect.centery, str(heal_amount), green)
                            damage_text_group.add(damage_text)
                            current_fighter += 1
                            action_cooldown = 0
        else:
            game_over = -1

        for count, enemy in enumerate(enemy_list):
            if current_fighter == 2 + count:
                if enemy.alive == True:
                    action_cooldown += 1
                    if action_cooldown >= action_wait_time:
                        if(enemy.hp / enemy.max_hp) < 0.5 and enemy.potions > 0:
                            if enemy.max_hp - enemy.hp > enemy_potion_effect:
                                heal_amount = enemy_potion_effect
                            else:
                                heal_amount = enemy.max_hp - enemy.hp
                            enemy.hp += heal_amount
                            enemy.potions -= 1
                            damage_text = DamageText(enemy.rect.centerx, enemy.rect.centery, str(heal_amount), green)
                            damage_text_group.add(damage_text)
                            current_fighter += 1
                            action_cooldown = 0
                        else:
                            enemy.attack(warrior)
                            current_fighter += 1
                            action_cooldown = 0
                else:
                    current_fighter += 1

        if current_fighter > total_fighters:
            current_fighter = 1

    alive_enemies = 0
    for enemy in enemy_list:
        if enemy.alive == True:
            alive_enemies += 1
    if alive_enemies == 0:
        game_over = 1

    if game_over != 0:
        if game_over == 1:
            screen.blit(victory_img, (415, 200))
        if game_over == -1:
            screen.blit(game_over_img, (460, 200))
        if reset_button.draw():
            warrior.reset()
            for enemy in enemy_list:
                enemy.reset()
                current_fighter = 1
                action_cooldown
                game_over = 0


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            clicked = True
        else:
            clicked = False

    pygame.display.update()


pygame.quit()
