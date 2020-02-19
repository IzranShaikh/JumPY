#####JumPY!!!#####

import pygame
import random
import time
from settings import *
from sprites import *
from os import path

class Jumpy:
    def __init__(self):
        # initialize game window, etc
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(title)
        self.clock = pygame.time.Clock()
        self.running = True
        self.load_data()

    def load_data(self):
        self.dir = path.dirname(__file__)
        img_dir = path.join(self.dir, 'images')
        with open(path.join(self.dir, HS_FILE), 'r') as f:
            try:
                self.highscore = int(f.read())
            except:
                self.highscore = 0

        #load spritesheet images
        self.spritesheet = Spritesheet(path.join(img_dir, SPRITESHEET))
        #load sounds and music
        self.sound_dir = path.join(self.dir, 'snd')
        self.jump_sound = pygame.mixer.Sound(path.join(self.sound_dir, 'Jump33.wav'))

    def new(self):
        # start a new game
        self.score = 0
        self.all_sprites = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.power_ups = pygame.sprite.Group()
        self.power_upsc = pygame.sprite.Group()
        self.player = Player(self)
        #Platforms
        for plats in platform_list:
            Platform(self, *plats)
        pygame.mixer.music.load(path.join(self.sound_dir, 'Happy Tune.ogg'))
        self.run()

    def run(self):
        # Game Loop
        pygame.mixer.music.fadeout(1)
        pygame.mixer.music.play(loops=-1)
        self.playing = True
        while self.playing:
            self.clock.tick(fps)
            self.events()
            self.draw()
            self.update()
        pygame.mixer.music.fadeout(1)

    def update(self):
        # Game Loop - Update
        self.all_sprites.update()
        #check if player hits a platform - only if falling
        if self.player.vel.y > 0:
            hits = pygame.sprite.spritecollide(self.player, self.platforms, False)
            if hits:
                lowest = hits[0]
                for hit in hits:
                    if hit.rect.bottom > lowest.rect.centery:
                        lowest = hit
                if self.player.pos.x < lowest.rect.right + 10 and \
                    self.player.pos.x > lowest.rect.left - 10:
                    if self.player.pos.y < lowest.rect.bottom:
                        self.player.vel.y = 0
                        self.player.pos.y = lowest.rect.top
                        self.player.jumping = False

        #if player reacher top 1/4  of screen || scrolling window upwards
        if self.player.rect.top <= HEIGHT/4:
            self.player.pos.y += max(abs(self.player.vel.y), 2)
            for plats in self.platforms:
                plats.rect.y += max(abs(self.player.vel.y), 2)

                #to destroy platforms that are not visible || explored and are way down
                #reason
                    #saves processing time
                    #deallocates all memories which aren't in use
                if plats.rect.top >= HEIGHT:
                    plats.kill()
                    self.score += get_score

        #Die!
        if self.player.rect.bottom > HEIGHT:
            for sprite in self.all_sprites:
                sprite.rect.y -= max(self.player.vel.y, 10)
                if sprite.rect.bottom < 0:
                    sprite.kill()
        if len(self.platforms) == 0:
            self.playing = False
            self.show_go_screen()

        #spawn new platforms
        while len(self.platforms) < platforms_on_screen:
            rWIDTH = random.randrange(50, 100)
            Platform(self, random.randrange(0, WIDTH - rWIDTH),
                         random.randrange(-75, -30))

        #Power-Ups
        keys = pygame.key.get_pressed()
        hits = pygame.sprite.spritecollide(self.player, self.power_ups, False)
        if hits and keys[pygame.K_u]:
            self.player.vel.y = boost_power
        hitsc = pygame.sprite.spritecollide(self.player, self.power_upsc, True)
        if hitsc:
            self.score += 500

    def events(self):
        # Game Loop - events
        for event in pygame.event.get():
            # check for closing window
            if event.type == pygame.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False

            #Jumping
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                    self.player.jump()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                    self.player.jump_cut()

    def draw(self):
        # Game Loop - draw
        self.screen.fill(lightblue)
        self.all_sprites.draw(self.screen)
        #player on top
        self.screen.blit(self.player.image, self.player.rect)
        #priniting score
        self.message_to_screen('Score - '+str(self.score), 22, ghostwhite, WIDTH/2, 15, 'Comic Sans MS')

        # *after* drawing everything, flip the display, update screen contents
        pygame.display.flip()

    def show_start_screen(self):
        # game start screen
        pygame.mixer.music.load(path.join(self.sound_dir, 'Yippee.ogg'))
        pygame.mixer.music.play(loops=-1)
        self.screen.fill(darkslateblue)
        self.message_to_screen(title, 48, white, WIDTH/2, HEIGHT/4, 'Comic Sans MS')
        self.message_to_screen('Arrows to move, Space to jump', 22, white, WIDTH/2, HEIGHT/2, 'Comic Sans MS')
        self.message_to_screen('u to use powerups', 22, ghostwhite, WIDTH/2, HEIGHT/2+20 , 'Comic Sans MS')
        self.message_to_screen("Press any key to play", 22,blue2, WIDTH/2, HEIGHT*3/4, 'Comic Sans MS')
        self.message_to_screen("High Score : "+str(self.highscore), 22,blue2, WIDTH/2, 15, 'Comic Sans MS')
        pygame.display.flip();
        self.wait_for_key()

    def show_go_screen(self):
        # game over/continue
        if self.running == False:
            #end this method if player directly clicks close window button // don't show_go_screen if pygame.QUIT event is performed
            return

        pygame.mixer.music.load(path.join(self.sound_dir, 'Yippee.ogg'))
        pygame.mixer.music.play(loops=-1)
        self.screen.fill(darkslateblue)
        self.message_to_screen('Game Over!!!',48, white, WIDTH/2, HEIGHT/4, 'Comic Sans MS')
        self.message_to_screen("Your Score : "+str(self.score),22, crimson, WIDTH/2, HEIGHT/2, 'Comic Sans MS')
        self.message_to_screen("Press any key to play again",22, blue2, WIDTH/2, HEIGHT*3/4, 'Comic Sans MS')
        if self.score > self.highscore:
            self.highscore = self.score
            self.message_to_screen("NEW HIGH SCORE",22,blue2,WIDTH/2,HEIGHT/2+100,'Comic Sans MS')
            with open(path.join(self.dir, HS_FILE), 'w') as f:
                f.write(str(self.score))
        else:
            self.message_to_screen("High Score : "+str(self.highscore),22, blue2, WIDTH/2, HEIGHT/2+40, 'Comic Sans MS')

        pygame.display.flip()
        self.wait_for_key()
        pygame.mixer.music.fadeout(1)

    def wait_for_key(self):
        #show screens until user press any key
        waiting = True
        while waiting:
            self.clock.tick(fps)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                    self.running = False
                if event.type == pygame.KEYUP:
                    waiting = False

    #method for cutom message on game screen
    def message_to_screen(self, msg, fontsize, color, msgxpos, msgypos, fontname):
        font_name = pygame.font.match_font(fontname)
        font = pygame.font.Font(font_name, fontsize)
        text_surface = font.render(msg, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (msgxpos, msgypos)
        self.screen.blit(text_surface, text_rect)

#object for class Jumpy
g = Jumpy()

g.show_start_screen()
while g.running:
    g.new()
    g.show_go_screen()

pygame.quit()
time.sleep(0.2)
quit()
