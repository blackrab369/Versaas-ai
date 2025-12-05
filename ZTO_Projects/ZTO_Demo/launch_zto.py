#!/usr/bin/env python3
"""
Zero-to-One Virtual Software Inc. - Main Launcher
Launches the complete virtual company simulation
"""

import sys
import os
import subprocess
import threading
import time
import argparse
from pathlib import Path
import platform
import webbrowser

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

def launch_auditorium():
    """Launch the 2.5D auditorium simulation"""
    try:
        from _Auditorium.zto_auditorium import main as auditorium_main
        auditorium_main()
    except Exception as e:
        print(f"Error launching auditorium: {e}")

def launch_ceo_chat():
    """Launch the CEO chat interface"""
    try:
        from ceo_chat import CEOChatInterface
        chat = CEOChatInterface()
        chat.run()
    except Exception as e:
        print(f"Error launching CEO chat: {e}")

def launch_dashboard():
    """Launch the financial dashboard"""
    try:
        from .finance.dashboard_generator import FinancialDashboard
        dashboard = FinancialDashboard()
        path = dashboard.generate_dashboard()
        
        # Open in browser
        webbrowser.open(f"file://{Path(path).absolute()}")
        print(f"Dashboard opened: {path}")
    except Exception as e:
        print(f"Error launching dashboard: {e}")

def launch_vscode():
    """Open VS Code workspace"""
    try:
        if platform.system() == "Windows":
            subprocess.run(['code', '.'], shell=True)
        else:
            subprocess.run(['code', '.'])
    except Exception as e:
        print(f"Could not launch VS Code: {e}")
        print("Please open VS Code manually and open the project folder")

def create_windows_shortcut():
    """Create Windows shortcut for easy launching"""
    if platform.system() != "Windows":
        print("Windows shortcut creation only works on Windows")
        return
    
    try:
        import winshell
        from win32com.client import Dispatch
        
        # Create shortcut on desktop
        desktop = winshell.desktop()
        path = os.path.join(desktop, "ZTO Inc.lnk")
        
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(path)
        shortcut.Targetpath = sys.executable
        shortcut.Arguments = str(Path(__file__).absolute())
        shortcut.WorkingDirectory = str(Path(__file__).parent)
        shortcut.IconLocation = sys.executable
        shortcut.save()
        
        print(f"Windows shortcut created: {path}")
        return path
    except Exception as e:
        print(f"Could not create Windows shortcut: {e}")
        return None

def show_menu():
    """Show interactive menu"""
    print("\n" + "="*60)
    print("Zero-to-One Virtual Software Inc. - Main Menu")
    print("="*60)
    print("1. Launch 2.5D Auditorium (Virtual Office)")
    print("2. Launch CEO Chat Interface")
    print("3. Open Financial Dashboard")
    print("4. Open VS Code Workspace")
    print("5. Create Windows Shortcut")
    print("6. Launch All Components")
    print("7. Exit")
    print("="*60)
    
    choice = input("\nEnter your choice (1-7): ").strip()
    return choice

def launch_all():
    """Launch all components simultaneously"""
    print("Launching all ZTO Inc. components...")
    
    # Launch components in separate threads
    threads = []
    
    # Auditorium
    auditorium_thread = threading.Thread(target=launch_auditorium, daemon=True)
    threads.append(auditorium_thread)
    auditorium_thread.start()
    time.sleep(2)  # Small delay between launches
    
    # CEO Chat (this will block, so we handle it differently)
    print("CEO Chat Interface is ready (use menu option 2 to open)")
    
    # Dashboard
    try:
        launch_dashboard()
        print("Financial dashboard opened in browser")
    except Exception as e:
        print(f"Could not open dashboard: {e}")
    
    # VS Code
    try:
        launch_vscode()
        print("VS Code workspace opened")
    except Exception as e:
        print(f"Could not open VS Code: {e}")
    
    print("\nAll components launched! The virtual company is now operational.")
    print("Press Ctrl+C to stop the simulation.")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down ZTO Inc...")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Launch Zero-to-One Virtual Software Inc.")
    parser.add_argument('--mode', choices=['menu', 'auditorium', 'chat', 'dashboard', 'all'], 
                       default='menu', help='Launch mode')
    parser.add_argument('--no-shortcut', action='store_true', help='Skip Windows shortcut creation')
    
    args = parser.parse_args()
    
    print("Zero-to-One Virtual Software Inc. - Virtual Company Launcher")
    print("="*65)
    print("Initializing virtual software company with 25 AI employees...")
    
    # Create Windows shortcut if on Windows
    if platform.system() == "Windows" and not args.no_shortcut:
        try:
            shortcut_path = create_windows_shortcut()
            if shortcut_path:
                print(f"Created desktop shortcut: {shortcut_path}")
        except Exception as e:
            print(f"Could not create shortcut: {e}")
    
    if args.mode == 'menu':
        while True:
            choice = show_menu()
            
            if choice == '1':
                print("Launching 2.5D Auditorium...")
                launch_auditorium()
            elif choice == '2':
                print("Launching CEO Chat Interface...")
                launch_ceo_chat()
            elif choice == '3':
                print("Opening Financial Dashboard...")
                launch_dashboard()
            elif choice == '4':
                print("Opening VS Code Workspace...")
                launch_vscode()
            elif choice == '5':
                print("Creating Windows Shortcut...")
                create_windows_shortcut()
            elif choice == '6':
                launch_all()
            elif choice == '7':
                print("Exiting ZTO Inc. Launcher...")
                break
            else:
                print("Invalid choice. Please enter a number between 1 and 7.")
    
    elif args.mode == 'auditorium':
        launch_auditorium()
    elif args.mode == 'chat':
        launch_ceo_chat()
    elif args.mode == 'dashboard':
        launch_dashboard()
    elif args.mode == 'all':
        launch_all()

if __name__ == "__main__":
    main()