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
        self.track_color = (50, 50, 50)  # Center line color (black)
        self.left_lane_color = (50, 50, 255)  # Blue
        self.right_lane_color = (255, 255, 0)  # Yellow
        self.track_width = 1  # Center line width in pixels (reduced from 2)
        self.lane_width = 1  # Side lane width in pixels
        self.track_total_width = 0.75  # Track width in meters (reduced from 1.5)
        self.pixels_per_meter = 8  # Scale factor (reduced from 10)
        self.lane_offset = (self.track_total_width / 2) * self.pixels_per_meter  # Distance from center to each lane
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
        
        # Add zoom related attributes
        self.zoom_level = 1.0
        self.min_zoom = 0.2
        self.max_zoom = 5.0
        self.zoom_speed = 0.1
        self.pan_start = None
        self.offset = [0, 0]  # [x, y] offset for panning

        # Add description text box
        self.description_font = pygame.font.SysFont('Arial', 14)
        self.description = ""
        self.description_active = False
        self.description_rect = pygame.Rect(10, self.height - 100, self.width - 20, 80)

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
        # Always start from current position
        start_pos = self.current_pos
        start_angle = self.current_direction
        
        print(f"Starting curve at pos: {start_pos}, angle: {start_angle}")
        
        # Convert angles to radians for calculations
        start_rad = math.radians(start_angle)
        
        if direction == 'right':
            # Calculate center point from current position
            center = (
                start_pos[0] - radius * math.sin(start_rad),  # Move right perpendicular to direction
                start_pos[1] + radius * math.cos(start_rad)   # Move right perpendicular to direction
            )
            
            # Keep the angle calculations (they work correctly)
            start_angle_draw = (math.pi/2 + start_rad)
            end_angle_draw = start_angle_draw + math.radians(angle)
            end_angle = (start_angle - angle) % 360
            
        else:  # left
            # Calculate center point from current position
            center = (
                start_pos[0] + radius * math.sin(start_rad),  # Move left perpendicular to direction
                start_pos[1] - radius * math.cos(start_rad)   # Move left perpendicular to direction
            )
            
            # Keep the angle calculations (they work correctly)
            start_angle_draw = (math.pi/2 + start_rad + math.pi)
            end_angle_draw = start_angle_draw + math.radians(angle)
            end_angle = (start_angle + angle) % 360
        
        # Calculate end position using the center point
        end_rad = math.radians(end_angle)
        if direction == 'right':
            end_pos = (
                center[0] + radius * math.sin(end_rad),
                center[1] - radius * math.cos(end_rad)
            )
        else:
            end_pos = (
                center[0] - radius * math.sin(end_rad),
                center[1] + radius * math.cos(end_rad)
            )
        
        print(f"Curve ends at pos: {end_pos}, angle: {end_angle}")
        
        # Store the curve element
        new_element = {
            'type': 'curve',
            'start': start_pos,  # Use exact current position
            'center': center,
            'radius': radius,
            'start_angle': start_angle_draw,
            'end_angle': end_angle_draw,
            'direction': direction
        }
        
        # Update track state
        self.track_elements.append(new_element)
        self.undo_stack.append(('add', new_element))
        self.current_pos = end_pos  # Update position for next segment
        self.current_direction = end_angle  # Update direction for next segment

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
            self.background_image_path = image_path  # Store the path
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
        # Handle zooming with mouse wheel
        if event.type == pygame.MOUSEWHEEL:
            if self.surface.get_rect().collidepoint(pygame.mouse.get_pos()):
                mouse_x, mouse_y = pygame.mouse.get_pos()
                self.zoom(event.y, mouse_x, mouse_y)
        
        # Handle panning with middle mouse button
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 2:  # Middle mouse button
            self.pan_start = pygame.mouse.get_pos()
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 2:
            self.pan_start = None
        elif event.type == pygame.MOUSEMOTION and self.pan_start is not None:
            current_pos = pygame.mouse.get_pos()
            dx = current_pos[0] - self.pan_start[0]
            dy = current_pos[1] - self.pan_start[1]
            self.offset[0] += dx
            self.offset[1] += dy
            self.pan_start = current_pos

        if event.type == pygame.MOUSEBUTTONDOWN:
            # If clicking outside angle input box, deactivate it
            if self.angle_input_active and not self.angle_input_rect.collidepoint(event.pos):
                self.set_angle_input(False)
                return

            # Convert screen coordinates to world coordinates for clicking
            screen_pos = event.pos
            world_pos = self.screen_to_world(screen_pos)
            
            if self.surface.get_rect().collidepoint(screen_pos):
                if self.waiting_for_start_point:
                    self.current_pos = world_pos
                    self.current_direction = self.start_direction
                    self.waiting_for_start_point = False
                elif self.waiting_for_angle:
                    dx = world_pos[0] - self.current_pos[0]
                    dy = world_pos[1] - self.current_pos[1]
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

        # Handle description text input
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.description_rect.collidepoint(event.pos):
                self.description_active = True
            else:
                self.description_active = False

        if event.type == pygame.KEYDOWN and self.description_active:
            if event.key == pygame.K_BACKSPACE:
                self.description = self.description[:-1]
            elif event.key == pygame.K_RETURN:
                self.description_active = False
            else:
                self.description += event.unicode

    def update(self) -> None:
        pass

    def draw_parallel_line(self, start: Tuple[float, float], end: Tuple[float, float], 
                         offset: float, color: Tuple[int, int, int], width: int) -> None:
        """Draw a line parallel to the given line at specified offset"""
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        length = math.sqrt(dx*dx + dy*dy)
        if length == 0:
            return
        
        # Calculate offset vector (perpendicular to line)
        offset_x = -dy * offset / length
        offset_y = dx * offset / length
        
        # Calculate parallel line points
        start_parallel = (start[0] + offset_x, start[1] + offset_y)
        end_parallel = (end[0] + offset_x, end[1] + offset_y)
        
        # Draw the parallel line
        pygame.draw.line(self.surface, color, start_parallel, end_parallel, width)

    def draw_parallel_arc(self, center: Tuple[float, float], radius: float, 
                         start_angle: float, end_angle: float, offset: float,
                         color: Tuple[int, int, int], width: int, direction: str) -> None:
        """Draw an arc parallel to the given arc at specified offset"""
        # Adjust radius based on offset and direction
        if direction == 'right':
            new_radius = radius + offset if offset > 0 else radius - abs(offset)
        else:
            new_radius = radius - offset if offset > 0 else radius + abs(offset)
        
        rect = pygame.Rect(
            center[0] - new_radius,
            center[1] - new_radius,
            new_radius * 2,
            new_radius * 2
        )
        pygame.draw.arc(self.surface, color, rect, start_angle, end_angle, width)

    def draw_dotted_line(self, surface: pygame.Surface, color: Tuple[int, int, int],
                        start_pos: Tuple[float, float], end_pos: Tuple[float, float],
                        width: int = 1, dash_length: int = 5) -> None:
        """Draw a dotted line between two points"""
        dx = end_pos[0] - start_pos[0]
        dy = end_pos[1] - start_pos[1]
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance <= 0:
            return
            
        dash_count = int(distance / (2 * dash_length))
        
        unit_x = dx / distance
        unit_y = dy / distance
        
        for i in range(dash_count):
            start_x = start_pos[0] + (2 * i * dash_length) * unit_x
            start_y = start_pos[1] + (2 * i * dash_length) * unit_y
            end_x = start_x + dash_length * unit_x
            end_y = start_y + dash_length * unit_y
            
            pygame.draw.line(surface, color, (start_x, start_y), (end_x, end_y), width)

    def draw(self) -> None:
        # Draw background image if available, otherwise fill with white
        if self.background_image:
            scaled_image = pygame.transform.scale(
                self.background_image,
                (int(self.width * self.zoom_level), int(self.height * self.zoom_level))
            )
            self.surface.blit(scaled_image, self.offset)
        else:
            self.surface.fill((255, 255, 255))
        
        # Draw grid with zoom
        grid_size = 50 * self.zoom_level
        grid_color = (230, 230, 230, 128)
        grid_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Calculate grid lines with offset
        start_x = self.offset[0] % grid_size
        start_y = self.offset[1] % grid_size
        
        for x in range(int(start_x - grid_size), self.width, int(grid_size)):
            pygame.draw.line(grid_surface, grid_color, (x, 0), (x, self.height))
        
        for y in range(int(start_y - grid_size), self.height, int(grid_size)):
            pygame.draw.line(grid_surface, grid_color, (0, y), (self.width, y))
        
        self.surface.blit(grid_surface, (0, 0))

        # Draw track elements with parallel lanes
        for element in self.track_elements:
            if element['type'] == 'straight':
                start = self.world_to_screen(element['start'])
                end = self.world_to_screen(element['end'])
                
                # Draw center dotted line
                self.draw_dotted_line(self.surface, self.track_color,
                                    start, end,
                                    max(1, int(self.track_width * self.zoom_level)),
                                    dash_length=max(3, int(5 * self.zoom_level)))
                
                # Draw parallel lanes
                offset = self.lane_offset * self.zoom_level
                self.draw_parallel_line(start, end, offset, self.right_lane_color,
                                     max(1, int(self.lane_width * self.zoom_level)))
                self.draw_parallel_line(start, end, -offset, self.left_lane_color,
                                     max(1, int(self.lane_width * self.zoom_level)))
                
            elif element['type'] == 'curve':
                center = self.world_to_screen(element['center'])
                radius = element['radius'] * self.zoom_level
                
                # Draw center dotted arc
                rect = pygame.Rect(
                    center[0] - radius,
                    center[1] - radius,
                    radius * 2,
                    radius * 2
                )
                
                # For dotted arc, we'll draw small lines along the arc path
                start_angle = element['start_angle']
                end_angle = element['end_angle']
                angle_range = np.linspace(start_angle, end_angle, 20)  # Adjust number for density
                for i in range(0, len(angle_range)-1, 2):
                    a1 = angle_range[i]
                    a2 = min(angle_range[i+1], end_angle)
                    pygame.draw.arc(self.surface, self.track_color,
                                  rect, a1, a2,
                                  max(1, int(self.track_width * self.zoom_level)))
                
                # Draw parallel lanes
                offset = self.lane_offset * self.zoom_level
                self.draw_parallel_arc(center, radius, start_angle, end_angle,
                                    offset, self.right_lane_color,
                                    max(1, int(self.lane_width * self.zoom_level)),
                                    element['direction'])
                self.draw_parallel_arc(center, radius, start_angle, end_angle,
                                    -offset, self.left_lane_color,
                                    max(1, int(self.lane_width * self.zoom_level)),
                                    element['direction'])

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

        # Draw description text box
        pygame.draw.rect(self.surface, (255, 255, 255), self.description_rect)
        pygame.draw.rect(self.surface, (100, 100, 100), self.description_rect, 1)
        
        # Draw description text or placeholder
        if self.description:
            text = self.description_font.render(self.description, True, (0, 0, 0))
        else:
            text = self.description_font.render("Click here to enter track description...", True, (150, 150, 150))
        
        self.surface.blit(text, (self.description_rect.x + 5, self.description_rect.y + 5))

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

    def zoom(self, direction: int, mouse_x: int, mouse_y: int) -> None:
        """Handle zooming centered on mouse position"""
        old_zoom = self.zoom_level
        
        # Update zoom level
        if direction > 0:
            self.zoom_level = min(self.zoom_level + self.zoom_speed, self.max_zoom)
        else:
            self.zoom_level = max(self.zoom_level - self.zoom_speed, self.min_zoom)
            
        # Adjust offset to zoom towards mouse position
        zoom_factor = self.zoom_level / old_zoom
        self.offset[0] = mouse_x - (mouse_x - self.offset[0]) * zoom_factor
        self.offset[1] = mouse_y - (mouse_y - self.offset[1]) * zoom_factor

    def world_to_screen(self, pos: Tuple[float, float]) -> Tuple[float, float]:
        """Convert world coordinates to screen coordinates"""
        x = pos[0] * self.zoom_level + self.offset[0]
        y = pos[1] * self.zoom_level + self.offset[1]
        return (x, y)

    def screen_to_world(self, pos: Tuple[float, float]) -> Tuple[float, float]:
        """Convert screen coordinates to world coordinates"""
        x = (pos[0] - self.offset[0]) / self.zoom_level
        y = (pos[1] - self.offset[1]) / self.zoom_level
        return (x, y)
