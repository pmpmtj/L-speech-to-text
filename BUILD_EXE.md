# Building L-speech-to-text Executable

This guide explains how to build a standalone Windows executable for the L-speech-to-text application using PyInstaller.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Building the Executable](#building-the-executable)
- [Running the Executable](#running-the-executable)
- [Administrator Privileges](#administrator-privileges)
- [Troubleshooting](#troubleshooting)
- [Distribution](#distribution)

## Prerequisites

### System Requirements

- **Windows 10 or later** (Windows 11 recommended)
- **Python 3.8+** installed on the build machine
- **Administrator privileges** for both building and running
- **OpenAI API Key** (set as environment variable)

### Python Dependencies

All dependencies should be installed from `requirements.txt`:

```bash
pip install -r requirements.txt
```

### PyInstaller

Install PyInstaller separately (it's commented out in requirements.txt):

```bash
pip install pyinstaller>=5.13.0
```

## Installation

1. **Clone or download the project**

2. **Install all dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install pyinstaller
   ```

3. **Set environment variables**:
   - `OPENAI_API_KEY`: Your OpenAI API key (required)
   - `SAVE_DEBUG_AUDIO`: Optional, set to `1` to enable debug audio saving
   - `DEBUG_MODE`: Optional, alternative way to enable debug features

## Building the Executable

### Standard Build

Use the provided spec file for a consistent build:

```bash
pyinstaller L-speech-to-text.spec
```

This will create:
- `build/` directory with temporary build files
- `dist/L-speech-to-text/` directory with the executable and all dependencies

### Build Options

The spec file is pre-configured with:
- ✅ Console mode (shows console window for logs)
- ✅ All hidden imports included
- ✅ Certificate bundles for HTTPS
- ✅ PyAutoGUI dependencies
- ✅ PortAudio DLL for audio recording

To change to **windowed mode** (no console window):
1. Open `L-speech-to-text.spec`
2. Change `console=True` to `console=False` in the `EXE()` section
3. Rebuild with `pyinstaller L-speech-to-text.spec`

### Clean Build

To force a complete rebuild:

```bash
# Remove old build artifacts
rmdir /s /q build dist

# Rebuild
pyinstaller L-speech-to-text.spec
```

## Running the Executable

### Location

After building, the executable is located at:
```
dist/L-speech-to-text/L-speech-to-text.exe
```

### Basic Usage

1. **Open PowerShell or Command Prompt as Administrator**
2. **Set your API key** (if not set system-wide):
   ```powershell
   $env:OPENAI_API_KEY="your-api-key-here"
   ```
3. **Navigate to the dist folder**:
   ```bash
   cd dist\L-speech-to-text
   ```
4. **Run the executable**:
   ```bash
   .\L-speech-to-text.exe
   ```

### With Dependency Checks

To run with dependency verification:

```bash
.\L-speech-to-text.exe --apply-checks
```

### Configuration

The application will automatically create configuration directories:
- **Windows**: `%LOCALAPPDATA%\L-speech-to-text\recordings`
- **Logs**: As configured in `common/config/config_app.py`

## Administrator Privileges

### Why Administrator Rights Are Required

The application requires elevated privileges for:

1. **Global keyboard hooks** (`keyboard` library)
   - Captures hotkeys system-wide (Ctrl+Shift+R)
   - Required on Windows due to UAC security model

2. **Clipboard operations** (`pyautogui`, `pyperclip`)
   - Paste transcribed text at cursor position
   - Some Windows configurations restrict clipboard access

3. **Audio device access** (`sounddevice`)
   - Low-level microphone access
   - May be restricted by Windows security policies

### Running as Administrator

**Option 1: Right-click context menu**
1. Right-click `L-speech-to-text.exe`
2. Select "Run as administrator"

**Option 2: Properties (permanent)**
1. Right-click `L-speech-to-text.exe` → Properties
2. Go to "Compatibility" tab
3. Check "Run this program as an administrator"
4. Click OK

**Option 3: PowerShell**
```powershell
Start-Process -FilePath ".\L-speech-to-text.exe" -Verb RunAs
```

### Corporate/IT Environments

In environments with:
- **Enhanced UAC policies**
- **Endpoint protection software**
- **IT security tools**

You may need to:
1. Request IT approval for keyboard hook permissions
2. Add the executable to security tool whitelist
3. Configure group policies to allow global hooks

## Troubleshooting

### Common Issues

#### 1. "OPENAI_API_KEY environment variable is not set"

**Solution**: Set the environment variable before running:
```powershell
# Temporarily (current session)
$env:OPENAI_API_KEY="sk-your-key-here"

# Permanently (system-wide) - requires admin
[System.Environment]::SetEnvironmentVariable('OPENAI_API_KEY', 'sk-your-key-here', 'User')
```

#### 2. "Access Denied" or keyboard hooks not working

**Cause**: Not running as administrator

**Solution**: 
- Right-click the exe and select "Run as administrator"
- Or set the compatibility flag (see [Administrator Privileges](#administrator-privileges))

#### 3. Paste functionality not working

**Possible causes**:
- Not running as administrator
- Anti-virus blocking clipboard access
- PyAutoGUI dependencies not bundled

**Solution**:
1. Ensure running as administrator
2. Temporarily disable anti-virus (to test)
3. Rebuild with: `pyinstaller L-speech-to-text.spec --clean`

#### 4. "Failed to connect to OpenAI API" / SSL Certificate errors

**Cause**: `certifi` package not properly bundled

**Solution**:
1. Verify `certifi` is in requirements.txt
2. Rebuild: `pyinstaller L-speech-to-text.spec --clean`
3. Check internet connectivity

#### 5. Audio recording fails / "PortAudio error"

**Possible causes**:
- PortAudio DLL not bundled
- Audio drivers not installed
- Microphone not connected

**Solution**:
1. Ensure microphone is connected and permissions granted
2. Install/update audio drivers
3. Rebuild with hidden imports: already in spec file

#### 6. ModuleNotFoundError at runtime

**Cause**: Missing hidden import in spec file

**Solution**:
1. Open `L-speech-to-text.spec`
2. Add the missing module to `hidden_imports` list
3. Rebuild with `pyinstaller L-speech-to-text.spec`

### Debug Mode

To troubleshoot issues, enable debug audio saving:

```powershell
$env:SAVE_DEBUG_AUDIO="1"
.\L-speech-to-text.exe
```

This saves audio files to `tests/` directory for inspection.

### Logs

Check logs for detailed error messages:
- Location configured in `common/config/config_app.py`
- Default: Project directory or `%LOCALAPPDATA%\L-speech-to-text\logs`

## Distribution

### Folder Contents

The `dist/L-speech-to-text/` folder contains:
- `L-speech-to-text.exe` - Main executable
- Various `.dll` files - Required dependencies
- `_internal/` folder - Python runtime and libraries

### Distribution Package

To distribute the application:

1. **Zip the entire folder**:
   ```powershell
   Compress-Archive -Path "dist\L-speech-to-text" -DestinationPath "L-speech-to-text-v1.0.zip"
   ```

2. **Include instructions**:
   - Create a `README-DIST.txt` with:
     - How to set OPENAI_API_KEY
     - Requirement to run as administrator
     - Basic usage instructions

3. **Test on a clean machine**:
   - No Python installed
   - Different user account
   - Fresh Windows installation if possible

### System Requirements for End Users

Inform users they need:
- **Windows 10+** (64-bit)
- **Administrator privileges**
- **Internet connection** (for OpenAI API)
- **Microphone** configured and working
- **OpenAI API key** (they must provide their own)

### Security Considerations

⚠️ **Important**:
- Never include your API key in the distribution
- Users must set their own `OPENAI_API_KEY`
- Warn users about administrator privilege requirements
- Document that keyboard hooks have system-wide access

## Advanced Configuration

### Custom Icon

To add a custom icon:

1. Create or obtain an `.ico` file
2. Edit `L-speech-to-text.spec`:
   ```python
   exe = EXE(
       ...
       icon='path/to/icon.ico',
       ...
   )
   ```
3. Rebuild

### One-File Bundle

To create a single `.exe` file (slower startup):

1. Edit `L-speech-to-text.spec`
2. Change `EXE()` section:
   ```python
   exe = EXE(
       pyz,
       a.scripts,
       a.binaries,  # Add this
       a.zipfiles,  # Add this
       a.datas,     # Add this
       [],
       exclude_binaries=False,  # Change this
       name='L-speech-to-text',
       ...
   )
   ```
3. Remove or comment out the `COLLECT()` section
4. Rebuild

### Version Information

Add version info for Windows properties:

1. Create `version_info.txt` using `pyi-grab_version` or manually
2. Add to spec file:
   ```python
   exe = EXE(
       ...
       version='version_info.txt',
       ...
   )
   ```

## Build Checklist

Before distributing:

- [ ] All dependencies in requirements.txt installed
- [ ] PyInstaller installed (`pip install pyinstaller`)
- [ ] Clean build completed (`rmdir /s /q build dist`)
- [ ] Spec file up to date (`L-speech-to-text.spec`)
- [ ] Tested on build machine (as admin)
- [ ] Tested on clean machine (if possible)
- [ ] README/instructions included for end users
- [ ] API key instructions clearly documented
- [ ] Administrator requirement documented

## Support

For issues specific to:
- **Building**: Check PyInstaller documentation
- **Runtime errors**: Check application logs
- **API issues**: Verify OpenAI API key and connectivity
- **Permission issues**: Ensure running as administrator

---

**Last updated**: Generated for EXE readiness
**Tested on**: Windows 10/11 with Python 3.8+

