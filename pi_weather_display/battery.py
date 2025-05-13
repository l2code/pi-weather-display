import os
import sys
import time
import json
import logging
from datetime import datetime

# Configure module-level logger
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

# Path for storing charging history
def get_history_file_path():
    current_dir = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(current_dir, 'battery_history.json')

def is_raspberry_pi():
    """Check if we're actually running on a Raspberry Pi"""
    try:
        with open('/proc/device-tree/model', 'r') as f:
            model = f.read()
            return 'Raspberry Pi' in model
    except:
        return False

def get_battery_status():
    """
    Get battery percentage and charging status from UPS HAT
    
    Returns:
        tuple: (battery_percentage, is_charging, current_mA)
    """
    # For non-Raspberry Pi environments, return mock values
    if not is_raspberry_pi():
        mock_level = 85.7
        mock_charging = True  # Can toggle for testing
        mock_current = 250 if mock_charging else -150
        logger.info(f"Using mock battery level: {mock_level:.1f}%, Charging: {mock_charging}")
        return (mock_level, mock_charging, mock_current)
    
    # We're on a Raspberry Pi - try to use the real INA219
    try:
        # Add paths to find INA219.py
        current_dir = os.path.dirname(os.path.realpath(__file__))
        parent_dir = os.path.dirname(current_dir)
        ups_hat_dir = os.path.join(current_dir, 'external', 'ups_hat')

        if current_dir not in sys.path:
            sys.path.append(current_dir)
        if parent_dir not in sys.path:
            sys.path.append(parent_dir)                
        if ups_hat_dir not in sys.path:
            sys.path.append(ups_hat_dir)
            
        from INA219 import INA219
        
        # Create an INA219 instance
        ina219 = INA219(addr=0x43)
        
        # Get battery level
        bus_voltage = ina219.getBusVoltage_V()
        p = (bus_voltage - 3)/1.2*100
        if p > 100: p = 100
        if p < 0: p = 0
        
        # Get current to determine charging status
        current_mA = ina219.getCurrent_mA()
        is_charging = current_mA > 20  # Positive current means charging
        
        logger.info(f"Battery level: {p:.1f}%, Current: {current_mA:.1f}mA, Charging: {is_charging}")
        return (p, is_charging, current_mA)
    except Exception as e:
        logger.error(f"Error reading battery status: {e}")
        return (-1, False, 0)

def update_charging_history(battery_level, is_charging, current_mA):
    """
    Update the charging history file with new battery status
    Returns the last charging timestamp and status
    """
    history_file = get_history_file_path()
    now = datetime.now()
    timestamp = now.isoformat()
    
    # Default history structure
    history_data = {
        "last_charging_time": None,
        "charging_history": [],
        "last_check": {
            "timestamp": timestamp,
            "status": "unknown",
            "battery_level": -1,
            "current_mA": 0
        }
    }
    
    # Load existing history if available
    try:
        if os.path.exists(history_file):
            with open(history_file, 'r') as f:
                history_data = json.load(f)
    except:
        logger.warning("Could not read history file, starting new history")
    
    # Current status
    current_status = "charging" if is_charging else "discharging"
    
    # Check if status changed from last check
    status_changed = False
    if "last_check" in history_data:
        last_status = history_data["last_check"].get("status", "unknown")
        if last_status != current_status:
            status_changed = True
    
    # Update last charging time if we're charging now
    if is_charging and status_changed:
        history_data["last_charging_time"] = timestamp
    
    # Update history if status changed or significant battery level change
    if status_changed or "last_check" not in history_data:
        history_data["charging_history"].append({
            "timestamp": timestamp,
            "status": current_status,
            "battery_level": battery_level,
            "current_mA": current_mA
        })
        
        # Keep only the last 50 entries
        if len(history_data["charging_history"]) > 50:
            history_data["charging_history"] = history_data["charging_history"][-50:]
    
    # Update last check
    history_data["last_check"] = {
        "timestamp": timestamp,
        "status": current_status,
        "battery_level": battery_level,
        "current_mA": current_mA
    }
    
    # Save history
    try:
        with open(history_file, 'w') as f:
            json.dump(history_data, f, indent=2)
    except:
        logger.error("Could not write history file")
    
    return history_data.get("last_charging_time"), current_status

def get_formatted_last_charge_time():
    """Get the formatted last charge time for display"""
    history_file = get_history_file_path()
    
    if not os.path.exists(history_file):
        return None
    
    try:
        with open(history_file, 'r') as f:
            history_data = json.load(f)
            
        last_charge_time = history_data.get("last_charging_time")
        if not last_charge_time:
            return None
            
        # Parse the ISO timestamp
        charge_time = datetime.fromisoformat(last_charge_time)
        
        # Format as mm/dd hh:mm
        formatted_time = charge_time.strftime("%m/%d %H:%M")
        return f"Last chg: {formatted_time}"
    except:
        return None

