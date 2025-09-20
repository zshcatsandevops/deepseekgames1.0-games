import pygame
import random
import math
import sys

# Initialize pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pokémon-style Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (76, 187, 23)
DARK_GREEN = (47, 117, 14)
BROWN = (139, 69, 19)
BLUE = (30, 144, 255)
RED = (220, 20, 60)
YELLOW = (255, 215, 0)
LIGHT_BLUE = (173, 216, 230)
GRAY = (128, 128, 128)

# Fonts
font_large = pygame.font.SysFont('Arial', 32)
font_medium = pygame.font.SysFont('Arial', 24)
font_small = pygame.font.SysFont('Arial', 18)

# Game states
OVERWORLD = 0
BATTLE = 1
MENU = 2
game_state = OVERWORLD

# Player class
class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 32
        self.height = 32
        self.speed = 3
        self.direction = "down"
        self.pokemon = [
            {"name": "Pikachu", "hp": 35, "max_hp": 35, "level": 5, "moves": ["Thunder Shock", "Quick Attack"]}
        ]
        self.potions = 3
        
    def move(self, dx, dy, tiles):
        new_x = self.x + dx
        new_y = self.y + dy
        
        # Check collision with trees
        for tile in tiles:
            if tile[2] == "tree" and self.check_collision(new_x, new_y, tile[0], tile[1], 32, 32):
                return
        
        # Boundary checking
        if 0 <= new_x <= SCREEN_WIDTH - self.width and 0 <= new_y <= SCREEN_HEIGHT - self.height:
            self.x = new_x
            self.y = new_y
            
        # Set direction for animation
        if dx > 0:
            self.direction = "right"
        elif dx < 0:
            self.direction = "left"
        elif dy > 0:
            self.direction = "down"
        elif dy < 0:
            self.direction = "up"
    
    def check_collision(self, x1, y1, x2, y2, width2, height2):
        return (x1 < x2 + width2 and x1 + self.width > x2 and
                y1 < y2 + height2 and y1 + self.height > y2)
    
    def draw(self, screen):
        color = RED if self.direction == "right" else BLUE
        pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height))
        
        # Draw eyes based on direction
        if self.direction == "right":
            pygame.draw.rect(screen, BLACK, (self.x + 20, self.y + 8, 6, 6))
        elif self.direction == "left":
            pygame.draw.rect(screen, BLACK, (self.x + 6, self.y + 8, 6, 6))
        elif self.direction == "down":
            pygame.draw.rect(screen, BLACK, (self.x + 8, self.y + 20, 6, 6))
        else:  # up
            pygame.draw.rect(screen, BLACK, (self.x + 8, self.y + 6, 6, 6))

