#!/usr/bin/env python3
"""
Script to generate icon.png for the Nimba SMS Odoo module.
This creates a simple 128x128 PNG icon.

Requirements: Pillow (pip install Pillow)
"""

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("Pillow is required. Install it with: pip install Pillow")
    exit(1)

# Create a 128x128 image
img = Image.new('RGB', (128, 128), color='#875A7B')
draw = ImageDraw.Draw(img)

# Draw a rounded rectangle background
draw.rounded_rectangle([(8, 8), (120, 120)], radius=12, fill='#875A7B', outline='#FFFFFF', width=2)

# Draw SMS text (simple version)
try:
    # Try to use a font if available
    font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 32)
except:
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
    except:
        font = ImageFont.load_default()

# Draw "SMS" text
text = "SMS"
bbox = draw.textbbox((0, 0), text, font=font)
text_width = bbox[2] - bbox[0]
text_height = bbox[3] - bbox[1]
x = (128 - text_width) // 2
y = (128 - text_height) // 2 - 10
draw.text((x, y), text, fill='#FFFFFF', font=font)

# Draw a small phone icon (simple representation)
# Draw a rectangle for phone body
draw.rectangle([(40, 70), (88, 100)], outline='#FFFFFF', width=2)
# Draw a small circle for phone button
draw.ellipse([(60, 105), (68, 113)], fill='#FFFFFF')

# Save the image
img.save('icon.png', 'PNG')
print("Icon generated successfully: icon.png")

