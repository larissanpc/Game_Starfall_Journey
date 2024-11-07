import math
import pygame
from sys import exit
from random import *
from pygame.locals import*

# inicialização pygame
pygame.init()
pygame.font.init()
font = pygame.font.Font(None, 36)  # Você pode ajustar o tamanho da fonte

# config da tela
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Starfall Journey')

nave_image = pygame.image.load('maninhoV2.png')
collision_star_sound = pygame.mixer.Sound("coin_flip.wav")

nave_image = pygame.transform.scale(nave_image, (60, 70))

chao_image = pygame.image.load('chao.png')
chao_image = pygame.transform.scale(chao_image, (screen_width, 100))  # ajusta o chão para a largura da tela
predio_image=pygame.image.load('predio.png')
predio_image = pygame.transform.scale(predio_image, (272, 320))  # ajusta o chão para a largura da tela
starfall_image = pygame.image.load('starfall.png')  # A imagem de fundo do menu
starfall_image = pygame.transform.scale(starfall_image, (screen_width, screen_height))  # Ajusta o tamanho do fundo
cloud_image=pygame.image.load('nuvem.png')
# Fonte para os botões
option_font = pygame.font.Font(None, 48)

nave_image = pygame.transform.scale(nave_image,(60,70))

color_transition = []

def interpolate_color(color1, color2, factor):
    """ Interpolates between two colors based on a factor between 0 and 1."""
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
        self.image = self.image_direita
        self.rect = self.image.get_rect()
        self.direction = True
        self.pause= False

        
    def update(self):
        keys = pygame.key.get_pressed()
        if self.pause==False:
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

    def descer(self, chao_y):
        """Desce a nave suavemente até tocar o chão"""
        if self.position.y < chao_y + 15:  # ajusta para o topo da nave tocar o chão
            self.position.y += 1  # ajusta a velocidade de descida
            return False
        self.pause=True# ainda não chegou ao chão
        return True  # chegou ao chão
