"""
EduMentor — Root Streamlit Application Launcher.
Delegates to the modular edumentor.app application.
"""

import sys
import os

# Ensure workspace root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from edumentor.app import main

if __name__ == "__main__":
    main()
