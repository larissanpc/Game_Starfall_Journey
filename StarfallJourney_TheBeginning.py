import math
import pygame
from sys import exit
from random import *
from pygame.locals import*

# inicialização pygame
pygame.init()

# config da tela
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Starfall Journey')

nave_image = pygame.image.load('maninhoV1.png')
nave_image = pygame.transform.scale(nave_image,(60,70))

color_transition = [
    (0, 0, 128),     # Navy Blue
    (75, 0, 130),    # Indigo
    (123, 104, 238), # Medium Slate Blue
    (30, 144, 255),  # Dodger Blue
    (135, 206, 250), # Light Sky Blue
    (173, 216, 230)  # Light Blue
]


class Floor(pygame.sprite.Sprite):
    def __init__(self,name):
        super(Floor,self).__init__()
        self.image = pygame.image.load('chao.png').convert_alpha()  # Carrega a imagem do chão
        self.rect = self.image.get_rect(topleft=(0, 600))  #        

def interpolate_color(color1, color2, factor):
    """ interpolates between two colors based on a factor between 0 and 1."""
    return (
        int(color1[0] + (color2[0] - color1[0]) * factor),
        int(color1[1] + (color2[1] - color1[1]) * factor),
        int(color1[2] + (color2[2] - color1[2]) * factor)
    )


class NaveEspacial(pygame.sprite.Sprite):
    def __init__(self, name):
        super(NaveEspacial, self).__init__()
        self.name = name
        self.alive = True
        self.position = pygame.math.Vector2(screen_width // 2, screen_height // 2)
        self.direction = 0 #direcao inicial 0 graus
        self.speed = 5 # velocidade da nave
        self.shield = 100
        self.energy = 100
        
        self.image_direita = nave_image
        self.image_esquerda = pygame.transform.flip(nave_image, True, False)
        self.image=self.image_direita
        self.rect = self.image.get_rect()
        self.direction = True


    def update(self):
        keys = pygame.key.get_pressed()

        # movimentacao
        if keys[K_LEFT]:
            self.position.x -= self.speed
            self.direction = False

        if keys[K_RIGHT]:
            self.position.x += self.speed
            self.direction = True

        if self.direction:
            self.image = self.image_direita
        else:
            self.image = self.image_esquerda


        # atualiza a posicao do retangulo da nave
        self.rect.center = self.position

 

# classe asteroide
class Asteroide(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super(Asteroide, self).__init__()
        self.position = pygame.math.Vector2(x, y)
        self.speed = 5
        self.image = pygame.image.load('pixel_star.png')
        self.image = pygame.transform.scale(self.image, (30, 30))
        
        self.rect = self.image.get_rect()
        self.rect.center = self.position

    def update(self):
        self.position.y -= self.speed
        self.rect.center = self.position
        #remove o asteroide
        if self.position.y < 0:
            self.kill()

# funcao principal do jogo
def main():
    nave = NaveEspacial("Nave 1")
    all_sprites = pygame.sprite.Group()
    asteroides = pygame.sprite.Group()

    all_sprites.add(nave)
    
    clock = pygame.time.Clock()
    running = True

    #controle time criação asteroides
    last_asteroid_time = pygame.time.get_ticks()
    asteroid_delay = 2000  #intervalo entre asteroides

    transition_index = 0
    transition_duration = 5000  #duracao da cor
    last_transition_time = pygame.time.get_ticks()
    transition_factor = 0
    floor = Floor("Chão")
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
                
        keys = pygame.key.get_pressed()

        collided_asteroids = pygame.sprite.spritecollide(nave, asteroides, True)

        all_sprites.update()


        # tempo controlado
        current_time = pygame.time.get_ticks()
        if current_time - last_asteroid_time > asteroid_delay:
            pos_x = randrange(0, screen_width)
            asteroide = Asteroide(pos_x, screen_height)
            all_sprites.add(asteroide)
            asteroides.add(asteroide)
            last_asteroid_time = current_time  # att tempo

        #screen.fill((0, 0, 0))  # preenche o fundo de preto

        if transition_index < len(color_transition) - 1:
            if current_time - last_transition_time > transition_duration:
                last_transition_time = current_time
                transition_index += 1
                transition_factor = 0

            transition_factor += clock.get_time() / transition_duration
            if transition_factor > 1:
                transition_factor = 1

            next_color_index = min(transition_index + 1, len(color_transition) - 1)

            current_color = interpolate_color(
                color_transition[transition_index], 
                color_transition[next_color_index], 
                transition_factor
            )
        else:
            current_color = color_transition[-1]

        if current_color == (173, 216, 230):
            screen.blit(floor.image, floor.rect)  # Desenha o chão
        screen.fill(current_color)
        
        all_sprites.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
