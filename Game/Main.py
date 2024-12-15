import pygame
from game_config import SCREEN_WIDTH, SCREEN_HEIGHT, BACKGROUND_COLOR, FPS ,PLAYER_COLOR, SPEED

# Base class for all game states
class GameState:
    def __init__(self, manager):
        self.manager = manager

    def handle_events(self):
        """Handle events specific to this state."""
        pass

    def update(self, dt):
        """Update logic specific to this state."""
        pass

    def render(self, screen):
        """Render the state to the screen."""
        pass


# Gameplay State
class GameplayState(GameState):
    def __init__(self, manager):
        super().__init__(manager)
        self.player_pos = pygame.Vector2(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        self.player_radius = 40
        self.player_color = PLAYER_COLOR
        self.speed = SPEED

    def handle_events(self):
        """Handle gameplay-specific events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.manager.running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.manager.change_state("pause", 0.1)

    def update(self, dt):
        """Update gameplay logic."""
        keys = pygame.key.get_pressed()
        velocity = pygame.Vector2(0, 0)
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            velocity.y -= self.speed * dt
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            velocity.y += self.speed * dt
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            velocity.x -= self.speed * dt
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            velocity.x += self.speed * dt
        
        if keys[pygame.K_F1]:
            self.player_pos = pygame.Vector2(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)

        if velocity.length() > 0:
            velocity = velocity.normalize() * self.speed * dt

        self.player_pos += velocity
        self.player_pos.x = max(self.player_radius, min(self.player_pos.x, SCREEN_WIDTH - self.player_radius))
        self.player_pos.y = max(self.player_radius, min(self.player_pos.y, SCREEN_HEIGHT - self.player_radius))

    def render(self, screen):
        """Render gameplay elements."""
        screen.fill(BACKGROUND_COLOR)
        pygame.draw.circle(screen, self.player_color, self.player_pos, self.player_radius)


# Pause State
class PauseState(GameState):
    def handle_events(self):
        """Handle pause-specific events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.manager.running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.manager.change_state("gameplay",0.1)
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_b:
                self.manager.change_state("menu")

    def render(self, screen):
        """Render pause screen."""
        screen.fill("gray")
        font = pygame.font.Font(None, 74)
        text = font.render("Paused - Press ESC to Resume", True, "white")
        screen.blit(text, (SCREEN_WIDTH // 5.5, SCREEN_HEIGHT // 2.4))
        text = font.render("Press B to go back to menu", True ,"white")
        screen.blit(text, (SCREEN_WIDTH // 5.5, SCREEN_HEIGHT // 1.9))


# Menu State
class MenuState(GameState): 
    def __init__(self, manager):
        super().__init__(manager)
        self.options = ["Start Game", "Options", "Quit"]
        self.current_option = 0

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.manager.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    self.current_option = (self.current_option + 1) % len(self.options)
                elif event.key == pygame.K_UP or event.key == pygame.K_w:
                    self.current_option = (self.current_option - 1) % len(self.options)
                elif event.key == pygame.K_RETURN:
                    if self.current_option == 0:  # Start Game
                        self.manager.change_state("gameplay")
                    elif self.current_option ==1:
                        self.manager.change_state("options", 0.1)
                    elif self.current_option == 2:  # Quit
                        self.manager.running = False

    def render(self, screen):
        screen.fill("blue")
        font = pygame.font.Font(None, 74)
        for i, option in enumerate(self.options):
            color = "white" if i == self.current_option else "gray"
            text = font.render(option, True, color)
            screen.blit(text, (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 3 + i * 100))


# Options State
class OptionsState(GameState):
    def __init__(self, manager):
        super().__init__(manager)
        self.options = ["Volume: 100%", "Fullscreen: OFF", "Back to Menu"]
        self.current_option = 0
        self.volume = 100  # Starting volume
        self.fullscreen = False

    def handle_events(self):
        """Handle input for the options menu."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.manager.running = False

            elif event.type == pygame.KEYDOWN:
                # Navigate options
                if event.key in (pygame.K_DOWN, pygame.K_s):
                    self.current_option = (self.current_option + 1) % len(self.options)
                elif event.key in (pygame.K_UP, pygame.K_w):
                    self.current_option = (self.current_option - 1) % len(self.options)

                # Select option with ENTER
                elif event.key == pygame.K_RETURN:
                    self.select_option()

                # Adjust volume only if the "Volume" option is selected
                elif self.current_option == 0:
                    if event.key in (pygame.K_PLUS, pygame.K_EQUALS, pygame.K_RIGHT, pygame.K_d):
                        self.volume = min(100, self.volume + 10)
                        pygame.mixer.music.set_volume(self.volume / 100)
                        print(f"Volume increased: {self.volume}% | Actual volume: {pygame.mixer.music.get_volume()}")
                        self.options[0] = f"Volume: {self.volume}%"
                    elif event.key in (pygame.K_MINUS, pygame.K_LEFT, pygame.K_a):
                        self.volume = max(0, self.volume - 10)
                        pygame.mixer.music.set_volume(self.volume / 100)
                        print(f"Volume decreased: {self.volume}% | Actual volume: {pygame.mixer.music.get_volume()}")
                        self.options[0] = f"Volume: {self.volume}%"

    def select_option(self):
        """Execute the selected option."""
        if self.current_option == 1:  # Fullscreen toggle
            self.fullscreen = not self.fullscreen
            if self.fullscreen:
                pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
                self.options[1] = "Fullscreen: ON"
                print("Fullscreen: ON")
            else:
                pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
                self.options[1] = "Fullscreen: OFF"
                print("Fullscreen: OFF")
                
        elif self.current_option == 2:  # Back to menu
            self.manager.change_state("menu", fade_duration=0.5)

    def render(self, screen):
        """Render the options menu."""
        screen.fill("purple")
        font = pygame.font.Font(None, 74)
        for i, option in enumerate(self.options):
            color = "white" if i == self.current_option else "gray"
            text = font.render(option, True, color)
            screen.blit(text, (SCREEN_WIDTH // 5, SCREEN_HEIGHT // 3 + i * 100))


# Game Manager
class GameManager:
    def __init__(self):
        # Setting up pygame
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("State Management Example")
        self.clock = pygame.time.Clock()
        self.running = True
        self.dt = 0
        
        # Initialize background music
        pygame.mixer.init()
        try:
            background_music = pygame.mixer.Sound("Assets/Music/pokemonBackgroundMusic.mp3")
            background_music.play(loops =-1)
        except pygame.error as e:
            print(f"Error loading background music: {e}")
            
        # Making starting fade
        self.fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.fade_surface.fill("black")
        self.fade_alpha = 0

        # Initialize states
        self.states = {
            "gameplay": GameplayState(self),
            "pause": PauseState(self),
            "menu" : MenuState(self),
            "options" : OptionsState(self)
        }
        
        self.current_state = self.states["menu"]

    def fade_to_black(self, duration):
        """perform a fade-to-black transition"""
        fade_time = 0
        while fade_time< duration:
            fade_time += self.clock.tick(FPS) /1000
            self.fade_alpha = min(255, int(255*(fade_time/ duration)))
            self.fade_surface.set_alpha(self.fade_alpha)
            self.current_state.render(self.screen)
            self.screen.blit(self.fade_surface, (0,0)) #Fade overlay
            pygame.display.flip()


    def change_state(self, state_name, fade_duration =0.7):
        """Switch to a different game state."""
        self.fade_to_black(fade_duration)
        
        if isinstance(self.current_state, PauseState) and state_name == "menu":
            gameplay_state = self.states["gameplay"]
            gameplay_state.player_pos = pygame.Vector2(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        
        self.current_state = self.states[state_name]

    def run(self):
        """Main game loop."""
        while self.running:
            self.dt = self.clock.tick(FPS) / 1000
            self.current_state.handle_events()
            self.current_state.update(self.dt)
            self.current_state.render(self.screen)
            pygame.display.flip()
        pygame.quit()


if __name__ == "__main__":
    game = GameManager()
    game.run()