import pygame
from src.gui.track_canvas import TrackCanvas
from src.gui.control_panel import ControlPanel

class MainWindow:
    def __init__(self):
        pygame.init()
        self.width = 1200
        self.height = 800
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Formula Student Track Builder")
        
        self.track_canvas = TrackCanvas(self.screen)
        self.control_panel = ControlPanel(self.screen)
        
        self.running = True

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            self.track_canvas.handle_event(event)
            self.control_panel.handle_event(event)

    def update(self):
        self.track_canvas.update()
        self.control_panel.update()

    def draw(self):
        self.screen.fill((255, 255, 255))  # White background
        self.track_canvas.draw()
        self.control_panel.draw()
        pygame.display.flip()
