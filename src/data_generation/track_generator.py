from typing import Dict, List, Tuple, Optional
import numpy as np
import json
import os
from datetime import datetime
import pygame
from src.gui.track_canvas import TrackCanvas
import math

class TrackDataGenerator:
    def __init__(self, output_dir: str = "data"):
        self.output_dir = output_dir
        self.raw_tracks_dir = os.path.join(output_dir, "raw_tracks")
        self.descriptions_dir = os.path.join(output_dir, "descriptions")
        self.processed_dir = os.path.join(output_dir, "processed")
        
        # Create directories if they don't exist
        os.makedirs(self.raw_tracks_dir, exist_ok=True)
        os.makedirs(self.descriptions_dir, exist_ok=True)
        os.makedirs(self.processed_dir, exist_ok=True)

        # Track generation parameters
        self.min_segments = 3
        self.max_segments = 10
        self.possible_angles = [15, 30, 45, 60, 75, 90, 120, 135, 150, 180]
        self.min_straight_length = 20
        self.max_straight_length = 300
        self.min_radius = 20
        self.max_radius = 150

        # Initialize pygame and surfaces for track generation
        pygame.init()
        self.width = 1200
        self.height = 800
        self.screen = pygame.Surface((self.width, self.height))
        self.track_canvas = TrackCanvas(self.screen, self.width, self.height)

    def generate_track_params(self) -> Dict:
        """Generate random track parameters"""
        # Start with fewer segments for testing
        num_segments = int(np.random.randint(3, 6))  # Reduced from (3, 10)
        segments = []
        
        for _ in range(num_segments):
            if np.random.random() < 0.4:  # 40% chance of straight
                segment = {
                    'type': 'straight',
                    'length': int(np.random.randint(50, 150))  # Reduced length range
                }
            else:  # curve
                segment = {
                    'type': 'curve',
                    'direction': str(np.random.choice(['left', 'right'])),
                    'angle': int(np.random.choice([45, 90])),  # Simplified angles
                    'radius': int(np.random.randint(30, 70))  # Reduced radius range
                }
            segments.append(segment)
            
        return {
            'num_segments': num_segments,
            'segments': segments,
            'timestamp': datetime.now().strftime("%Y%m%d_%H%M%S")
        }

    def generate_description(self, track_params: Dict) -> str:
        """Generate natural language description of the track"""
        segments = track_params['segments']
        description_parts = []
        
        # Count segment types
        num_straights = sum(1 for s in segments if s['type'] == 'straight')
        num_curves = len(segments) - num_straights
        
        # Overall description
        description_parts.append(f"A track with {len(segments)} segments, "
                              f"featuring {num_straights} straight sections and "
                              f"{num_curves} turns.")
        
        # Detailed segment description
        for i, segment in enumerate(segments, 1):
            if segment['type'] == 'straight':
                length_desc = "short" if segment['length'] < 100 else "long"
                description_parts.append(f"Segment {i} is a {length_desc} straight "
                                      f"of {segment['length']} meters.")
            else:
                tightness = "tight" if segment['radius'] < 50 else "wide"
                description_parts.append(f"Segment {i} is a {tightness} {segment['direction']} "
                                      f"turn of {segment['angle']} degrees.")
        
        return " ".join(description_parts)

    def save_training_example(self, track_params: Dict, track_image: pygame.Surface,
                            description: str) -> None:
        """Save a complete training example"""
        timestamp = track_params['timestamp']
        
        # Convert any remaining numpy types to Python native types
        def convert_to_native(obj):
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            return obj
        
        # Convert track parameters recursively
        track_params_native = {k: convert_to_native(v) for k, v in track_params.items()}
        
        # Save track image
        image_path = os.path.join(self.raw_tracks_dir, f"track_{timestamp}.png")
        pygame.image.save(track_image, image_path)
        
        # Save track parameters with background image path
        params_path = os.path.join(self.processed_dir, f"track_{timestamp}.json")
        with open(params_path, 'w') as f:
            json.dump(track_params_native, f, indent=2)
        
        # Save description
        desc_path = os.path.join(self.descriptions_dir, f"track_{timestamp}.txt")
        with open(desc_path, 'w') as f:
            f.write(description)
            
        # If there's a background image, save a copy
        if track_params.get('background_image'):
            bg_path = os.path.join(self.raw_tracks_dir, f"background_{timestamp}.png")
            import shutil
            shutil.copy2(track_params['background_image'], bg_path)

    def generate_track_image(self, track_params: Dict) -> pygame.Surface:
        """Generate track image from parameters"""
        # Reset canvas
        self.track_canvas.clear_track()
        
        # Set starting position in center
        self.track_canvas.current_pos = (self.width // 2, self.height // 2)
        
        # Start with upward direction
        self.track_canvas.current_direction = -90
        
        # Add each segment
        for segment in track_params['segments']:
            if segment['type'] == 'straight':
                self.track_canvas.add_straight_segment(length=segment['length'])
            else:  # curve
                self.track_canvas.add_curve_segment(
                    direction=segment['direction'],
                    angle=segment['angle'],
                    radius=segment['radius']
                )
            
            # Add debug print for each segment
            print(f"Added segment: {segment['type']}, "
                  f"current_pos: {self.track_canvas.current_pos}, "
                  f"current_direction: {self.track_canvas.current_direction}")
        
        # Draw the track
        self.track_canvas.draw()
        
        return self.screen.copy()

    def validate_track(self, track_params: Dict) -> bool:
        """Validate if the track is within bounds and properly connected"""
        # Store original position and direction
        original_pos = self.track_canvas.current_pos
        original_dir = self.track_canvas.current_direction
        
        try:
            # Try generating the track
            self.generate_track_image(track_params)
            
            # Check if any point is outside the safe area
            margin = 100  # Increased margin for better safety
            
            # Get all track points
            all_points = []
            for element in self.track_canvas.track_elements:
                if element['type'] == 'straight':
                    all_points.extend([element['start'], element['end']])
                else:  # curve
                    center = element['center']
                    radius = element['radius']
                    start_angle = element['start_angle']
                    end_angle = element['end_angle']
                    # Sample fewer points for curves
                    angles = np.linspace(start_angle, end_angle, 5)
                    curve_points = [(center[0] + radius * math.cos(angle),
                                   center[1] + radius * math.sin(angle))
                                  for angle in angles]
                    all_points.extend(curve_points)
            
            # Add debug print
            print(f"Track points: {len(all_points)}")
            print(f"Track bounds: x({min(p[0] for p in all_points):.1f}, {max(p[0] for p in all_points):.1f}), "
                  f"y({min(p[1] for p in all_points):.1f}, {max(p[1] for p in all_points):.1f})")
            
            # Check bounds
            for x, y in all_points:
                if (x < margin or x > self.width - margin or
                    y < margin or y > self.height - margin):
                    print(f"Point out of bounds: ({x:.1f}, {y:.1f})")
                    return False
            
            return True
            
        except Exception as e:
            print(f"Track validation failed: {e}")
            return False
        finally:
            # Restore original position and direction
            self.track_canvas.current_pos = original_pos
            self.track_canvas.current_direction = original_dir

    def generate_dataset(self, num_samples: int) -> None:
        """Generate multiple track samples"""
        successful_samples = 0
        attempts = 0
        max_attempts = num_samples * 3  # Allow some failed attempts
        
        while successful_samples < num_samples and attempts < max_attempts:
            # Generate track parameters
            track_params = self.generate_track_params()
            
            # Validate track
            if self.validate_track(track_params):
                # Generate track image
                track_image = self.generate_track_image(track_params)
                
                # Generate description
                description = self.generate_description(track_params)
                
                # Save everything
                self.save_training_example(track_params, track_image, description)
                
                successful_samples += 1
                print(f"Generated valid sample {successful_samples}/{num_samples}")
            
            attempts += 1
            if attempts % 10 == 0:
                print(f"Attempts: {attempts}, Successful: {successful_samples}")
        
        if successful_samples < num_samples:
            print(f"Warning: Only generated {successful_samples} valid samples out of {num_samples} requested") 