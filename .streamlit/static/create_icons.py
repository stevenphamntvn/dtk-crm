# Script để tạo icon placeholder cho PWA
from PIL import Image, ImageDraw, ImageFont
import os

def create_placeholder_icons():
    """Tạo icon placeholder đơn giản cho CRM"""
    
    # Tạo thư mục static nếu chưa có
    static_dir = os.path.join(os.path.dirname(__file__))
    os.makedirs(static_dir, exist_ok=True)
    
    # Tạo icon 192x192
    img_192 = Image.new('RGB', (192, 192), color='#FF4B4B')
    draw_192 = ImageDraw.Draw(img_192)
    
    # Vẽ chữ "CRM" vào giữa
    try:
        # Thử sử dụng font hệ thống
        font = ImageFont.truetype("arial.ttf", 60)
    except:
        # Fallback to default font
        font = ImageFont.load_default()
    
    text = "CRM"
    # Get text bounding box
    bbox = draw_192.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Center text
    x = (192 - text_width) // 2
    y = (192 - text_height) // 2
    
    draw_192.text((x, y), text, fill='white', font=font)
    
    # Lưu icon 192
    icon_192_path = os.path.join(static_dir, 'icon-192.png')
    img_192.save(icon_192_path)
    print(f"Created {icon_192_path}")
    
    # Tạo icon 512x512
    img_512 = Image.new('RGB', (512, 512), color='#FF4B4B')
    draw_512 = ImageDraw.Draw(img_512)
    
    try:
        font_large = ImageFont.truetype("arial.ttf", 160)
    except:
        font_large = ImageFont.load_default()
    
    bbox_512 = draw_512.textbbox((0, 0), text, font=font_large)
    text_width_512 = bbox_512[2] - bbox_512[0]
    text_height_512 = bbox_512[3] - bbox_512[1]
    
    x_512 = (512 - text_width_512) // 2
    y_512 = (512 - text_height_512) // 2
    
    draw_512.text((x_512, y_512), text, fill='white', font=font_large)
    
    # Lưu icon 512
    icon_512_path = os.path.join(static_dir, 'icon-512.png')
    img_512.save(icon_512_path)
    print(f"Created {icon_512_path}")
    
    print("Successfully created placeholder icons for PWA!")

if __name__ == "__main__":
    try:
        create_placeholder_icons()
    except ImportError:
        print("Need to install Pillow: pip install Pillow")
    except Exception as e:
        print(f"Error creating icons: {e}")
        print("You can create icons manually using any image tool")