class Cloud(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super(Cloud, self).__init__()
        self.position = pygame.math.Vector2(x, y)
        self.speed = 2
        self.image = pygame.image.load('nuvem.png')
        self.image = pygame.transform.scale(self.image, (70, 30))
        
        self.rect = self.image.get_rect()
        self.rect.center = self.position

    def update(self):
        self.position.y -= self.speed
        self.rect.center = self.position
        #remove o asteroide
        if self.position.y < 0:
            self.kill()


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
class AsteroideDoMal(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super(AsteroideDoMal, self).__init__()
        self.position = pygame.math.Vector2(x, y)
        self.speed = 3
        sla=randrange(0,2)
        escolhedor=randrange(0,3)
        if escolhedor==0:
            self.image = pygame.image.load('bomba.png')
            self.image = pygame.transform.scale(self.image, (40, 40))
        elif escolhedor==1:
            self.image = pygame.image.load('pipa.png')
            self.image = pygame.transform.scale(self.image, (45, 35))

        elif escolhedor==2:
            self.image = pygame.image.load('aguia.png')
            self.image = pygame.transform.scale(self.image, (45, 45))


        self.image_direita = self.image
        self.image_esquerda = pygame.transform.flip(self.image, True, False)

        if(sla==0):
            self.speedx = 2
            self.image=self.image_direita
        else:
            self.speedx = -2
            self.image=self.image_esquerda
        
        self.rect = self.image.get_rect()
        self.rect.center = self.position

    def update(self):
        self.position.y -= self.speed
        self.position.x+=self.speedx

        self.rect.center = self.position
        #remove o asteroide
        if self.position.y < 0:
            self.kill()

# funcao principal do jogo
def main(color_transition):
    nave = NaveEspacial("Nave 1")
    all_sprites = pygame.sprite.Group()
    asteroides = pygame.sprite.Group()
    asteroidesDosMais = pygame.sprite.Group()
    clouds=pygame.sprite.Group()
    all_sprites.add(nave)
    clock = pygame.time.Clock()
    running = True
    pos_x_antigo=screen_width/2
    # controle time criação asteroides
    last_asteroid_time = pygame.time.get_ticks()
    asteroid_delay = 500  # intervalo entre asteroides
    last_cloud_time = pygame.time.get_ticks()
    cloud_delay = 500
    last_bomb_time = pygame.time.get_ticks()
    bomb_delay=2500
    transition_index = 0
    transition_duration = 5000  # duracao da cor
    last_transition_time = pygame.time.get_ticks()
    transition_factor = 0
    vida=3
    # variavel de deslocamento da tela
    background_y = 0
    background_speed = 2  # velocidade do movimento de fundo

    # variáveis para controlar o chão
    chao_visible = False
    chao_y = screen_height  # começar fora da tela
    chao_speed = 0.875  # velocidade suave para o chão subir
    chao_fixo = False  # controlar se o chão parou de se mover
    predio_visible=False
    predioy=screen_height
    prediospeed=0.9
    prediofixo=False
    restart_timer = 0  # temporizador para reiniciar
    restart_delay = 5000  # tempo antes de reiniciar em milissegundos
    asteroide_pause=False
    cloud_pause=False
    pomtos=0
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
                
        keys = pygame.key.get_pressed()

        # colisões
        collided_asteroids = pygame.sprite.spritecollide(nave, asteroides, True)
        if(collided_asteroids):
            collision_star_sound.play()
            pomtos+=1
        collided_asteroidsDosMais = pygame.sprite.spritecollide(nave, asteroidesDosMais, True)
        if(collided_asteroidsDosMais) and vida>0:
            collision_star_sound.play()
            vida-=1

        all_sprites.update()

        # tempo controlado
        current_time = pygame.time.get_ticks()
        if current_time - last_asteroid_time > asteroid_delay and asteroide_pause==False:
            pos_x = randrange(0, 2)
            if pos_x==1 and pos_x_antigo+50<=screen_width-100:
                pos_x=pos_x_antigo+50
            elif pos_x==0 and pos_x_antigo-50>=100:
                pos_x=pos_x_antigo-50
            else:
                pos_x=pos_x_antigo
            asteroide = Asteroide(pos_x, screen_height)
            all_sprites.add(asteroide)
            asteroides.add(asteroide)
            last_asteroid_time = current_time  # att tempo
            pos_x_antigo=pos_x

            
        current_bomb_time = pygame.time.get_ticks()
        if current_bomb_time - last_bomb_time > bomb_delay and asteroide_pause==False:
            pos_xMal= randrange(0, screen_width)

            asteroideDoMal=AsteroideDoMal(pos_xMal,screen_height)
            all_sprites.add(asteroideDoMal)
            asteroidesDosMais.add(asteroideDoMal)
            last_bomb_time = current_bomb_time  # att tempo

        current_time_cloud = pygame.time.get_ticks()

        if current_time_cloud - last_cloud_time > cloud_delay and cloud_pause==False:
            pos_xNuvem = randrange(0, screen_width)
            cloud=Cloud(pos_xNuvem,screen_width)
            all_sprites.add(cloud)
            last_cloud_time = current_time_cloud
        # controle da transição de cores
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
        # Ativa o chão apenas quando a cor mais clara for alcançada (Light Blue)
        if transition_index == len(color_transition) - 1 or vida==0:
            chao_visible = True
        
        if transition_index == len(color_transition) - 2 or vida==0:
            predio_visible = True

        # movimentação do fundo (rolling screen)
        background_y += background_speed
        if background_y >= screen_height:
            background_y = 0

        # desenhar o fundo rolando
        screen.fill(current_color)
        pygame.draw.rect(screen, current_color, (0, background_y - screen_height, screen_width, screen_height))
        pygame.draw.rect(screen, current_color, (0, background_y, screen_width, screen_height))
        if predio_visible:
            cloud_pause=True

            if predioy > screen_height - 370:
                predioy -= prediospeed
            else:
                prediofixo=True
            screen.blit(predio_image,(0,predioy))
        # desenhar o chão se visível
        if chao_visible:
            asteroide_pause=True
            if chao_y > screen_height - 100:  # posição final do chão (tamanho da imagem)
                chao_y -= chao_speed  # fazer o chão subir lentamente
            else:
                chao_fixo = True  # chão parou de se mover quando alcança sua posição final
            screen.blit(chao_image, (0, chao_y))
        
        # Se o chão está fixo, faz a nave descer lentamente até o chão
        if chao_fixo:
            if nave.descer(chao_y):  # verifica se a nave chegou ao chão
                restart_timer += clock.get_time()
                distancia=nave.position.x-screen_width/2
                distancia/=100
                if(distancia<=0):
                    distancia*=-1
                pontos_distancia = font.render(f'Distancia: {distancia}', True, (255, 255, 255))  # Texto branco
                screen.blit(pontos_distancia, (screen_height/2, screen_width/2))  # Desenha no canto superior esquerdo

                if restart_timer >= restart_delay:  # se passaram 5 segundos
                    nave.pause=False
                    asteroide_pause=True
                    pomtos=0
                    menu()  # reinicia o jogo

        # desenhar todos os sprites
        all_sprites.draw(screen)
        pontos_texto = font.render(f'Pontos: {pomtos}', True, (255, 255, 255))  # Texto branco
        screen.blit(pontos_texto, (10, 10))  # Desenha no canto superior esquerdo

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
def menu():
    """Tela principal de menu com as opções de iniciar ou sair"""
    menu_running = True
    selected_option = 0  # 0 = 'Iniciar', 1 = 'Sair'
    
    while menu_running:
        for event in pygame.event.get():
            if event.type == QUIT:
                menu_running = False
                pygame.quit()
                exit()

            # Navegação com as teclas
            if event.type == KEYDOWN:
                if event.key == K_DOWN:
                    selected_option = (selected_option + 1) % 3  # Alterna entre 0 e 1 (Iniciar ou Sair)
                elif event.key == K_UP:
                    selected_option = (selected_option - 1) % 3  # Alterna entre 0 e 1
                elif event.key == K_RETURN:
                    if selected_option == 0:
                        color_transition = [
                            #(0, 0, 128),     # Navy Blue
                            #(75, 0, 130),    # Indigo
                            #(123, 104, 238), # Medium Slate Blue
                            (30, 144, 255),  # Dodger Blue
                            (30, 144, 255),  # Dodger Blue
                            (135, 206, 250), # Light Sky Blue
                            (135, 206, 250), # Light Sky Blue
                            (173, 216, 230),  # Light Blue (cor mais clara)
                            (173, 216, 230)  # Light Blue (cor mais clara)
                        ]
                        main(color_transition)  # Inicia o jogo facil
                    elif selected_option == 1:
                        color_transition = [
                            #(0, 0, 128),     # Navy Blue
                            (75, 0, 130),    # Indigo
                            (75, 0, 130),    # Indigo
                            (123, 104, 238), # Medium Slate Blue
                            (123, 104, 238), # Medium Slate Blue
                            (30, 144, 255),  # Dodger Blue
                            (30, 144, 255),  # Dodger Blue
                            (135, 206, 250), # Light Sky Blue
                            (135, 206, 250), # Light Sky Blue
                            (173, 216, 230),  # Light Blue (cor mais clara)
                            (173, 216, 230)  # Light Blue (cor mais clara)
                        ]
                        main(color_transition)  # Inicia o jogo medio
                    elif selected_option == 2:
                        color_transition = [
                            (0,0,0),
                                                        (0,0,0),

                            (0, 0, 128),     # Navy Blue
                            (0, 0, 128),     # Navy Blue
                            (75, 0, 130),    # Indigo
                            (75, 0, 130),    # Indigo
                            (123, 104, 238), # Medium Slate Blue
                            (123, 104, 238), # Medium Slate Blue
                            (30, 144, 255),  # Dodger Blue
                            (30, 144, 255),  # Dodger Blue
                            (135, 206, 250), # Light Sky Blue
                            (135, 206, 250), # Light Sky Blue
                            (173, 216, 230),  # Light Blue (cor mais clara)
                            (173, 216, 230)  # Light Blue (cor mais clara)
                        ]
                        main(color_transition)  # Inicia o jogo dificil
                    elif selected_option == 3:
                        pygame.quit()  # Inicia o jogo medio
                        exit()

        # Desenha o fundo com a imagem 'starfall.png'
        screen.blit(starfall_image, (0, 0))  # Desenha a imagem do fundo na tela

        # Desenha as opções do menu
        easy_text = option_font.render("Fácil", True, (255, 255, 255))  # Opção 'Facil' em branco
        medium_text = option_font.render("Médio", True, (255, 255, 255))  # Opção 'Medio' em branco
        hard_text = option_font.render("Difícil", True, (255, 255, 255))  # Opção 'Dificil' em branco

        quit_text = option_font.render("Sair", True, (255, 255, 255))  # Opção 'Sair' em branco

        # Destaca a opção selecionada
        if selected_option == 0:
            pygame.draw.rect(screen, (255, 255, 0), (screen_width // 2 - easy_text.get_width() // 2 - 10, screen_height // 2 - 75, easy_text.get_width() + 20, easy_text.get_height() + 10), 3)
        if selected_option == 1:
            pygame.draw.rect(screen, (255, 255, 0), (screen_width // 2 - medium_text.get_width() // 2 - 10, screen_height // 2 + 5, medium_text.get_width() + 20, medium_text.get_height() + 10), 3)
        if selected_option == 2:
            pygame.draw.rect(screen, (255, 255, 0), (screen_width // 2 - hard_text.get_width() // 2 - 10, screen_height // 2 + 85, hard_text.get_width() + 20, hard_text.get_height() + 10), 3)

        if selected_option == 3:
            pygame.draw.rect(screen, (255, 255, 0), (screen_width // 2 - quit_text.get_width() // 2 - 10, screen_height // 2 + 25, quit_text.get_width() + 20, quit_text.get_height() + 10), 3)

        # Exibe as opções
        screen.blit(easy_text, (screen_width // 2 - easy_text.get_width() // 2, screen_height // 2 - 70))
        screen.blit(medium_text, (screen_width // 2 - medium_text.get_width() // 2, screen_height // 2 + 10))
        screen.blit(hard_text, (screen_width // 2 - hard_text.get_width() // 2, screen_height // 2 + 90))

        #screen.blit(quit_text, (screen_width // 2 - quit_text.get_width() // 2, screen_height // 2 + 30))

        pygame.display.flip()  # Atualiza a tela
        pygame.time.Clock().tick(60)  # Limita a taxa de quadros para 60 FPS

# Chama o menu
if __name__ == "__main__":
    menu()  # Inicia o menu principal
