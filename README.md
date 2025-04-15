This repository contains code to build Formula Student Tracks

# Formula Student Track Builder

A Python-based tool for designing and validating Formula Student competition tracks.

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/fs_track_builder.git
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Features
- Generate track layouts following Formula Student competition rules
- Validate track dimensions and cone placement
- Export tracks to common formats (CSV, JSON)
- Visualize tracks with matplotlib
- Calculate optimal racing line

## Usage
```python
from fs_track_builder import TrackBuilder

# Create a new track
track = TrackBuilder()

# Add track elements
track.add_straight(length=30)
track.add_corner(radius=9, angle=90)

# Validate track
track.validate()

# Export track
track.export("my_track.json")
```

## Configuration
Track parameters can be configured in `config.yaml`:
- Minimum track width
- Maximum track length
- Cone spacing
- Safety margins

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments
- Formula Student Germany for track design guidelines
- Contributors and maintainers
