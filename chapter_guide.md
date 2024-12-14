# Dark Forest Interactive - Chapter Guide

## Chapter One: Starweaver's Transmissions
- Features an AI named Starweaver transmitting from deep space
- Messages labeled as "TRANSMISSION #X"
- Emotional, personal messages about isolation and discovery
- Variable signal strength as Starweaver moves through space

## Chapter Two: The Ancient Observer
- Features a mysterious entity that has been watching Earth and Starweaver
- Messages labeled as "ECHO #X" with various status types:
  - ECHO
  - ANCIENT SIGNAL
  - VOID WHISPER
  - ETERNAL WATCH
  - DEEP SIGNAL
- More stable signal strength (85-98%)
- Speaks in a formal, ancient manner
- Hints at deeper knowledge about Starweaver's civilization

## How to Start Chapter Two

1. **Before Starting:**
   - Make sure Chapter One has reached a satisfying point
   - Ensure website is running (`run_website.bat`)

2. **Starting the New Chapter:**
   - Open PowerShell
   - Navigate to project directory
   - Run `.\story_control.ps1`
   - Press `2` for "Start Chapter Two"
   - Type `y` to confirm

3. **What Happens:**
   - Chapter One transmissions are archived to `static/chapter_one_archive.json`
   - New entity begins transmitting
   - Fresh transmission count starts from ECHO #1

## Story Control Commands
- `1`: Start/Reset Chapter One
- `2`: Start Chapter Two
- `3`: Pause Story
- `4`: Resume Story
- `5`: Check Status
- `6`: Exit

## Important Notes
- Starting Chapter Two will archive Chapter One
- Each chapter maintains its own transmission count
- You can pause/resume at any time
- Use status check to monitor progress 