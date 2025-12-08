#!/usr/bin/env python3
"""
Debug startup script to capture error messages
Run this instead of the main application to see detailed error output
"""

import sys
import traceback
from datetime import datetime

# Redirect all output to a log file
log_file = f"startup_error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

try:
    print(f"Starting application... (logging to {log_file})")

    with open(log_file, 'w') as f:
        # Redirect stdout and stderr
        sys.stdout = f
        sys.stderr = f

        print("=" * 80)
        print(f"Application Startup Debug Log - {datetime.now()}")
        print("=" * 80)
        print()

        # Import and run the main application
        print("Importing main application module...")
        import tkinter as tk
        from AIT_CMMS_REV3 import AITCMMSSystem

        print("Main module imported successfully")
        print("Starting main application...")

        # Create and run the actual application
        root = tk.Tk()
        print("Tk root window created")

        app = AITCMMSSystem(root)
        print("AITCMMSSystem initialized successfully")

        print("Starting mainloop...")
        root.mainloop()
        print("Application closed normally")

except Exception as e:
    with open(log_file, 'a') as f:
        f.write("\n" + "=" * 80 + "\n")
        f.write("FATAL ERROR DURING STARTUP\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Error Type: {type(e).__name__}\n")
        f.write(f"Error Message: {str(e)}\n\n")
        f.write("Full Traceback:\n")
        f.write(traceback.format_exc())
        f.write("\n" + "=" * 80 + "\n")

    print(f"\n\nERROR: Application crashed during startup!")
    print(f"Error details have been saved to: {log_file}")
    print(f"\nError: {type(e).__name__}: {str(e)}")
    print(f"\nPlease share the contents of {log_file} for debugging.")
    sys.exit(1)
