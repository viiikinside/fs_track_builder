import pygame
from tkinter import Tk, filedialog

class ControlPanel:
    def __init__(self, screen, x, width, height, track_canvas):
        self.screen = screen
        self.x = x
        self.width = width
        self.height = height
        self.surface = pygame.Surface((width, height))
        self.background_color = (220, 220, 220)
        self.track_canvas = track_canvas
        
        # Initialize font
        pygame.font.init()
        self.title_font = pygame.font.SysFont('Arial', 20, bold=True)
        self.font = pygame.font.SysFont('Arial', 14)
        
        # Button colors
        self.button_colors = {
            'normal': (150, 150, 150),
            'hover': (130, 130, 130),
            'text': (255, 255, 255),
            'section': (180, 180, 180)
        }
        
        self.straight_length = 100
        self.curve_radius = 50
        
        self.buttons = self.create_buttons()
        self.hovered_button = None
        
        # Remove Tkinter initialization from __init__
        self.tk_root = None
        
        # Load default background
        self.load_default_background()

    def create_buttons(self):
        buttons = {}
        button_height = 30
        button_width = (self.width - 30) // 2
        padding = 10
        current_y = 50

        # Start point button
        buttons['set_start'] = {
            'rect': pygame.Rect(padding, current_y, self.width - 2*padding, button_height),
            'text': 'Set Start Point',
            'color': self.button_colors['normal'],
            'section': 'basic'
        }
        current_y += button_height + 5

        # Length control
        buttons['length_minus'] = {
            'rect': pygame.Rect(padding, current_y, button_height, button_height),
            'text': '-',
            'color': self.button_colors['normal']
        }
        buttons['length_plus'] = {
            'rect': pygame.Rect(self.width - padding - button_height, current_y, button_height, button_height),
            'text': '+',
            'color': self.button_colors['normal']
        }
        current_y += button_height + 5

        # Radius control
        buttons['radius_minus'] = {
            'rect': pygame.Rect(padding, current_y, button_height, button_height),
            'text': '-',
            'color': self.button_colors['normal']
        }
        buttons['radius_plus'] = {
            'rect': pygame.Rect(self.width - padding - button_height, current_y, button_height, button_height),
            'text': '+',
            'color': self.button_colors['normal']
        }
        current_y += button_height + 5

        # Set angle button
        buttons['set_angle'] = {
            'rect': pygame.Rect(padding, current_y, self.width - 2*padding, button_height),
            'text': 'Set Direction',
            'color': self.button_colors['normal'],
            'section': 'basic'
        }
        current_y += button_height + 5

        # Straight segment button
        buttons['add_straight'] = {
            'rect': pygame.Rect(padding, current_y, self.width - 2*padding, button_height),
            'text': 'Add Straight Segment',
            'color': self.button_colors['normal'],
            'section': 'basic'
        }
        current_y += button_height + 5

        # Add load image button
        buttons['load_image'] = {
            'rect': pygame.Rect(padding, current_y, self.width - 2*padding, button_height),
            'text': 'Load Background',
            'color': self.button_colors['normal'],
            'section': 'basic'
        }
        current_y += button_height + 5

        # Add precise angle input button
        buttons['set_precise_angle'] = {
            'rect': pygame.Rect(padding, current_y, self.width - 2*padding, button_height),
            'text': 'Enter Angle',
            'color': self.button_colors['normal'],
            'section': 'basic'
        }
        current_y += button_height + 5

        # Right turn angles
        current_y += 25  # Space for section title
        angles = [15, 30, 45, 60, 75, 90, 120, 135, 150, 180]
        for i, angle in enumerate(angles):
            row = i // 2
            col = i % 2
            x = padding + col * (button_width + padding)
            y = current_y + row * (button_height + 5)
            
            buttons[f'right_{angle}'] = {
                'rect': pygame.Rect(x, y, button_width, button_height),
                'text': f'Right {angle}°',
                'color': self.button_colors['normal'],
                'section': 'right',
                'angle': angle
            }

        # Left turn angles
        current_y += (len(angles)//2 + 1) * (button_height + 5)
        current_y += 25  # Space for section title
        for i, angle in enumerate(angles):
            row = i // 2
            col = i % 2
            x = padding + col * (button_width + padding)
            y = current_y + row * (button_height + 5)
            
            buttons[f'left_{angle}'] = {
                'rect': pygame.Rect(x, y, button_width, button_height),
                'text': f'Left {angle}°',
                'color': self.button_colors['normal'],
                'section': 'left',
                'angle': angle
            }

        # Control buttons at bottom
        current_y = self.height - 2 * (button_height + padding)
        buttons['undo'] = {
            'rect': pygame.Rect(padding, current_y, button_width, button_height),
            'text': 'Undo',
            'color': self.button_colors['normal'],
            'section': 'control'
        }
        buttons['clear_track'] = {
            'rect': pygame.Rect(padding + button_width + padding, current_y, button_width, button_height),
            'text': 'Clear Track',
            'color': self.button_colors['normal'],
            'section': 'control'
        }

        return buttons

    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()
        # Adjust mouse position relative to panel
        relative_pos = (mouse_pos[0] - self.x, mouse_pos[1])
        
        # Handle hover effects
        self.hovered_button = None
        for button_name, button_data in self.buttons.items():
            if button_data['rect'].collidepoint(relative_pos):
                self.hovered_button = button_name
                button_data['color'] = self.button_colors['hover']
            else:
                button_data['color'] = self.button_colors['normal']

        if event.type == pygame.MOUSEBUTTONDOWN:
            for button_name, button_data in self.buttons.items():
                if button_data['rect'].collidepoint(relative_pos):
                    self.handle_button_click(button_name)

    def handle_button_click(self, button_name):
        if button_name == 'set_start':
            self.track_canvas.set_waiting_for_start(True)
        elif button_name == 'set_angle':
            self.track_canvas.start_angle_selection()
        elif button_name == 'length_minus':
            self.straight_length = max(20, self.straight_length - 10)
        elif button_name == 'length_plus':
            self.straight_length = min(300, self.straight_length + 10)
        elif button_name == 'radius_minus':
            self.curve_radius = max(20, self.curve_radius - 5)
        elif button_name == 'radius_plus':
            self.curve_radius = min(150, self.curve_radius + 5)
        elif button_name == 'add_straight':
            self.track_canvas.add_straight_segment(length=self.straight_length)
        elif button_name == 'undo':
            self.track_canvas.undo()
        elif button_name == 'clear_track':
            self.track_canvas.clear_track()
        elif button_name == 'load_image':
            import tkinter as tk
            from tkinter import filedialog
            
            root = tk.Tk()
            root.wm_attributes('-topmost', 1)  # Keep window on top
            root.focus_force()  # Force focus to the dialog
            root.withdraw()
            
            try:
                file_path = filedialog.askopenfilename(
                    master=root,
                    initialdir="track_backgrounds",
                    title="Select Background Image",
                    filetypes=(
                        ("PNG files", "*.png"),
                        ("JPEG files", "*.jpg"),
                        ("All files", "*.*")
                    )
                )
                
                if file_path:
                    self.track_canvas.load_background(file_path)
            except Exception as e:
                print(f"Error loading image: {e}")
            finally:
                root.destroy()
        elif button_name == 'set_precise_angle':
            self.track_canvas.set_angle_input(True)
        elif button_name.startswith('right_'):
            angle = int(button_name.split('_')[1])
            self.track_canvas.add_curve_segment('right', angle=angle, radius=self.curve_radius)
        elif button_name.startswith('left_'):
            angle = int(button_name.split('_')[1])
            self.track_canvas.add_curve_segment('left', angle=angle, radius=self.curve_radius)

    def update(self):
        pass

    def draw(self):
        # Fill background
        self.surface.fill(self.background_color)
        
        # Draw title
        title = self.title_font.render('Track Controls', True, (0, 0, 0))
        title_rect = title.get_rect(centerx=self.width//2, y=15)
        self.surface.blit(title, title_rect)
        
        # Draw section titles
        sections = {
            'right': 'Right Turns',
            'left': 'Left Turns'
        }
        
        current_section = None
        for button_name, button_data in self.buttons.items():
            if 'section' in button_data:
                if button_data['section'] in sections and current_section != button_data['section']:
                    current_section = button_data['section']
                    section_y = button_data['rect'].y - 20
                    section_text = self.font.render(sections[current_section], True, (0, 0, 0))
                    self.surface.blit(section_text, (10, section_y))
        
        # Draw length and radius values
        length_text = self.font.render(f'Length: {self.straight_length}px', True, (0, 0, 0))
        radius_text = self.font.render(f'Radius: {self.curve_radius}px', True, (0, 0, 0))
        
        length_rect = length_text.get_rect(
            centerx=self.width//2, 
            centery=self.buttons['length_minus']['rect'].centery
        )
        radius_rect = radius_text.get_rect(
            centerx=self.width//2, 
            centery=self.buttons['radius_minus']['rect'].centery
        )
        
        self.surface.blit(length_text, length_rect)
        self.surface.blit(radius_text, radius_rect)
        
        # Draw buttons
        for button_data in self.buttons.values():
            # Draw button background
            pygame.draw.rect(self.surface, button_data['color'], button_data['rect'])
            # Draw button border
            pygame.draw.rect(self.surface, (100, 100, 100), button_data['rect'], 1)
            
            # Draw button text
            text = self.font.render(button_data['text'], True, self.button_colors['text'])
            text_rect = text.get_rect(center=button_data['rect'].center)
            self.surface.blit(text, text_rect)

        # Draw panel border
        pygame.draw.rect(self.surface, (200, 200, 200), (0, 0, self.width, self.height), 2)
        
        # If waiting for start point, highlight the set_start button
        if self.track_canvas.waiting_for_start_point:
            self.buttons['set_start']['color'] = (100, 200, 100)  # Green highlight
        elif self.buttons['set_start']['color'] == (100, 200, 100):
            self.buttons['set_start']['color'] = self.button_colors['normal']
        
        # Draw surface to screen
        self.screen.blit(self.surface, (self.x, 0))

    def load_default_background(self):
        default_image = "track_backgrounds/goms_airfield.png"
        try:
            self.track_canvas.load_background(default_image)
        except Exception as e:
            print(f"Error loading default background: {e}")
