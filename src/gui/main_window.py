import pygame
import numpy as np
import os
from datetime import datetime
import gpxpy
import gpxpy.gpx
from src.gui.track_canvas import TrackCanvas
from src.gui.control_panel import ControlPanel
import math
from typing import Optional
from src.gui.description_dialog import DescriptionDialog
from src.data_generation.track_generator import TrackDataGenerator
import tkinter as tk

class MainWindow:
    def __init__(self) -> None:
        pygame.init()
        self.width = 1600  # Increased from 1200
        self.height = 1000  # Increased from 800
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Formula Student Track Builder")
        
        # Define background color (light gray)
        self.background_color = (240, 240, 240)
        
        # Calculate dimensions for track canvas and control panel
        canvas_width = int(self.width * 0.8)  # Keep original 80% ratio
        control_panel_width = self.width - canvas_width  # 20% of window width
        
        # Create track canvas first
        self.track_canvas = TrackCanvas(self.screen, width=canvas_width, height=self.height)
        
        # Pass track_canvas and self to control panel
        self.control_panel = ControlPanel(
            self.screen,
            x=canvas_width,
            width=control_panel_width,
            height=self.height,
            track_canvas=self.track_canvas,
            main_window=self
        )
        
        self.running = True
        
        # Create output directories if they don't exist
        self.output_dir = "output"
        self.images_dir = os.path.join(self.output_dir, "images")
        self.tracks_dir = os.path.join(self.output_dir, "tracks")
        os.makedirs(self.images_dir, exist_ok=True)
        os.makedirs(self.tracks_dir, exist_ok=True)
        
        self.track_generator = TrackDataGenerator()

    def run(self) -> None:
        clock = pygame.time.Clock()
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            clock.tick(60)  # Limit to 60 FPS
            
    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.save_track_data()  # Save before closing
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.save_track_data()  # Save before closing
                    self.running = False
            self.track_canvas.handle_event(event)
            self.control_panel.handle_event(event)

    def update(self) -> None:
        self.track_canvas.update()
        self.control_panel.update()

    def draw(self) -> None:
        self.screen.fill(self.background_color)  # Light gray background
        self.track_canvas.draw()
        self.control_panel.draw()
        pygame.display.flip()

    def save_track_data(self) -> None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save as PNG image
        image_path = os.path.join(self.images_dir, f"track_{timestamp}.png")
        pygame.image.save(self.screen, image_path)
        
        # Save track coordinates as numpy array
        track_points = self.track_canvas.get_track_points()
        if track_points is not None and len(track_points) > 0:
            np_path = os.path.join(self.tracks_dir, f"track_{timestamp}.npy")
            np.save(np_path, track_points)
            
            # Save as GPX
            gpx_path = os.path.join(self.tracks_dir, f"track_{timestamp}.gpx")
            self.save_as_gpx(track_points, gpx_path)
            
            print(f"Track saved to:\n"
                  f"- Image: {image_path}\n"
                  f"- Numpy: {np_path}\n"
                  f"- GPX: {gpx_path}")
        else:
            print(f"Track saved to:\n- Image: {image_path}")

    def save_as_gpx(self, track_points: np.ndarray, gpx_path: str) -> None:
        gpx = gpxpy.gpx.GPX()
        gpx_track = gpxpy.gpx.GPXTrack()
        gpx.tracks.append(gpx_track)
        gpx_segment = gpxpy.gpx.GPXTrackSegment()
        gpx_track.segments.append(gpx_segment)
        
        # Convert track points to GPS coordinates (simplified example)
        # This assumes the track is centered around (0,0) latitude/longitude
        scale = 0.0001  # Scale factor to convert pixels to GPS coordinates
        for point in track_points:
            lat = point[1] * scale
            lon = point[0] * scale
            gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(lat, lon))
            
        with open(gpx_path, 'w') as f:
            f.write(gpx.to_xml())

    def add_curve_segment(self, direction='right', radius=50):
        start_pos = self.current_pos
        start_angle = self.current_direction
        
        # Convert angles to radians for calculations
        start_rad = math.radians(start_angle)
        
        if direction == 'right':
            # For right turns, center is radius units perpendicular to current direction
            center = (
                start_pos[0] - radius * math.sin(start_rad),
                start_pos[1] + radius * math.cos(start_rad)
            )
            # For right turns, we go clockwise
            start_angle_draw = start_angle
            end_angle_draw = start_angle + 180
            end_angle = start_angle + 180
            
            # Calculate end position for right turn
            end_pos = (
                center[0] + radius * math.sin(start_rad + math.pi),
                center[1] - radius * math.cos(start_rad + math.pi)
            )
        else:  # left
            # For left turns, center is radius units perpendicular in opposite direction
            center = (
                start_pos[0] + radius * math.sin(start_rad),
                start_pos[1] - radius * math.cos(start_rad)
            )
            # For left turns, we go counter-clockwise
            start_angle_draw = start_angle + 180
            end_angle_draw = start_angle
            end_angle = start_angle + 180
            
            # Calculate end position for left turn
            end_pos = (
                center[0] - radius * math.sin(start_rad + math.pi),
                center[1] + radius * math.cos(start_rad + math.pi)
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

    def save_training_example(self):
        """Save current track as a training example"""
        if not self.track_canvas.track_elements:
            print("No track to save!")
            return
            
        try:
            # Initialize Tkinter root properly
            root = tk.Tk()
            root.withdraw()  # Hide the main window
            
            # Create and configure dialog
            dialog = DescriptionDialog(root)
            
            # Update the dialog to ensure it's shown
            dialog.dialog.update()
            
            # Run the dialog in the main thread
            root.mainloop()
            
            # After dialog closes, check if description was provided
            if dialog.description:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                
                # Get track parameters
                track_params = {
                    'timestamp': timestamp,
                    'segments': [
                        {k: float(v) if isinstance(v, (int, float)) else v 
                         for k, v in segment.items()}
                        for segment in self.track_canvas.track_elements
                    ],
                    'background_image': self.track_canvas.background_image_path 
                        if hasattr(self.track_canvas, 'background_image_path') else None
                }
                
                # Save training example
                self.track_generator.save_training_example(
                    track_params,
                    self.screen,
                    dialog.description
                )
                print("Training example saved successfully!")
            
        except Exception as e:
            print(f"Error saving training example: {e}")
            import traceback
            traceback.print_exc()
        finally:
            if 'root' in locals():
                root.destroy()
            
            # Force Pygame to regain focus
            pygame.event.post(pygame.event.Event(pygame.ACTIVEEVENT, 
                                               gain=1, 
                                               state=pygame.APPACTIVE))
