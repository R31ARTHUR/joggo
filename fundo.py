import pygame
import random

pygame.init()

# Configurações da tela
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Ilusão Tridimensional com Movimento de Câmera")

# Cores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Relógio para controlar a taxa de atualização
clock = pygame.time.Clock()

# Lista de estrelas
num_stars = 300  # Aumentar o número de estrelas
stars = [{"x": random.randint(-screen_width, screen_width), "y": random.randint(-screen_height, screen_height), "z": random.randint(1, 5)} for _ in range(num_stars)]

# Posição da câmera
camera_x = 0
camera_y = 0

# Função para desenhar estrelas
def draw_stars(screen, stars, camera_x, camera_y):
    for star in stars:
        # Calcula o tamanho baseado na "distância"
        size = 5 / star["z"]
        # Ajusta a posição da estrela com base na câmera
        screen_x = int((star["x"] - camera_x) / star["z"]) + screen_width // 2
        screen_y = int((star["y"] - camera_y) / star["z"]) + screen_height // 2
        pygame.draw.circle(screen, WHITE, (screen_x, screen_y), int(size))

# Loop principal do jogo
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Captura as teclas pressionadas
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        camera_x -= 5
    if keys[pygame.K_RIGHT]:
        camera_x += 5
    if keys[pygame.K_UP]:
        camera_y -= 5
    if keys[pygame.K_DOWN]:
        camera_y += 5

    # Preenche o fundo com preto
    screen.fill(BLACK)

    # Atualiza a posição das estrelas para simular movimento
    for star in stars:
        star["z"] -= 0.1
        if star["z"] <= 0:
            star["x"] = random.randint(-screen_width, screen_width)
            star["y"] = random.randint(-screen_height, screen_height)
            star["z"] = 5

    # Desenha estrelas
    draw_stars(screen, stars, camera_x, camera_y)

    # Atualiza a tela
    pygame.display.flip()

    # Controla a velocidade do loop
    clock.tick(60)

pygame.quit()