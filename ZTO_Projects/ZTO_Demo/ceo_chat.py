#!/usr/bin/env python3
"""
Virsaas Virtual Software Inc. - CEO Chat Interface
Human owner communication interface with the virtual CEO
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
import json
from datetime import datetime
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))
from zto_kernel import get_orchestrator

class CEOChatInterface:
    """CEO chat interface for human owner communication"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("ZTO Inc. - CEO Chat Interface")
        self.root.geometry("800x600")
        
        # Get orchestrator
        self.orchestrator = get_orchestrator()
        
        # Message queue for async updates
        self.message_queue = []
        self.running = True
        
        self.setup_ui()
        self.start_update_thread()
        
        # Welcome message
        self.display_message("System", "Welcome to Virsaas Virtual Software Inc. CEO Chat Interface", "system")
        self.display_message("CEO-001", "Hello! I'm the CEO of ZTO Inc. Please share your software product idea, and I'll coordinate our virtual team to bring it to life.", "agent")
    
    def setup_ui(self):
        """Setup the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Chat display area
        self.chat_display = scrolledtext.ScrolledText(
            main_frame,
            wrap=tk.WORD,
            width=80,
            height=25,
            font=('Arial', 10)
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Configure text tags for different message types
        self.chat_display.tag_configure("system", foreground="gray", font=('Arial', 9, 'italic'))
        self.chat_display.tag_configure("user", foreground="blue", font=('Arial', 10, 'bold'))
        self.chat_display.tag_configure("agent", foreground="green", font=('Arial', 10))
        self.chat_display.tag_configure("timestamp", foreground="gray", font=('Arial', 8))
        
        # Make chat display read-only
        self.chat_display.config(state=tk.DISABLED)
        
        # Input frame
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Message input
        self.message_input = tk.Text(
            input_frame,
            height=3,
            width=60,
            font=('Arial', 10)
        )
        self.message_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        # Send button
        self.send_button = ttk.Button(
            input_frame,
            text="Send Message",
            command=self.send_message,
            width=15
        )
        self.send_button.pack(side=tk.RIGHT)
        
        # Bind Enter key to send message
        self.message_input.bind('<Return>', lambda e: self.send_message())
        self.message_input.bind('<Shift-Return>', lambda e: None)  # Allow Shift+Enter for new line
        
        # Status frame
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X)
        
        # Company status
        self.status_label = ttk.Label(
            status_frame,
            text="Company Status: Initializing...",
            font=('Arial', 9)
        )
        self.status_label.pack(side=tk.LEFT)
        
        # Phase indicator
        self.phase_label = ttk.Label(
            status_frame,
            text="Phase: Idea Intake",
            font=('Arial', 9, 'bold')
        )
        self.phase_label.pack(side=tk.RIGHT)
        
        # Menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Save Chat Log", command=self.save_chat_log)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Company Dashboard", command=self.open_dashboard)
        tools_menu.add_command(label="View Project Files", command=self.open_project_files)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="Commands", command=self.show_commands)
    
    def display_message(self, sender: str, message: str, msg_type: str = "agent"):
        """Display a message in the chat window"""
        self.chat_display.config(state=tk.NORMAL)
        
        # Timestamp
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.chat_display.insert(tk.END, f"[{timestamp}] ", "timestamp")
        
        # Sender
        self.chat_display.insert(tk.END, f"{sender}: ", msg_type)
        
        # Message
        self.chat_display.insert(tk.END, f"{message}\n")
        
        # Auto-scroll to bottom
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
    
    def send_message(self):
        """Send a message to the CEO"""
        message = self.message_input.get(1.0, tk.END).strip()
        if not message:
            return
        
        # Clear input
        self.message_input.delete(1.0, tk.END)
        
        # Display user message
        self.display_message("You", message, "user")
        
        # Process message through orchestrator
        try:
            self.orchestrator.process_owner_request(message)
            
            # Get CEO response
            ceo_response = self.generate_ceo_response(message)
            
            # Display CEO response after a short delay
            self.root.after(1000, lambda: self.display_message("CEO-001", ceo_response, "agent"))
            
            # Update status
            self.update_status()
            
        except Exception as e:
            self.display_message("System", f"Error processing message: {str(e)}", "system")
    
    def generate_ceo_response(self, message: str) -> str:
        """Generate CEO response based on message content"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['idea', 'product', 'app', 'software']):
            return ("Excellent idea! I've documented this in our project backlog. I'll coordinate with our UX researcher to conduct user interviews and our architect to design the system architecture. "
                   "Our discovery phase will begin immediately, focusing on market validation and technical feasibility.")
        
        elif any(word in message_lower for word in ['status', 'progress', 'update']):
            state = self.orchestrator.company_state
            return (f"Current status: We're in {state['phase']}, Day {state['days_elapsed']:.0f}. "
                   f"Revenue: ${state['revenue']:.0f}, Runway: {state['runway_days']:.0f} days. "
                   f"Team morale is at {state['team_morale']}%. All systems operational.")
        
        elif any(word in message_lower for word in ['team', 'employees', 'agents']):
            agent_count = len(self.orchestrator.agents)
            dev_count = len([a for a in self.orchestrator.agents.values() if a.role_id.startswith('DEV')])
            return (f"Our virtual team consists of {agent_count} AI agents, including {dev_count} developers, "
                   f"2 designers, 2 project managers, and 4 board members. Each agent has specialized skills "
                   f"and is currently working on their assigned tasks.")
        
        elif any(word in message_lower for word in ['help', 'commands', 'assist']):
            return ("I can help you with: sharing product ideas, checking company status, reviewing team composition, "
                   "monitoring financial metrics, and tracking project progress. Just tell me what you'd like to know or do!")
        
        elif any(word in message_lower for word in ['shutdown', 'stop', 'quit']):
            return ("I'll initiate the company shutdown sequence. All agents will complete their current tasks and save their work. "
                   "Final financial reports and project documentation will be generated.")
        
        else:
            return ("Thank you for your input. I've logged this in our communication system and will ensure the relevant team members are notified. "
                   f"Is there anything specific about our product development you'd like to discuss?")
    
    def update_status(self):
        """Update company status display"""
        state = self.orchestrator.company_state
        self.status_label.config(
            text=f"Revenue: ${state['revenue']:.0f} | Runway: {state['runway_days']:.0f} days | Agents: {len(self.orchestrator.agents)}"
        )
        self.phase_label.config(text=f"Phase: {state['phase']}")
    
    def start_update_thread(self):
        """Start background update thread"""
        def update_loop():
            while self.running:
                try:
                    # Update status every 5 seconds
                    time.sleep(5)
                    self.root.after(0, self.update_status)
                except Exception as e:
                    print(f"Update thread error: {e}")
        
        thread = threading.Thread(target=update_loop, daemon=True)
        thread.start()
    
    def save_chat_log(self):
        """Save chat log to file"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file = Path(f".comm/chat_log_{timestamp}.txt")
            log_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(log_file, 'w') as f:
                f.write("ZTO Inc. - CEO Chat Log\n")
                f.write(f"Generated: {datetime.now().isoformat()}\n")
                f.write("=" * 50 + "\n\n")
                f.write(self.chat_display.get(1.0, tk.END))
            
            messagebox.showinfo("Success", f"Chat log saved to {log_file}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save chat log: {str(e)}")
    
    def open_dashboard(self):
        """Open financial dashboard"""
        try:
            import webbrowser
            dashboard_path = Path(".finance/dashboard.html").absolute()
            if dashboard_path.exists():
                webbrowser.open(f"file://{dashboard_path}")
            else:
                messagebox.showinfo("Dashboard", "Dashboard not yet generated. It will be created as the company progresses.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open dashboard: {str(e)}")
    
    def open_project_files(self):
        """Open project files directory"""
        try:
            import subprocess
            import platform
            
            project_path = Path(".").absolute()
            if platform.system() == "Windows":
                subprocess.run(['explorer', str(project_path)])
            elif platform.system() == "Darwin":
                subprocess.run(['open', str(project_path)])
            else:
                subprocess.run(['xdg-open', str(project_path)])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open project files: {str(e)}")
    
    def show_about(self):
        """Show about dialog"""
        about_text = """Virsaas Virtual Software Inc.
        
A fully autonomous virtual software company with 25 AI employees working to build a profitable product in 180 days with $0 outside capital.

Features:
• 25 AI agents with unique personalities
• Real-time 2.5D office simulation
• Complete development lifecycle automation
• Financial tracking and dashboard
• CEO chat interface for owner communication

Version 1.0"""
        messagebox.showinfo("About ZTO Inc.", about_text)
    
    def show_commands(self):
        """Show available commands"""
        commands_text = """Available Commands:

• Share your product idea (e.g., "I want to build a mobile app for X")
• Check status (e.g., "What's our current status?")
• View team info (e.g., "Tell me about our team")
• Get help (e.g., "Help" or "What can I do?")
• Shutdown (e.g., "Shutdown the company")

The CEO will interpret your messages and coordinate the virtual team accordingly."""
        messagebox.showinfo("Commands", commands_text)
    
    def on_closing(self):
        """Handle window closing"""
        if messagebox.askokcancel("Quit", "Do you want to quit the CEO chat interface?"):
            self.running = False
            self.root.quit()
    
    def run(self):
        """Run the chat interface"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

def main():
    """Main entry point for CEO chat"""
    chat = CEOChatInterface()
    chat.run()

if __name__ == "__main__":
    main()