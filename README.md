# Formula Student Track Builder

A Python-based graphical tool for designing and exporting Formula Student autocross/endurance tracks. Create precise track layouts with an intuitive interface, supporting background images and multiple export formats.

## Features

### Track Building
- **Customizable Segments**
  - Straight segments with adjustable length (20-300 pixels)
  - Curved segments with adjustable radius (20-150 pixels)
  - Multiple curve angles (15°, 30°, 45°, 60°, 75°, 90°, 120°, 135°, 150°, 180°)
  - Both left and right turns supported

### Interface Controls
- **Track Manipulation**
  - Set custom starting points by clicking on the canvas
  - Precise angle input for segments
  - Visual angle selection with mouse
  - Undo functionality
  - Clear track option
  - Zoom in/out with mouse wheel
  - Pan view with middle mouse button

- **Segment Parameters**
  - Adjustable straight segment length
  - Adjustable curve radius
  - Real-time visual feedback

### Background Support
- Load custom background images (PNG, JPG)
- Default background (goms_airfield.png)
- Transparent grid overlay for better visualization
- Maintains aspect ratio while scaling to canvas

### Export Options
- **Multiple Export Formats**
  - PNG screenshot of the track
  - NumPy array of track coordinates (.npy)
  - GPX file format for GPS compatibility
- Automatic file naming with timestamps
- Organized output directory structure

## Installation

1. Clone the repository from GitHub
2. Navigate to the project directory
3. Install required dependencies using pip and the requirements.txt file

## Usage

### Starting the Application
Run the main.py file to launch the application.

### Basic Controls

1. **Setting Track Start Point**
   - Click "Set Start Point"
   - Click anywhere on the canvas
   - A green arrow indicates the initial direction

2. **Adding Straight Segments**
   - Adjust length using +/- buttons
   - Click "Add Straight Segment"
   - Or set custom angle:
     - Click "Set Direction" and use mouse
     - Or click "Enter Angle" for precise input

3. **Adding Curves**
   - Adjust radius using +/- buttons
   - Choose from predefined angles
   - Select left or right direction

4. **Background Management**
   - Click "Load Background" to choose custom image
   - Images are loaded from track_backgrounds directory
   - Default background loads automatically

5. **View Control**
   - Use mouse wheel to zoom in/out
   - Hold middle mouse button to pan view
   - Zoom centers on mouse position
   - Zoom range: 20% to 500%

### Advanced Features

1. **Track Modification**
   - Use "Undo" to remove last segment
   - "Clear Track" removes all segments
   - Adjust segment parameters anytime

2. **Export Options**
   - Tracks auto-save on exit
   - Exports to output/images/ and output/tracks/
   - Supports multiple format exports simultaneously

## Project Structure

```
fs_track_builder/
├── src/
│   ├── gui/
│   │   ├── main_window.py
│   │   ├── track_canvas.py
│   │   └── control_panel.py
│   └── models/
│       └── track_element.py
├── track_backgrounds/
│   └── goms_airfield.png
├── output/
│   ├── images/
│   └── tracks/
├── main.py
└── README.md
```

## Technical Details

### Track Elements
- **Straight Segments**
  - Defined by start point, length, and angle
  - Continuous connection with previous segment

- **Curved Segments**
  - Defined by center point, radius, and sweep angle
  - Automatic tangent calculation for smooth transitions

### Coordinate System
- Origin (0,0) at top-left corner
- Positive x-axis points right
- Positive y-axis points down
- Angles measured clockwise from vertical

### Export Formats
- **PNG**: Full resolution screenshot
- **NPY**: NumPy array of (x,y) coordinates
- **GPX**: Standard GPS Exchange Format
  - Coordinates scaled to GPS format
  - Compatible with navigation software

## Development

The project uses:
- Python 3.7+
- Pygame for graphics and user interface
- NumPy for coordinate calculations
- GPXpy for GPS file export
- Type hints throughout the codebase
- Modular architecture for easy extension

## Contributing

Contributions are welcome! The codebase is fully typed and follows a modular structure. Feel free to submit pull requests or open issues for:
- New features
- Bug fixes
- Documentation improvements
- Performance optimizations

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built using Pygame for robust graphics handling
- GPX export functionality using gpxpy
- Background image support for real track visualization
- Formula Student community for track design inspiration

## Data Generation

The project now includes functionality for generating training data for machine learning models. To generate training data:

```
python main.py --generate-data --num-samples 100
```

This will generate:
- Track images in data/raw_tracks/
- Track descriptions in data/descriptions/
- Track parameters in data/processed/

Each track includes:
- Randomized segments (straight and curves)
- Natural language description
- Full parameter set for reproduction
- Standardized image format

The generated data can be used to train models for:
- Track generation from descriptions
- Track analysis and validation
- Style transfer between tracks
