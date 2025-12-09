#!/usr/bin/env python3
"""
Virsaas Virtual Software Inc. - 2.5D Auditorium Simulation
Visual representation of the virtual office with real-time agent activities
"""

import pygame
import pygame_gui
import sys
import os
import json
import math
import random
from datetime import datetime
from pathlib import Path
import threading
import queue
from typing import Dict, List, Tuple, Optional
import logging

# Add parent directory to path to import kernel
sys.path.append(str(Path(__file__).parent.parent.parent))
from zto_kernel import get_orchestrator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('ZTO-Auditorium')

# Constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60
TILE_SIZE = 64
ISOMETRIC_WIDTH = 128
ISOMETRIC_HEIGHT = 64

# Colors
COLORS = {
    'floor': (45, 45, 48),
    'wall': (139, 69, 19),
    'desk': (101, 67, 33),
    'chair': (68, 68, 68),
    'computer': (0, 255, 0),
    'text': (255, 255, 255),
    'highlight': (255, 255, 0),
    'green': (0, 255, 0),
    'red': (255, 0, 0),
    'yellow': (255, 255, 0),
    'blue': (0, 150, 255)
}

class AgentSprite:
    """Represents an AI agent in the virtual office"""
    
    def __init__(self, agent_id: str, position: Tuple[int, int], color: Tuple[int, int, int]):
        self.agent_id = agent_id
        self.position = position
        self.color = color
        self.target_position = position
        self.animation_offset = (0, 0)
        self.animation_time = 0
        self.speech_bubble = None
        self.speech_timer = 0
        self.status_color = COLORS['green']  # Based on CI status
        self.walking_direction = 0  # 0-7 for 8 directions
        
    def update(self, dt: float):
        """Update agent animation and position"""
        self.animation_time += dt
        
        # Simple walking animation
        if self.position != self.target_position:
            dx = self.target_position[0] - self.position[0]
            dy = self.target_position[1] - self.position[1]
            
            # Determine walking direction
            if abs(dx) > abs(dy):
                self.walking_direction = 0 if dx > 0 else 4  # East or West
            else:
                self.walking_direction = 2 if dy > 0 else 6  # South or North
            
            # Move towards target
            speed = 2 * dt * 60  # 60 FPS base
            if abs(dx) > speed:
                self.position = (self.position[0] + speed * (1 if dx > 0 else -1), self.position[1])
            elif abs(dy) > speed:
                self.position = (self.position[0], self.position[1] + speed * (1 if dy > 0 else -1))
            else:
                self.position = self.target_position
        
        # Update speech bubble
        if self.speech_bubble and self.speech_timer > 0:
            self.speech_timer -= dt
            if self.speech_timer <= 0:
                self.speech_bubble = None
    
    def set_speech(self, text: str, duration: float = 3.0):
        """Set speech bubble text"""
        self.speech_bubble = text[:30] + "..." if len(text) > 30 else text
        self.speech_timer = duration
    
    def set_status(self, status: str):
        """Set status color based on CI/build status"""
        if status == "success":
            self.status_color = COLORS['green']
        elif status == "failure":
            self.status_color = COLORS['red']
        elif status == "pending":
            self.status_color = COLORS['yellow']
        else:
            self.status_color = COLORS['blue']

