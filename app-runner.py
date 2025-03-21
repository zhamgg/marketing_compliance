# Run this file to start the Marketing Compliance Review Application
import streamlit as st
import subprocess
import sys
import os

def main():
    """
    Main entry point for the Marketing Compliance Review Application.
    This script will check for the required dependencies and launch the Streamlit app.
    """
    # Check for required packages
    required_packages = [
        "streamlit", 
        "pandas", 
        "numpy", 
        "plotly", 
        "pillow", 
        "xlsxwriter"
    ]
    
    print("Checking for required packages...")
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"✗ {package}")
    
    # Install any missing packages
    if missing_packages:
        print("\nInstalling missing packages...")
        for package in missing_packages:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    
    # Launch the Streamlit app
    print("\nLaunching Marketing Compliance Review Application...")
    
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to the main application file
    app_path = os.path.join(script_dir, "marketing_compliance_app.py")
    
    # Run Streamlit
    subprocess.call(["streamlit", "run", app_path])

if __name__ == "__main__":
    main()
