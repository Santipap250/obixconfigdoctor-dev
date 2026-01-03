# obixconfigdoctor (patched)

This repository was patched to improve input validation, add error handlers, and provide safer defaults.

## Quick start (mobile / termux)
1. Install Termux on Android from F-Droid or Play Store (or use GitHub mobile app to upload files).
2. In Termux:
   ```bash
   pkg install python git
   python -m pip install -r requirements.txt
   python app.py
   ```
3. Set SECRET_KEY in env before running in production:
   ```bash
   export SECRET_KEY="change-this-to-a-random-secret"
   ```

## What was changed
- Replaced `app.py` with a safer version (validation, error handlers).
- Added `templates/error.html` for user-friendly errors.
- Added tests skeleton and patch file for easy review.