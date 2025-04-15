from typing import Optional, Tuple, List, Dict, Union, Any
import pygame
from models.track_element import TrackElement
import numpy as np
import math

class TrackCanvas:
    def __init__(self, screen: pygame.Surface, width: int, height: int) -> None:
        self.screen = screen
        self.width = width
        self.height = height
        self.surface = pygame.Surface((width, height))
        # Add a subtle grid or border to make it visible
        self.border_color = (200, 200, 200)
        self.track_elements = []
        self.undo_stack = []  # Stack for undo functionality
        
        # Track drawing properties
        self.current_pos = (width // 2, height // 2)  # Start from center
        self.track_color = (50, 50, 50)  # Dark gray for the track
        self.track_width = 5  # Reduced from 10 to 5 pixels
        self.current_direction = -90  # Start pointing upward (in degrees)
        self.waiting_for_start_point = False
        self.start_direction = -90  # Default direction (upward)
        self.waiting_for_angle = False
        self.temp_start_pos = None
        self.temp_angle_line = None
        self.background_image = None
        self.background_rect = None
        self.angle_input_active = False
        self.current_angle_str = ""
        self.font = pygame.font.SysFont('Arial', 16)
        self.angle_input_rect = pygame.Rect(10, 10, 100, 30)

    def add_straight_segment(self, length: float = 100) -> None:
        start_pos = self.current_pos
        # Calculate end position based on current direction
        rad = math.radians(self.current_direction)
        dx = length * math.cos(rad)
        dy = length * math.sin(rad)
        end_pos = (start_pos[0] + dx, start_pos[1] + dy)
        
        new_element = {
            'type': 'straight',
            'start': start_pos,
            'end': end_pos,
        }
        self.track_elements.append(new_element)
        self.undo_stack.append(('add', new_element))
        self.current_pos = end_pos

    def add_curve_segment(self, direction: str = 'right', angle: float = 180, radius: float = 50) -> None:
        start_pos = self.current_pos
        start_angle = self.current_direction
        
        # Convert angles to radians for calculations
        start_rad = math.radians(start_angle)
        turn_rad = math.radians(angle)
        
        if direction == 'right':
            center = (
                start_pos[0] - radius * math.sin(start_rad),
                start_pos[1] + radius * math.cos(start_rad)
            )
            start_angle_draw = start_angle
            end_angle_draw = start_angle + angle
            end_angle = start_angle + angle
            
            # Calculate end position based on angle
            end_pos = (
                center[0] + radius * math.sin(start_rad + turn_rad),
                center[1] - radius * math.cos(start_rad + turn_rad)
            )
        else:  # left
            center = (
                start_pos[0] + radius * math.sin(start_rad),
                start_pos[1] - radius * math.cos(start_rad)
            )
            start_angle_draw = start_angle + 180
            end_angle_draw = start_angle + (180 - angle)
            end_angle = start_angle + angle
            
            # Calculate end position based on angle
            end_pos = (
                center[0] - radius * math.sin(start_rad + turn_rad),
                center[1] + radius * math.cos(start_rad + turn_rad)
            )
        
        new_element = {
            'type': 'curve',
            'start': start_pos,
            'center': center,
            'radius': radius,
            'start_angle': start_angle_draw,
            'end_angle': end_angle_draw,
            'direction': direction
        }
        
        self.track_elements.append(new_element)
        self.undo_stack.append(('add', new_element))
        self.current_pos = end_pos
        self.current_direction = end_angle

    def undo(self) -> None:
        if self.undo_stack:
            action, element = self.undo_stack.pop()
            if action == 'add':
                self.track_elements.pop()
                # Reset position to previous element's end or center if no elements left
                if self.track_elements:
                    last_element = self.track_elements[-1]
                    if last_element['type'] == 'straight':
                        self.current_pos = last_element['end']
                        dx = last_element['end'][0] - last_element['start'][0]
                        dy = last_element['end'][1] - last_element['start'][1]
                        self.current_direction = math.degrees(math.atan2(dy, dx))
                    else:  # curve
                        self.current_pos = last_element['end']
                        self.current_direction = last_element['end_angle']
                else:
                    self.current_pos = (self.width // 2, self.height // 2)
                    self.current_direction = -90

    def clear_track(self) -> None:
        self.track_elements = []
        self.undo_stack = []
        self.current_pos = (self.width // 2, self.height // 2)
        self.current_direction = -90

    def set_waiting_for_start(self, waiting: bool) -> None:
        self.waiting_for_start_point = waiting
        self.waiting_for_angle = False
        self.temp_start_pos = None
        if waiting:
            self.clear_track()

    def start_angle_selection(self) -> None:
        self.waiting_for_angle = True
        self.temp_start_pos = self.current_pos

    def load_background(self, image_path: str) -> bool:
        try:
            # Load and scale the image to fit the canvas
            original_image = pygame.image.load(image_path)
            self.background_image = pygame.transform.scale(original_image, (self.width, self.height))
            self.background_rect = self.background_image.get_rect()
            return True
        except Exception as e:
            print(f"Error loading background image: {e}")
            return False

    def set_angle_input(self, active: bool) -> None:
        self.angle_input_active = active
        if active:
            self.current_angle_str = str(int(self.current_direction))
        else:
            try:
                if self.current_angle_str:
                    new_angle = float(self.current_angle_str)
                    self.current_direction = new_angle
            except ValueError:
                pass
            self.current_angle_str = ""

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN:
            # If clicking outside angle input box, deactivate it
            if self.angle_input_active and not self.angle_input_rect.collidepoint(event.pos):
                self.set_angle_input(False)
                return

            canvas_pos = (event.pos[0], event.pos[1])
            if self.surface.get_rect().collidepoint(canvas_pos):
                if self.waiting_for_start_point:
                    self.current_pos = canvas_pos
                    self.current_direction = self.start_direction
                    self.waiting_for_start_point = False
                elif self.waiting_for_angle:
                    dx = canvas_pos[0] - self.current_pos[0]
                    dy = canvas_pos[1] - self.current_pos[1]
                    self.current_direction = math.degrees(math.atan2(dy, dx))
                    self.waiting_for_angle = False
                    self.temp_start_pos = None

        elif event.type == pygame.KEYDOWN and self.angle_input_active:
            if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                self.set_angle_input(False)
            elif event.key == pygame.K_ESCAPE:
                self.angle_input_active = False
                self.current_angle_str = ""
            elif event.key == pygame.K_BACKSPACE:
                self.current_angle_str = self.current_angle_str[:-1]
            elif len(self.current_angle_str) < 6:  # Limit input length
                if event.unicode.isnumeric() or event.unicode in '.-':
                    self.current_angle_str += event.unicode

        elif event.type == pygame.MOUSEMOTION and self.waiting_for_angle:
            # Update temporary angle line
            self.temp_angle_line = (self.current_pos, event.pos)

    def update(self) -> None:
        pass

    def draw(self) -> None:
        # Draw background image if available, otherwise fill with white
        if self.background_image:
            self.surface.blit(self.background_image, (0, 0))
        else:
            self.surface.fill((255, 255, 255))
        
        # Draw grid lines with semi-transparent overlay
        grid_color = (230, 230, 230, 128)  # Added alpha for transparency
        grid_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        for x in range(0, self.width, 50):
            pygame.draw.line(grid_surface, grid_color, 
                           (x, 0), 
                           (x, self.height))
        
        for y in range(0, self.height, 50):
            pygame.draw.line(grid_surface, grid_color, 
                           (0, y), 
                           (self.width, y))
        
        self.surface.blit(grid_surface, (0, 0))

        # Draw track elements
        for element in self.track_elements:
            if element['type'] == 'straight':
                pygame.draw.line(self.surface, self.track_color,
                               element['start'], element['end'],
                               self.track_width)
            elif element['type'] == 'curve':
                rect = pygame.Rect(
                    element['center'][0] - element['radius'],
                    element['center'][1] - element['radius'],
                    element['radius'] * 2,
                    element['radius'] * 2
                )
                start_angle = math.radians(element['start_angle'])
                end_angle = math.radians(element['end_angle'])
                pygame.draw.arc(self.surface, self.track_color,
                              rect, start_angle, end_angle,
                              self.track_width)

        # Draw border
        pygame.draw.rect(self.surface, self.border_color, (0, 0, self.width, self.height), 2)
        
        # If waiting for start point, draw a cursor
        if self.waiting_for_start_point:
            mouse_pos = pygame.mouse.get_pos()
            if self.surface.get_rect().collidepoint(mouse_pos):
                # Draw crosshair cursor
                cursor_size = 10
                pygame.draw.line(self.surface, (255, 0, 0),
                               (mouse_pos[0] - cursor_size, mouse_pos[1]),
                               (mouse_pos[0] + cursor_size, mouse_pos[1]), 2)
                pygame.draw.line(self.surface, (255, 0, 0),
                               (mouse_pos[0], mouse_pos[1] - cursor_size),
                               (mouse_pos[0], mouse_pos[1] + cursor_size), 2)
                
                # Draw direction indicator
                direction_rad = math.radians(self.start_direction)
                end_x = mouse_pos[0] + cursor_size * 2 * math.cos(direction_rad)
                end_y = mouse_pos[1] + cursor_size * 2 * math.sin(direction_rad)
                pygame.draw.line(self.surface, (0, 255, 0),
                               mouse_pos,
                               (end_x, end_y), 2)

        # Draw temporary angle line
        if self.waiting_for_angle and self.temp_angle_line:
            pygame.draw.line(self.surface, (0, 255, 0),
                           self.temp_angle_line[0],
                           self.temp_angle_line[1], 2)

        # Draw angle input if active
        if self.angle_input_active:
            pygame.draw.rect(self.surface, (255, 255, 255), self.angle_input_rect)
            pygame.draw.rect(self.surface, (0, 0, 0), self.angle_input_rect, 1)
            text = self.font.render(self.current_angle_str + "°", True, (0, 0, 0))
            text_rect = text.get_rect(midleft=(self.angle_input_rect.x + 5, self.angle_input_rect.centery))
            self.surface.blit(text, text_rect)

        # Draw surface to screen
        self.screen.blit(self.surface, (0, 0))

    def get_track_points(self) -> Optional[np.ndarray]:
        if not self.track_elements:
            return None
            
        points = []
        for element in self.track_elements:
            if element['type'] == 'straight':
                points.append(element['start'])
                points.append(element['end'])
            elif element['type'] == 'curve':
                # For curves, generate points along the arc
                center = element['center']
                radius = element['radius']
                start_angle = element['start_angle']
                end_angle = element['end_angle']
                
                # Generate points along the curve
                num_points = 20  # Number of points to generate along the curve
                angles = np.linspace(start_angle, end_angle, num_points)
                for angle in angles:
                    x = center[0] + radius * np.cos(np.radians(angle))
                    y = center[1] + radius * np.sin(np.radians(angle))
                    points.append((x, y))
                
        return np.array(points)
