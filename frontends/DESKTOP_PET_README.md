# Desktop Pet Skin System

## Quick Start

Run the desktop pet:
```bash
python3 desktop_pet_v2.pyw
```

## Features

### 1. Multi-skin Support
- Auto-discovers all skins under the `skins/` directory
- Right-click menu to switch skins
- Supports both sprite sheet and GIF formats

### 2. Multi-animation States
- **idle** - Idle animation
- **walk** - Walking animation
- **run** - Running animation
- **sprint** - Sprinting animation

The right-click menu can switch animation states

### 3. Interaction
- **Click** - Drag the pet
- **Double Click** - Close the program
- **Right Click** - Open the menu (switch skin/animation)

### 4. HTTP Remote Control
```bash
# Display message
curl "http://127.0.0.1:51983/?msg=Hello"

# Switch animation state
curl "http://127.0.0.1:51983/?state=run"

# POST message
curl -X POST -d "Task completed" http://127.0.0.1:51983/
```

## Adding New Skins

### Directory Structure
```
skins/
└── your-skin-name/
    ├── skin.json       # Config file (required)
    ├── idle.png        # Animation assets
    ├── walk.png
    ├── run.png
    └── sprint.png
```

### skin.json Configuration Example

#### Sprite Sheet Format (Recommended)
```json
{
  "name": "My Pet",
  "version": "1.0.0",
  "author": "Your Name",
  "description": "Description",
  "format": "sprite",
  "animations": {
    "idle": {
      "file": "idle.png",
      "loop": true,
      "sprite": {
        "frameWidth": 44,
        "frameHeight": 31,
        "frameCount": 6,
        "columns": 6,
        "fps": 6,
        "startFrame": 0
      }
    },
    "walk": {
      "file": "walk.png",
      "loop": true,
      "sprite": {
        "frameWidth": 65,
        "frameHeight": 32,
        "frameCount": 8,
        "columns": 8,
        "fps": 8,
        "startFrame": 0
      }
    }
  }
}
```

#### GIF Format
```json
{
  "name": "My Pet",
  "format": "gif",
  "animations": {
    "idle": {
      "file": "idle.gif",
      "loop": true
    },
    "walk": {
      "file": "walk.gif",
      "loop": true
    }
  }
}
```

### Configuration Notes

- **frameWidth/frameHeight**: Single frame dimensions (in pixels)
- **frameCount**: Number of frames
- **columns**: Number of columns in the sprite sheet
- **fps**: Playback frame rate
- **startFrame**: Starting frame index (0-indexed)

### Sprite Sheet Layout

```
+-------+-------+-------+-------+
| Frm 0 | Frm 1 | Frm 2 | Frm 3 |  ← Row 1
+-------+-------+-------+-------+
| Frm 4 | Frm 5 | Frm 6 | Frm 7 |  ← Row 2
+-------+-------+-------+-------+
```

If `columns=4, startFrame=2, frameCount=3`, it reads: Frame 2, Frame 3, Frame 4

## Included Skins

1. **Glube** - Pixel monster (Multi-file sprite)
2. **Vita** - Pixel dinosaur (Single-file sprite)
3. **Doux** - Pixel dinosaur (Single-file sprite)

## Importing More Skins from ai-bubu

The ai-bubu project contains more skin assets which can be directly copied:

```bash
# Copy skins
cp -r ai-bubu-main/packages/app/public/skins/boy frontends/skins/
cp -r ai-bubu-main/packages/app/public/skins/dinosaur frontends/skins/
cp -r ai-bubu-main/packages/app/public/skins/line frontends/skins/
cp -r ai-bubu-main/packages/app/public/skins/mort frontends/skins/
cp -r ai-bubu-main/packages/app/public/skins/tard frontends/skins/
```

## Integration with stapp.py

Clicking the "🐱 Desktop Pet" button in `stapp.py` automatically launches the desktop pet and sends a notification at the end of each turn.

## Troubleshooting

### Skin does not display
1. Check if `skin.json` format is correct
2. Confirm the image file exists
3. Check if sprite config parameters match image dimensions

### Animation is not smooth
- Adjust the `fps` parameter
- Check if the frame count is correct

### Transparent background issues
- Ensure the PNG file contains an alpha channel
- Use images with RGBA mode

## Technical Details

- Built on Tkinter + PIL/Pillow
- Supports transparent background (#01FF01 color key)
- Window stays on top, borderless
- HTTP server port: 51983
