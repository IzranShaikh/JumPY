#Sprites for JumPY!!!
import pygame
from settings import *
import random

vec = pygame.math.Vector2

class Spritesheet:
    #class for loading and parsing spritesheets from xml and spritesheet file
    def __init__(self, spritefilename):
        self.spritesheet = pygame.image.load(spritefilename).convert()

    def get_spimage(self, x, y, swidth, sheight):
        #grab an image out of a larg spritesheet
        spimage = pygame.Surface((swidth, sheight))
        spimage.blit(self.spritesheet, (0, 0), (x, y, swidth, sheight))
        spimage = pygame.transform.scale(spimage, (swidth //2, sheight // 2))
        return spimage

class Player(pygame.sprite.Sprite):
    def __init__(self, izran):
        self.groups = izran.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.izran = izran
        self.walking  = False
        self.jumping = False
        self.current_frame = 0
        self.last_update = 0
        self.load_images()
        self.image = self.standing_frames[0]
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH/2,HEIGHT/2)
        self.pos = vec(40,HEIGHT-100)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)

    def load_images(self):
        self.standing_frames = [self.izran.spritesheet.get_spimage(614, 1063 ,120, 191),
                                             self.izran.spritesheet.get_spimage(690, 406, 120, 201)]

        for frame in self.standing_frames:
            frame.set_colorkey(black)

        self.walk_frames_r = [self.izran.spritesheet.get_spimage(678, 860, 120, 201),
                                            self.izran.spritesheet.get_spimage(692, 1458, 120, 207)]
        self.walk_frames_l = []

        for frame in self.walk_frames_r:
            frame.set_colorkey(black)
            self.walk_frames_l.append(pygame.transform.flip(frame, True, False))

        self.jump_frame = self.izran.spritesheet.get_spimage(382, 763, 150, 181)
        frame.set_colorkey(black)

    def jump_cut(self):
        if self.jumping:
            if self.vel.y < -5:
                self.vel.y =- 5

    def jump(self):
        #jump if on any platform
        self.rect.x += 2
        hits = pygame.sprite.spritecollide(self,self.izran.platforms,False)
        self.rect.x -= 2
        if hits and not self.jumping:
            self.izran.jump_sound.play()
            self.jumping = True
            self.vel.y = jump_val

    def update(self):
        self.animate()
        self.acc = vec(0, player_grav)
        #Events and Movements for Sprites
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.acc.x = -player_acc
        if keys[pygame.K_RIGHT]:
            self.acc.x = player_acc

        #Applying Friction
        self.acc.x += self.vel.x * player_friction
        #Equations of Motion
        self.vel += self.acc
        self.pos += self.vel + 0.5 * self.acc

        #Wrap around the sides of the screen || player can't go of the screen
        if self.pos.x > WIDTH + self.rect.width/2:
            self.pos.x = 0 - self.rect.width/2
        if self.pos.x < 0 - self.rect.width/2:
            self.pos.x = WIDTH + self.rect.width/2

        #never fall mod
        if self.pos.y > HEIGHT:
            self.pos.y = 0

        self.rect.midbottom = self.pos

    def animate(self):
        now = pygame.time.get_ticks()
        if self.vel.x != 0:
            self.walking = True
        else:
            self.walking = False
        if self.walking:
            if now - self.last_update > 250:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.walk_frames_l)
                char_bottom = self.rect.bottom
                if self.vel.x > 0:
                    self.image = self.walk_frames_r[self.current_frame]
                    self.vel.x = 0
                else:
                    self.image = self.walk_frames_l[self.current_frame]
                    self.vel.x = 0
                self.rect = self.image.get_rect()
                self.rect.bottom = char_bottom

        if not self.jumping and not self.walking:
            if now - self.last_update > 350:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.standing_frames)
                char_bottom = self.rect.bottom
                self.image = self.standing_frames[self.current_frame]
                self.rect = self.image.get_rect()
                self.rect.bottom = char_bottom

class Platform(pygame.sprite.Sprite):
    def __init__(self, izran, x, y):
        self.groups = izran.all_sprites, izran.platforms
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.izran = izran
        platimages = [self.izran.spritesheet.get_spimage(0, 288, 380, 94),
                             self.izran.spritesheet.get_spimage(213, 1662, 201, 100),
                             self.izran.spritesheet.get_spimage(0, 768, 380, 94),
                             self.izran.spritesheet.get_spimage(213, 1764, 201, 100),
                             self.izran.spritesheet.get_spimage(0, 672, 380, 94),
                             self.izran.spritesheet.get_spimage(208, 1879, 201, 100),
                             self.izran.spritesheet.get_spimage(0, 96, 380, 94),
                             self.izran.spritesheet.get_spimage(382, 408, 200, 100)]
        self.image = random.choice(platimages)
        self.image.set_colorkey(black)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        if random.randrange(100) < pow_spawn_pct:
            Power_ups_jetboost(self.izran, self)
            Power_ups_scorebooster(self.izran, self)

class Power_ups_jetboost(pygame.sprite.Sprite):
    def __init__(self, izran, plat):
        self.groups = izran.all_sprites, izran.power_ups
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.izran = izran
        self.plat = plat
        self.type = random.choice(['boost'])
        self.pow_boostimageslist = [self.izran.spritesheet.get_spimage(820, 1805, 71, 70),
                                         self.izran.spritesheet.get_spimage(826, 1292, 71, 70)]
        self.image = random.choice(self.pow_boostimageslist)
        self.image.set_colorkey(black)
        self.rect = self.image.get_rect()
        self.rect.centerx = self.plat.rect.centerx
        self.rect.bottom = self.plat.rect.top -5

    def update(self):
        self.rect.bottom = self.plat.rect.top - 5
        if not self.izran.platforms.has(self.plat):
            self.kill()

class Power_ups_scorebooster(pygame.sprite.Sprite):
    def __init__(self, izran, plat):
        self.groups = izran.all_sprites, izran.power_upsc
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.izran = izran
        self.plat = plat
        self.type = random.choice(['scoreboost'])
        self.pow_scboostimageslist = [self.izran.spritesheet.get_spimage(244, 1981, 61, 61),
                                                       self.izran.spritesheet.get_spimage(820, 1733, 78, 70)
                                                    ]
        self.image = random.choice(self.pow_scboostimageslist)
        self.image.set_colorkey(black)
        self.rect = self.image.get_rect()
        self.rect.centerx = self.plat.rect.centerx-50
        self.rect.bottom = self.plat.rect.top -5

    def update(self):
        self.rect.bottom = self.plat.rect.top - 5
        if not self.izran.platforms.has(self.plat):
            self.kill()