class ZTOAuditorium:
    """Main auditorium simulation class"""
    
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Virsaas Virtual Software Inc. - Live Floor Plan")
        
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Initialize UI manager
        self.ui_manager = pygame_gui.UIManager((SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # Get orchestrator
        self.orchestrator = get_orchestrator()
        
        # Agent sprites
        self.agents: Dict[str, AgentSprite] = {}
        self._create_agent_sprites()
        
        # Office layout
        self.rooms = self._create_office_layout()
        
        # Camera
        self.camera_x = 0
        self.camera_y = 0
        self.zoom = 1.0
        
        # Animation
        self.frame_count = 0
        
        # Server status (mock data)
        self.server_status = {
            'cpu_usage': 0,
            'memory_usage': 0,
            'network_io': 0
        }
        
        # LED ticker
        self.ticker_text = "Virsaas Virtual Software Inc. - Revenue: $0 - Runway: 180 days"
        self.ticker_offset = 0
        
        logger.info("Auditorium initialized")
    
    def _create_agent_sprites(self):
        """Create agent sprites with positions and colors"""
        agent_colors = [
            (255, 100, 100), (100, 255, 100), (100, 100, 255),
            (255, 255, 100), (255, 100, 255), (100, 255, 255),
            (200, 100, 50), (50, 200, 100), (100, 50, 200),
            (200, 200, 50), (200, 50, 200), (50, 200, 200)
        ]
        
        # Position agents in their respective areas
        positions = {
            # North - Boardroom
            'CEO-001': (600, 100),
            'BOARD-001': (500, 100),
            'BOARD-002': (550, 100),
            'BOARD-003': (650, 100),
            'BOARD-004': (700, 100),
            
            # North-East - Executive row
            'MGT-001': (800, 150),
            'ADMIN-002': (850, 150),
            'ADMIN-001': (900, 150),
            'ADMIN-003': (950, 150),
            
            # East - DevOps & Cloud
            'DEV-005': (1000, 250),
            'DEV-006': (1050, 250),
            
            # South-East - QA & Security
            'DEV-010': (1000, 400),
            'DEV-009': (1050, 400),
            
            # South - Back-End island
            'DEV-002': (600, 500),
            'DEV-008': (650, 500),
            'DEV-007': (700, 500),
            
            # South-West - Front-End & Mobile
            'DEV-003': (300, 500),
            'DEV-004': (350, 500),
            
            # West - UX/Design studio
            'UX-001': (150, 250),
            'UX-002': (200, 250),
            'DOC-001': (250, 250),
            
            # North-West - PMO
            'PM-001': (150, 150),
            'PM-002': (200, 150),
            
            # Center - Agile Pit
            'DEV-001': (500, 300),
        }
        
        color_idx = 0
        for agent_id, agent in self.orchestrator.agents.items():
            if agent_id in positions:
                color = agent_colors[color_idx % len(agent_colors)]
                self.agents[agent_id] = AgentSprite(agent_id, positions[agent_id], color)
                color_idx += 1
    
    def _create_office_layout(self):
        """Create the office room layout"""
        return {
            'north_wall': {'x': 0, 'y': 0, 'width': 1200, 'height': 50},
            'south_wall': {'x': 0, 'y': 750, 'width': 1200, 'height': 50},
            'east_wall': {'x': 1150, 'y': 0, 'width': 50, 'height': 800},
            'west_wall': {'x': 0, 'y': 0, 'width': 50, 'height': 800},
            'boardroom': {'x': 400, 'y': 50, 'width': 400, 'height': 150},
            'executive_row': {'x': 750, 'y': 100, 'width': 300, 'height': 100},
            'devops_corner': {'x': 950, 'y': 200, 'width': 200, 'height': 150},
            'qa_corner': {'x': 950, 'y': 350, 'width': 200, 'height': 150},
            'backend_island': {'x': 500, 'y': 450, 'width': 300, 'height': 150},
            'frontend_island': {'x': 200, 'y': 450, 'width': 300, 'height': 150},
            'design_studio': {'x': 50, 'y': 200, 'width': 300, 'height': 150},
            'pmo': {'x': 50, 'y': 100, 'width': 300, 'height': 100},
            'agile_pit': {'x': 400, 'y': 250, 'width': 400, 'height': 200}
        }
    
    def world_to_screen(self, world_x: int, world_y: int) -> Tuple[int, int]:
        """Convert world coordinates to screen coordinates"""
        screen_x = (world_x - self.camera_x) * self.zoom + SCREEN_WIDTH // 2
        screen_y = (world_y - self.camera_y) * self.zoom + SCREEN_HEIGHT // 2
        return int(screen_x), int(screen_y)
    
    def draw_isometric_tile(self, x: int, y: int, color: Tuple[int, int, int], size: int = 32):
        """Draw an isometric tile"""
        points = [
            (x, y - size // 2),
            (x + size // 2, y),
            (x, y + size // 2),
            (x - size // 2, y)
        ]
        pygame.draw.polygon(self.screen, color, points)
        pygame.draw.polygon(self.screen, (0, 0, 0), points, 1)
    
    def draw_desk(self, x: int, y: int, agent: Optional[AgentSprite] = None):
        """Draw a desk with optional agent"""
        # Desk
        desk_rect = pygame.Rect(x - 30, y - 15, 60, 30)
        pygame.draw.rect(self.screen, COLORS['desk'], desk_rect)
        pygame.draw.rect(self.screen, (0, 0, 0), desk_rect, 1)
        
        # Computer monitor
        monitor_rect = pygame.Rect(x - 10, y - 25, 20, 15)
        pygame.draw.rect(self.screen, COLORS['computer'], monitor_rect)
        
        # Agent
        if agent:
            agent_x = x + 20
            agent_y = y - 10
            
            # Draw agent as a circle with color
            pygame.draw.circle(self.screen, agent.color, (agent_x, agent_y), 8)
            pygame.draw.circle(self.screen, (0, 0, 0), (agent_x, agent_y), 8, 1)
            
            # Status indicator
            status_y = agent_y - 15
            pygame.draw.circle(self.screen, agent.status_color, (agent_x, status_y), 3)
            
            # Speech bubble
            if agent.speech_bubble:
                self.draw_speech_bubble(agent_x, agent_y - 20, agent.speech_bubble)
    
    def draw_speech_bubble(self, x: int, y: int, text: str):
        """Draw a speech bubble with text"""
        font = pygame.font.Font(None, 12)
        text_surface = font.render(text, True, (0, 0, 0))
        
        # Bubble background
        padding = 5
        bubble_rect = pygame.Rect(
            x - text_surface.get_width() // 2 - padding,
            y - text_surface.get_height() - padding * 2,
            text_surface.get_width() + padding * 2,
            text_surface.get_height() + padding * 2
        )
        
        pygame.draw.rect(self.screen, (255, 255, 255), bubble_rect)
        pygame.draw.rect(self.screen, (0, 0, 0), bubble_rect, 1)
        
        # Text
        self.screen.blit(text_surface, (bubble_rect.x + padding, bubble_rect.y + padding))
    
    def draw_server_rack(self, x: int, y: int):
        """Draw a server rack with real-time status"""
        # Rack frame
        rack_rect = pygame.Rect(x, y, 60, 120)
        pygame.draw.rect(self.screen, (40, 40, 40), rack_rect)
        pygame.draw.rect(self.screen, (100, 100, 100), rack_rect, 2)
        
        # Server units with LED indicators
        for i in range(8):
            unit_y = y + 5 + i * 14
            unit_rect = pygame.Rect(x + 5, unit_y, 50, 10)
            
            # CPU usage simulation
            cpu_percent = (self.server_status['cpu_usage'] + i * 10) % 100
            intensity = int(cpu_percent * 2.55)
            
            pygame.draw.rect(self.screen, (0, intensity, 0), unit_rect)
            pygame.draw.rect(self.screen, (100, 100, 100), unit_rect, 1)
    
    def draw_led_ticker(self):
        """Draw the LED ticker showing company status"""
        ticker_height = 30
        ticker_rect = pygame.Rect(0, SCREEN_HEIGHT - ticker_height, SCREEN_WIDTH, ticker_height)
        pygame.draw.rect(self.screen, (0, 0, 0), ticker_rect)
        
        # Update ticker text
        state = self.orchestrator.company_state
        self.ticker_text = f"ZTO Inc. - Revenue: ${state['revenue']:.0f} - Runway: {state['runway_days']:.0f} days - Phase: {state['phase']} - Team Morale: {state['team_morale']}%"
        
        # Draw scrolling text
        font = pygame.font.Font(None, 20)
        text_surface = font.render(self.ticker_text, True, (0, 255, 0))
        
        self.ticker_offset -= 2
        if self.ticker_offset < -text_surface.get_width():
            self.ticker_offset = SCREEN_WIDTH
        
        self.screen.blit(text_surface, (self.ticker_offset, SCREEN_HEIGHT - ticker_height + 5))
    
    def draw_office_layout(self):
        """Draw the main office layout"""
        # Floor
        floor_rect = pygame.Rect(50, 50, SCREEN_WIDTH - 100, SCREEN_HEIGHT - 100)
        pygame.draw.rect(self.screen, COLORS['floor'], floor_rect)
        
        # Rooms
        for room_name, room_data in self.rooms.items():
            room_rect = pygame.Rect(room_data['x'], room_data['y'], room_data['width'], room_data['height'])
            
            if 'boardroom' in room_name:
                color = (60, 60, 80)
            elif 'executive' in room_name:
                color = (80, 60, 60)
            elif 'devops' in room_name or 'qa' in room_name:
                color = (60, 80, 60)
            elif 'backend' in room_name or 'frontend' in room_name:
                color = (80, 80, 60)
            elif 'design' in room_name:
                color = (80, 60, 80)
            elif 'pmo' in room_name:
                color = (60, 80, 80)
            else:
                color = (70, 70, 70)
            
            pygame.draw.rect(self.screen, color, room_rect)
            pygame.draw.rect(self.screen, (100, 100, 100), room_rect, 2)
            
            # Room label
            font = pygame.font.Font(None, 16)
            label = font.render(room_name.replace('_', ' ').title(), True, COLORS['text'])
            label_x = room_data['x'] + room_data['width'] // 2 - label.get_width() // 2
            label_y = room_data['y'] + 5
            self.screen.blit(label, (label_x, label_y))
    
    def draw_agents(self):
        """Draw all agent sprites"""
        for agent in self.agents.values():
            # Find desk position for this agent
            desk_x, desk_y = agent.position
            self.draw_desk(desk_x, desk_y, agent)
    
    def update_simulation(self, dt: float):
        """Update simulation state"""
        self.frame_count += 1
        
        # Update server status (mock data)
        self.server_status['cpu_usage'] = (math.sin(self.frame_count * 0.1) * 30 + 50 + random.randint(-10, 10)) % 100
        self.server_status['memory_usage'] = (self.server_status['cpu_usage'] + random.randint(-20, 20)) % 100
        
        # Update agents
        for agent in self.agents.values():
            agent.update(dt)
            
            # Random movement simulation
            if random.random() < 0.001:  # 0.1% chance per frame
                # Move to a random nearby position
                dx = random.randint(-100, 100)
                dy = random.randint(-50, 50)
                agent.target_position = (
                    max(100, min(1100, agent.position[0] + dx)),
                    max(100, min(700, agent.position[1] + dy))
                )
        
        # Update from orchestrator messages
        self._update_from_orchestrator()
    
    def _update_from_orchestrator(self):
        """Update simulation based on orchestrator state"""
        # Update agent statuses based on orchestrator state
        status = self.orchestrator.get_agent_status()
        
        for agent_id, agent_data in status['agents'].items():
            if agent_id in self.agents:
                agent_sprite = self.agents[agent_id]
                
                # Update status based on agent state
                if agent_data.get('status') == 'working':
                    agent_sprite.set_status('success')
                elif agent_data.get('status') == 'idle':
                    agent_sprite.set_status('pending')
                else:
                    agent_sprite.set_status('failure')
                
                # Add speech bubbles for recent messages
                if random.random() < 0.01:  # 1% chance per frame
                    messages = [
                        "Working on the next sprint...",
                        "Code review completed",
                        "Testing in progress",
                        "Meeting with the team",
                        "Deploying to staging"
                    ]
                    agent_sprite.set_speech(random.choice(messages))
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.VIDEORESIZE:
                self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                self.ui_manager.set_window_resolution((event.w, event.h))
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    # Toggle simulation speed
                    pass
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:  # Mouse wheel up
                    self.zoom = min(2.0, self.zoom * 1.1)
                elif event.button == 5:  # Mouse wheel down
                    self.zoom = max(0.5, self.zoom / 1.1)
            
            self.ui_manager.process_events(event)
    
    def draw(self):
        """Main draw function"""
        self.screen.fill((20, 20, 20))
        
        # Draw office layout
        self.draw_office_layout()
        
        # Draw server racks in DevOps corner
        if 'devops_corner' in self.rooms:
            rack_x = self.rooms['devops_corner']['x'] + 20
            rack_y = self.rooms['devops_corner']['y'] + 20
            self.draw_server_rack(rack_x, rack_y)
        
        # Draw agents
        self.draw_agents()
        
        # Draw LED ticker
        self.draw_led_ticker()
        
        # Draw UI elements
        self.ui_manager.draw_ui(self.screen)
        
        # Draw info overlay
        self.draw_info_overlay()
        
        pygame.display.flip()
    
    def draw_info_overlay(self):
        """Draw information overlay"""
        font = pygame.font.Font(None, 16)
        
        # Company status
        state = self.orchestrator.company_state
        info_lines = [
            f"Day: {state['days_elapsed']:.1f}",
            f"Phase: {state['phase']}",
            f"Revenue: ${state['revenue']:.0f}",
            f"Agents: {len(self.agents)}",
            f"Zoom: {self.zoom:.1f}x"
        ]
        
        for i, line in enumerate(info_lines):
            text = font.render(line, True, COLORS['text'])
            self.screen.blit(text, (10, 10 + i * 20))
    
    def run(self):
        """Main game loop"""
        logger.info("Starting auditorium simulation")
        
        # Start orchestrator simulation
        self.orchestrator.start_simulation()
        
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0  # Delta time in seconds
            
            # Handle events
            self.handle_events()
            
            # Update simulation
            self.update_simulation(dt)
            self.ui_manager.update(dt)
            
            # Draw everything
            self.draw()
            
            # Run orchestrator simulation step
            self.orchestrator.run_simulation_step()
        
        # Cleanup
        self.orchestrator.stop_simulation()
        pygame.quit()
        logger.info("Auditorium simulation stopped")

def main():
    """Main entry point"""
    try:
        auditorium = ZTOAuditorium()
        auditorium.run()
    except Exception as e:
        logger.error(f"Error in auditorium: {e}")
        pygame.quit()
        sys.exit(1)

if __name__ == "__main__":
    main()