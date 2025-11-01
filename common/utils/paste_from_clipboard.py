"""
Clipboard paste utility for the jassist application.

Provides functionality to paste content from the clipboard using pyautogui.
"""

def paste_clipboard():
    """
    Paste content from clipboard using pyautogui and add a trailing space.
    
    This function checks if there's content in the clipboard, uses
    pyautogui to simulate Ctrl+V (or Command+V on macOS) to paste it,
    and then adds a space to separate it from future content.
    
    If the add_timestamp config flag is enabled, the content will be
    prefixed with the current timestamp before pasting.
    
    Returns:
        bool: True if paste was successful, False otherwise
    """
    # Import here to avoid circular import issues
    import pyperclip
    import pyautogui
    from datetime import datetime
    from common.logging_utils import get_logger
    from common.config.config_app import config
    
    logger = get_logger('paste_from_clipboard')
    
    try:
        content = pyperclip.paste()
        if content:
            # Try to read from runtime config file if it exists
            add_timestamp = config.paste.add_timestamp
            try:
                from pathlib import Path
                import json
                runtime_config_path = Path(__file__).resolve().parent.parent.parent / "runtime_config.json"
                if runtime_config_path.exists():
                    with open(runtime_config_path, 'r') as f:
                        runtime_cfg = json.load(f)
                    add_timestamp = runtime_cfg.get("paste", {}).get("add_timestamp", add_timestamp)
                    logger.debug(f"Loaded runtime config from {runtime_config_path}")
            except Exception as e:
                logger.debug(f"Could not read runtime config, using default: {e}")
            
            # Check if timestamp should be added
            if add_timestamp:
                logger.debug("add_timestamp flag is enabled, generating timestamp")
                # Generate timestamp using datetime.now()
                timestamp = datetime.now()
                # Format as YY MM DD HH:MM:SS (2-digit year, space-separated)
                timestamp_str = timestamp.strftime("%y %m %d %H:%M:%S")
                # Prefix content with timestamp and space
                content = f"{timestamp_str} {content}"
                logger.debug(f"Timestamp prefix added: {timestamp_str}")
                # Copy the modified content back to clipboard
                pyperclip.copy(content)
                logger.debug("Modified content copied back to clipboard")
            
            # Use platform-agnostic approach (works on both Windows and macOS)
            pyautogui.hotkey('ctrl', 'v')  
            logger.debug("Attempting to paste clipboard content")
            
            # Add a space after the pasted content for proper separation
            pyautogui.write(' ')
            logger.debug("Added trailing space after pasted content")
            
            logger.info("Clipboard content pasted successfully with trailing space")
            return True
        else:
            logger.warning("Clipboard was empty, nothing to paste")
            return False
    except Exception as e:
        logger.error(f"Error during clipboard paste operation: {e}")
        return False

if __name__ == "__main__":
    result = paste_clipboard()
    print(f"Paste operation result: {result}")
