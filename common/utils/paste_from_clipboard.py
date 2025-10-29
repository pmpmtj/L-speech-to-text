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
    
    Returns:
        bool: True if paste was successful, False otherwise
    """
    # Import here to avoid circular import issues
    import pyperclip
    import pyautogui
    from common.logging_utils import get_logger
    
    logger = get_logger('paste_from_clipboard')
    
    try:
        content = pyperclip.paste()
        if content:
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
