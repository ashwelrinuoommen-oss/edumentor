# EduMentor - Desktop Launcher and Custom Icon Guide

This guide explains how to use the custom EduMentor Windows desktop launcher and icon.

---

## Asset and Launcher Locations

| File | Location | Description |
| :--- | :--- | :--- |
| **Windows Desktop Launcher** | `Launch-EduMentor.bat` | One-click batch launcher for Windows |
| **Shortcut Installer (PowerShell)** | `Install-Desktop-Shortcut.ps1` | PowerShell script to create Desktop `.lnk` shortcut |
| **Shortcut Installer (Batch)** | `Install-Desktop-Shortcut.bat` | Double-clickable runner for the installer |
| **Windows Icon (Multi-Resolution)** | `assets/branding/EduMentor.ico` | High-quality ICO (16, 24, 32, 48, 64, 128, 256 px) |
| **Master Square Icon (PNG)** | `assets/branding/edumentor-icon.png` | 1024x1024 master icon artwork |
| **Favicon Icon** | `assets/branding/favicon.ico` | Multi-resolution browser icon (16, 32, 48 px) |
| **Mentor Portrait (PNG)** | `assets/branding/mentor-portrait.png` | High-resolution cropped portrait |
| **Desktop Shortcut** | `C:\Users\ASHWEL RINU OOMMEN\Desktop\EduMentor.lnk` | Windows Desktop icon |

---

## How to Launch EduMentor

### Method 1: Desktop Icon (Recommended)
1. Go to your Windows Desktop.
2. Double-click the **`EduMentor`** icon.
3. The launcher will automatically:
   - Detect your Python environment.
   - Check if EduMentor is already running (to prevent duplicate processes).
   - Start the Streamlit application server in the background.
   - Wait until the server health check responds `200 ok`.
   - Open EduMentor in a dedicated clean app window (via Edge or Chrome if available, or your default browser).

### Method 2: Project Launcher
Double-click `Launch-EduMentor.bat` directly in this project folder.

### Method 3: Command Line
```powershell
python -m streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## How to Stop EduMentor

When you have finished your study session:
1. Close your browser window.
2. In the minimized or background **"EduMentor Server"** terminal window, press **`Ctrl + C`** or simply close the window.

---

## How to Reinstall the Desktop Shortcut

If you ever move this folder or want to recreate the desktop shortcut:
- Double-click **`Install-Desktop-Shortcut.bat`**, OR
- Open PowerShell in this folder and run:
  ```powershell
  powershell -ExecutionPolicy Bypass -File Install-Desktop-Shortcut.ps1
  ```

---

## Troubleshooting

### 1. "Python was not found" error
- Ensure Python 3.10+ is installed from [python.org](https://www.python.org/).
- Ensure **"Add python.exe to PATH"** was checked during Python installation.

### 2. "Streamlit is not installed" error
- Open a terminal in this project folder and run:
  ```powershell
  pip install -r requirements.txt
  ```

### 3. Server took longer than expected to report ready status
- The launcher includes an automatic 30-second health poll against `http://127.0.0.1:8501/_stcore/health`.
- If your system is under heavy load, the browser will still open automatically once the timeout completes.

---

## How to Change the Icon Later

1. Replace `assets/branding/EduMentor.ico` with your new `.ico` file.
2. Run `Install-Desktop-Shortcut.bat` to update your desktop shortcut with the new icon.
