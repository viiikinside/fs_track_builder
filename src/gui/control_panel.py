import pygame

class ControlPanel:
    def __init__(self, screen):
        self.screen = screen
        self.panel_rect = pygame.Rect(0, 0, 200, 800)  # Left side panel
        self.buttons = self.create_buttons()

    def create_buttons(self):
        buttons = {
            'add_straight': pygame.Rect(20, 50, 160, 40),
            'add_curve': pygame.Rect(20, 100, 160, 40)
        }
        return buttons

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            for button_name, button_rect in self.buttons.items():
                if button_rect.collidepoint(event.pos):
                    self.handle_button_click(button_name)

    def handle_button_click(self, button_name):
        if button_name == 'add_straight':
            print("Adding straight segment")
        elif button_name == 'add_curve':
            print("Adding curve segment")

    def update(self):
        pass

    def draw(self):
        # Draw panel background
        pygame.draw.rect(self.screen, (200, 200, 200), self.panel_rect)
        
        # Draw buttons
        for button_rect in self.buttons.values():
            pygame.draw.rect(self.screen, (150, 150, 150), button_rect)
