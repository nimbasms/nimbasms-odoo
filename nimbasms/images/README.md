# Images Directory

This directory should contain screenshots and images for the Odoo Apps Store.

## Required Files

1. **main_screenshot.png** - Main screenshot/cover image (thumbnail)
   - Displayed on the app store listing
   - Recommended size: 1280x720 or similar
   - Format: PNG, GIF, or JPEG

## Optional Files

- **main_1.png**, **main_2.png**, etc. - Additional screenshots
- If you have multiple images and one ends with `_screenshot`, it will be displayed as the big screenshot

## Note

The `images` key in `__manifest__.py` references these files:
```python
'images': [
    'images/main_screenshot.png',
],
```

Please add your actual screenshot images to this directory.