def add_battery_symbol_to_image(img, battery_pct, is_charging=False, font=None, position=(None, None)):
    """
    Add a graphical battery symbol with percentage inside to an image
    
    Args:
        img: PIL Image object
        battery_pct: Battery percentage (float)
        is_charging: True if battery is charging
        font: PIL ImageFont to use (optional)
        position: Custom (x, y) position tuple (optional, top-right if None)
        
    Returns:
        PIL Image with battery symbol added
    """
    if battery_pct < 0:
        return img  # No valid battery percentage
    
    try:
        from PIL import ImageDraw, ImageFont
        
        # Create a copy of the image to avoid modifying the original
        result = img.copy()
        draw = ImageDraw.Draw(result)
        
        # Use provided font or load default
        if font is None:
            try:
                # Try to load DejaVu Sans as in the weather display
                font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
                font = ImageFont.truetype(font_path, 12)
            except (IOError, OSError):
                font = ImageFont.load_default()
        
        # Battery symbol dimensions
        batt_width = 40
        batt_height = 24
        batt_border = 2
        batt_tip_width = 4
        batt_tip_height = 8
        batt_fill_width = int((batt_width - 2*batt_border) * (battery_pct / 100))
        
        # Percentage text
        percentage_text = f"{int(battery_pct)}%"
        text_bbox = draw.textbbox((0, 0), percentage_text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1] +5
        
        # Default position: top-right with padding
        if position[0] is None or position[1] is None:
            x_pos = img.width - batt_width - batt_tip_width - 10
            y_pos = 10
        else:
            x_pos, y_pos = position
        
        # Draw battery outline
        # First the main battery body
        draw.rectangle(
            (x_pos, y_pos, x_pos + batt_width, y_pos + batt_height),
            outline=0, width=batt_border, fill=255  # Black outline, white fill
        )
        
        # Add battery tip on the right
        draw.rectangle(
            (x_pos + batt_width, y_pos + (batt_height - batt_tip_height) // 2,
             x_pos + batt_width + batt_tip_width, y_pos + (batt_height + batt_tip_height) // 2),
            outline=0, width=1, fill=0  # Black outline and fill
        )
        
        # Draw battery fill level
        if batt_fill_width > 0:
            draw.rectangle(
                (x_pos + batt_border, y_pos + batt_border,
                 x_pos + batt_border + batt_fill_width, y_pos + batt_height - batt_border),
                outline=None, fill=0  # Black fill
            )
        
        # Add percentage text centered inside battery
        text_x = x_pos + (batt_width - text_width) // 2
        text_y = y_pos + (batt_height - text_height) // 2
        
        # Add a small white background behind the text for visibility when battery is filled
        padding = 1
        draw.rectangle(
            (text_x - padding, text_y - padding, 
             text_x + text_width + padding, text_y + text_height + padding),
            outline=None, fill=255  # White fill for text background
        )
        
        # Draw text
        draw.text(
            (text_x, text_y),
            percentage_text,
            font=font,
            fill=0  # Black text
        )
        
        # Add charging indicator if charging
        if is_charging:
            # Draw a small lightning bolt or indicator next to the battery
            bolt_x = x_pos - 12
            bolt_y = y_pos + (batt_height // 2) - 5
            
            # Simple lightning bolt using lines
            draw.line([(bolt_x, bolt_y), (bolt_x + 4, bolt_y + 5), 
                       (bolt_x, bolt_y + 5), (bolt_x + 4, bolt_y + 10)], 
                      fill=0, width=2)
        
        return result
    except Exception as e:
        logger.error(f"Error adding battery symbol to image: {e}")
        return img

def add_last_charge_time_to_image(img, font=None):
    """
    Add last charge time to bottom of image (left side)
    This is designed to be on the same line as the "Updated: XX:XX" text
    """
    # Get the formatted time
    last_charge_text = get_formatted_last_charge_time()
    
    # TEMPORARY FIX: If no charge time is found, use a hardcoded one for testing
    if not last_charge_text:
        print("No last charge time available, using hardcoded value for testing")
        # Format: mm/dd hh:mm
        import datetime
        now = datetime.datetime.now()
        formatted_time = now.strftime("%m/%d %H:%M")
        last_charge_text = f"Last Chrg: {formatted_time}"
    
    try:
        from PIL import ImageDraw, ImageFont
        
        # Create a copy of the image
        result = img.copy()
        draw = ImageDraw.Draw(result)
        
        # Use provided font or load default
        if font is None:
            try:
                font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
                font = ImageFont.truetype(font_path, 10)  # Smaller font for bottom text
            except (IOError, OSError):
                font = ImageFont.load_default()
        
        # Position for bottom left, with small padding
        x_pos = 10
        y_pos = img.height - 22  # Position for the bottom area
        
        # Draw text with black fill (0)
        draw.text((x_pos, y_pos), last_charge_text, font=font, fill=0)
        
        return result
    except Exception as e:
        print(f"Error adding charge time to image: {e}")
        return img

if __name__ == "__main__":
    # Set up root logger when run directly
    logging.basicConfig(level=logging.INFO, 
                        format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Get battery status and update history
    battery_pct, is_charging, current_mA = get_battery_status()
    last_charge_time, status = update_charging_history(battery_pct, is_charging, current_mA)
    
    print(f"Battery: {battery_pct:.1f}%, Status: {status}, Current: {current_mA}mA")
    print(f"Last charge time: {get_formatted_last_charge_time()}")
    
    # Test image creation
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Create a test image
        test_img = Image.new("1", (400, 300), 255)
        draw = ImageDraw.Draw(test_img)
        draw.rectangle((0, 0, 399, 299), outline=0, width=2)
        
        # Draw test content
        draw.text((10, 10), "Weather Display", font=ImageFont.load_default(), fill=0)
        
        # Add battery with charging indicator
        test_img = add_battery_symbol_to_image(test_img, battery_pct, is_charging)
        
        # Add last charge time at bottom
        test_img = add_last_charge_time_to_image(test_img)
        
        # Add sample "Updated" text to show positioning
        draw = ImageDraw.Draw(test_img)
        draw.text((300, 280), "Updated: 08:26 PM", font=ImageFont.load_default(), fill=0)
        
        # Display
        test_img.show()
    except Exception as e:
        print(f"Error creating test image: {e}")