# Wild Pokémon class
class WildPokemon:
    def __init__(self):
        pokemon_list = [
            {"name": "Pidgey", "hp": 25, "max_hp": 25, "level": 3},
            {"name": "Rattata", "hp": 20, "max_hp": 20, "level": 2},
            {"name": "Weedle", "hp": 22, "max_hp": 22, "level": 3},
            {"name": "Caterpie", "hp": 24, "max_hp": 24, "level": 3}
        ]
        self.pokemon = random.choice(pokemon_list)
        
    def draw(self, screen):
        pygame.draw.rect(screen, LIGHT_BLUE, (SCREEN_WIDTH//2 - 50, 100, 100, 100))
        pygame.draw.rect(screen, BLACK, (SCREEN_WIDTH//2 - 50, 100, 100, 100), 2)
        
        name_text = font_medium.render(self.pokemon["name"], True, BLACK)
        level_text = font_small.render(f"Lv. {self.pokemon['level']}", True, BLACK)
        screen.blit(name_text, (SCREEN_WIDTH//2 - name_text.get_width()//2, 210))
        screen.blit(level_text, (SCREEN_WIDTH//2 - level_text.get_width()//2, 240))
        
        # HP bar
        hp_percent = self.pokemon["hp"] / self.pokemon["max_hp"]
        pygame.draw.rect(screen, GRAY, (SCREEN_WIDTH//2 - 40, 260, 80, 15))
        pygame.draw.rect(screen, GREEN if hp_percent > 0.3 else RED, 
                         (SCREEN_WIDTH//2 - 40, 260, 80 * hp_percent, 15))
        pygame.draw.rect(screen, BLACK, (SCREEN_WIDTH//2 - 40, 260, 80, 15), 1)
        
        hp_text = font_small.render(f"HP: {self.pokemon['hp']}/{self.pokemon['max_hp']}", True, BLACK)
        screen.blit(hp_text, (SCREEN_WIDTH//2 - hp_text.get_width()//2, 280))

# Create player
player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

# Create tiles for the map (x, y, type)
tiles = []
for i in range(20):
    for j in range(15):
        # Add some random trees
        if random.random() < 0.1:
            tiles.append((i * 40, j * 40, "tree"))

# Battle variables
wild_pokemon = None
battle_option = 0
battle_text = "A wild Pokémon appeared!"
battle_state = "start"  # start, player_turn, enemy_turn, end

# Game loop
clock = pygame.time.Clock()
encounter_counter = 0
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if game_state == OVERWORLD:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    game_state = MENU
        
        elif game_state == BATTLE:
            if event.type == pygame.KEYDOWN:
                if battle_state == "start":
                    if event.key == pygame.K_SPACE:
                        battle_state = "player_turn"
                        battle_text = "What will you do?"
                
                elif battle_state == "player_turn":
                    if event.key == pygame.K_UP:
                        battle_option = (battle_option - 1) % 2
                    elif event.key == pygame.K_DOWN:
                        battle_option = (battle_option + 1) % 2
                    elif event.key == pygame.K_RETURN:
                        if battle_option == 0:  # Fight
                            damage = random.randint(3, 7)
                            wild_pokemon.pokemon["hp"] -= damage
                            battle_text = f"You dealt {damage} damage!"
                            battle_state = "enemy_turn"
                        else:  # Item
                            if player.potions > 0:
                                heal = random.randint(10, 15)
                                player.pokemon[0]["hp"] = min(player.pokemon[0]["hp"] + heal, 
                                                             player.pokemon[0]["max_hp"])
                                player.potions -= 1
                                battle_text = f"Used Potion! Restored {heal} HP!"
                                battle_state = "enemy_turn"
                            else:
                                battle_text = "You have no Potions left!"
                
                elif battle_state == "enemy_turn":
                    if event.key == pygame.K_SPACE:
                        # Enemy attack
                        damage = random.randint(2, 5)
                        player.pokemon[0]["hp"] -= damage
                        battle_text = f"Enemy dealt {damage} damage!"
                        
                        # Check if player Pokémon fainted
                        if player.pokemon[0]["hp"] <= 0:
                            battle_text = "Your Pokémon fainted!"
                            battle_state = "end"
                        else:
                            battle_state = "player_turn"
                            battle_text = "What will you do?"
                
                elif battle_state == "end":
                    if event.key == pygame.K_SPACE:
                        game_state = OVERWORLD
                        battle_state = "start"
        
        elif game_state == MENU:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    game_state = OVERWORLD
    
    # Movement in overworld
    if game_state == OVERWORLD:
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_LEFT]:
            dx = -player.speed
        if keys[pygame.K_RIGHT]:
            dx = player.speed
        if keys[pygame.K_UP]:
            dy = -player.speed
        if keys[pygame.K_DOWN]:
            dy = player.speed
        
        player.move(dx, dy, tiles)
        
        # Random encounters in grass areas (based on movement)
        if dx != 0 or dy != 0:
            encounter_counter += 1
            if encounter_counter > 100 and random.random() < 0.01:
                game_state = BATTLE
                wild_pokemon = WildPokemon()
                encounter_counter = 0
    
    # Draw everything
    screen.fill(LIGHT_BLUE)  # Sky
    
    # Draw ground
    for i in range(0, SCREEN_WIDTH, 40):
        for j in range(0, SCREEN_HEIGHT, 40):
            pygame.draw.rect(screen, GREEN if (i//40 + j//40) % 2 == 0 else DARK_GREEN, 
                            (i, j, 40, 40))
    
    # Draw trees
    for tile in tiles:
        x, y, tile_type = tile
        if tile_type == "tree":
            pygame.draw.rect(screen, BROWN, (x + 14, y + 10, 12, 30))
            pygame.draw.circle(screen, GREEN, (x + 20, y + 10), 20)
    
    # Draw player
    player.draw(screen)
    
    # Draw HUD
    pygame.draw.rect(screen, WHITE, (10, 10, 200, 80))
    pygame.draw.rect(screen, BLACK, (10, 10, 200, 80), 2)
    
    name_text = font_small.render(player.pokemon[0]["name"], True, BLACK)
    level_text = font_small.render(f"Lv. {player.pokemon[0]['level']}", True, BLACK)
    screen.blit(name_text, (20, 15))
    screen.blit(level_text, (150, 15))
    
    hp_text = font_small.render("HP:", True, BLACK)
    screen.blit(hp_text, (20, 45))
    
    # HP bar
    hp_percent = player.pokemon[0]["hp"] / player.pokemon[0]["max_hp"]
    pygame.draw.rect(screen, GRAY, (60, 45, 100, 15))
    pygame.draw.rect(screen, GREEN if hp_percent > 0.3 else RED, 
                    (60, 45, 100 * hp_percent, 15))
    pygame.draw.rect(screen, BLACK, (60, 45, 100, 15), 1)
    
    hp_value = font_small.render(f"{player.pokemon[0]['hp']}/{player.pokemon[0]['max_hp']}", True, BLACK)
    screen.blit(hp_value, (165, 45))
    
    # Draw battle screen if in battle
    if game_state == BATTLE:
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        screen.blit(overlay, (0, 0))
        
        # Battle dialog box
        pygame.draw.rect(screen, WHITE, (50, 350, SCREEN_WIDTH - 100, 150))
        pygame.draw.rect(screen, BLACK, (50, 350, SCREEN_WIDTH - 100, 150), 2)
        
        # Draw battle text
        text = font_medium.render(battle_text, True, BLACK)
        screen.blit(text, (70, 370))
        
        # Draw wild Pokémon
        wild_pokemon.draw(screen)
        
        # Draw player Pokémon
        pygame.draw.rect(screen, YELLOW, (100, 300, 80, 80))
        pygame.draw.rect(screen, BLACK, (100, 300, 80, 80), 2)
        
        name_text = font_small.render(player.pokemon[0]["name"], True, BLACK)
        level_text = font_small.render(f"Lv. {player.pokemon[0]['level']}", True, BLACK)
        screen.blit(name_text, (110, 310))
        screen.blit(level_text, (160, 310))
        
        # HP bar for player Pokémon
        hp_percent = player.pokemon[0]["hp"] / player.pokemon[0]["max_hp"]
        pygame.draw.rect(screen, GRAY, (110, 330, 60, 8))
        pygame.draw.rect(screen, GREEN if hp_percent > 0.3 else RED, 
                        (110, 330, 60 * hp_percent, 8))
        pygame.draw.rect(screen, BLACK, (110, 330, 60, 8), 1)
        
        # Draw battle options if it's player's turn
        if battle_state == "player_turn":
            options = ["Fight", "Item"]
            for i, option in enumerate(options):
                color = RED if i == battle_option else BLACK
                option_text = font_medium.render(option, True, color)
                screen.blit(option_text, (70 + i*150, 420))
    
    # Draw menu if in menu state
    elif game_state == MENU:
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        screen.blit(overlay, (0, 0))
        
        # Menu box
        pygame.draw.rect(screen, WHITE, (100, 100, SCREEN_WIDTH - 200, SCREEN_HEIGHT - 200))
        pygame.draw.rect(screen, BLACK, (100, 100, SCREEN_WIDTH - 200, SCREEN_HEIGHT - 200), 2)
        
        # Menu title
        title_text = font_large.render("MENU", True, BLACK)
        screen.blit(title_text, (SCREEN_WIDTH//2 - title_text.get_width()//2, 120))
        
        # Pokémon info
        pokemon_text = font_medium.render("Pokémon", True, BLUE)
        screen.blit(pokemon_text, (150, 180))
        
        pygame.draw.rect(screen, LIGHT_BLUE, (150, 220, 200, 60))
        pygame.draw.rect(screen, BLACK, (150, 220, 200, 60), 2)
        
        pkm_name = font_small.render(player.pokemon[0]["name"], True, BLACK)
        pkm_level = font_small.render(f"Lv. {player.pokemon[0]['level']}", True, BLACK)
        pkm_hp = font_small.render(f"HP: {player.pokemon[0]['hp']}/{player.pokemon[0]['max_hp']}", True, BLACK)
        screen.blit(pkm_name, (160, 230))
        screen.blit(pkm_level, (160, 250))
        screen.blit(pkm_hp, (250, 230))
        
        # Items info
        items_text = font_medium.render("Items", True, BLUE)
        screen.blit(items_text, (450, 180))
        
        pygame.draw.rect(screen, LIGHT_BLUE, (450, 220, 200, 60))
        pygame.draw.rect(screen, BLACK, (450, 220, 200, 60), 2)
        
        potions_text = font_small.render(f"Potions: {player.potions}", True, BLACK)
        screen.blit(potions_text, (460, 240))
        
        # Help text
        help_text = font_small.render("Press M to return to game", True, BLACK)
        screen.blit(help_text, (SCREEN_WIDTH//2 - help_text.get_width()//2, SCREEN_HEIGHT - 120))
    
    # Draw help text in overworld
    if game_state == OVERWORLD:
        help_text = font_small.render("Press M for Menu", True, WHITE)
        screen.blit(help_text, (SCREEN_WIDTH - help_text.get_width() - 10, SCREEN_HEIGHT - 30))
    
    pygame.display.flip()
    clock.tick(60)
