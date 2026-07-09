import subprocess
import logging
import sys

logger = logging.getLogger(__name__)

def open_path(path: str):
    """
    Safely opens a file or directory using the default system application.
    """
    try:
        if sys.platform == "darwin":
            # macOS
            subprocess.run(["open", path], check=True)
        elif sys.platform == "win32":
            # Windows
            import os
            os.startfile(path)
        else:
            # Linux
            subprocess.run(["xdg-open", path], check=True)
    except Exception as e:
        logger.error(f"Failed to open path {path}: {e}")

def show_notification(title: str, message: str, subtitle: str = None, sound: str = "Glass"):
    """
    Safely displays a desktop notification on macOS using osascript.
    """
    if sys.platform != "darwin":
        logger.debug("Notifications are currently only supported on macOS.")
        return

    try:
        # Escape double quotes and backslashes to prevent AppleScript injection
        title_esc = title.replace('\\', '\\\\').replace('"', '\\"')
        msg_esc = message.replace('\\', '\\\\').replace('"', '\\"')
        
        script_parts = [f'display notification "{msg_esc}"', f'with title "{title_esc}"']
        
        if subtitle:
            sub_esc = subtitle.replace('\\', '\\\\').replace('"', '\\"')
            script_parts.append(f'subtitle "{sub_esc}"')
            
        if sound:
            script_parts.append(f'sound name "{sound}"')
            
        script = " ".join(script_parts)
        
        # Run osascript directly without shell=True
        subprocess.run(["osascript", "-e", script], check=True)
    except Exception as e:
        logger.error(f"Failed to show notification: {e}")
