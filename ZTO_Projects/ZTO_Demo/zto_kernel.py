#!/usr/bin/env python3
"""
Virsaas Virtual Software Inc. - Orchestrator Kernel
Mission: Ship a profitable, million-dollar software product in under 180 days with $0 outside capital.
"""

import os
import sys
import json
import logging
import hashlib
import time
import queue
import threading
import random
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from pathlib import Path
import uuid

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('ZTO-Kernel')

# --- AI Service Abstraction ---

class AIService:
    """Service to handle interactions with LLMs (OpenAI, etc.) with mock fallback."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.client = None
        if self.api_key:
            try:
                import openai
                self.client = openai.OpenAI(api_key=self.api_key)
                logger.info("AI Service initialized with OpenAI")
            except ImportError:
                logger.warning("openai package not installed. Falling back to Mock AI.")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")

    def generate_content(self, system_prompt: str, user_prompt: str, model: str = "gpt-4-1106-preview") -> str:
        """Generate content using LLM or fallback to mock."""
        if self.client:
            try:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.7
                )
                return response.choices[0].message.content
            except Exception as e:
                logger.error(f"AI Generation failed: {e}. Falling back to mock.")
        
        return self._generate_mock_content(system_prompt, user_prompt)

    def _generate_mock_content(self, system_prompt: str, user_prompt: str) -> str:
        """Generate deterministic mock content based on prompts."""
        logger.info("Generating mock content...")
        
        if "Business Plan" in system_prompt or "business plan" in user_prompt.lower():
            return self._mock_business_plan(user_prompt)
        elif "Legal" in system_prompt or "terms of service" in user_prompt.lower():
            return self._mock_legal_docs(user_prompt)
        else:
            return f"Mock AI Response to: {user_prompt[:50]}...\n\n(AI Key missing or errored)"

    def _mock_business_plan(self, prompt: str) -> str:
        return f"""# Generated Business Plan
## Executive Summary
This is a mock business plan generated because no valid OpenAI API key was found.
**Project Concept**: {prompt}

## Market Analysis
- **Target Audience**: Tech-savvy users.
- **Competitors**: Big Corps.

## Financials
- **Projected MRR**: $10,000 in 6 months.
"""

    def _mock_legal_docs(self, prompt: str) -> str:
        return f"""# Terms of Service (Mock)
These are mock terms for project related to: {prompt}

1. **Acceptance**: By using this, you agree to nothing real.
2. **Liability**: None.
"""

# --- Domain Models ---

@dataclass
class AgentRole:
    DEVELOPMENT = "development"
    DESIGN = "design"
    MANAGEMENT = "management"
    ADMINISTRATION = "administration"
    BOARD = "board"
    CEO = "ceo"

@dataclass
class Agent:
    role_id: str
    title: str
    seniority: str
    fte_percentage: int
    primary_tools: List[str]
    personality: str
    role: str
    memory_buffer: List[str] = field(default_factory=list)
    current_task: Optional[str] = None
    status: str = "idle"

    def to_dict(self):
        return asdict(self)

@dataclass
class Message:
    from_agent: str
    to_agent: str
    timestamp: str
    message: str
    message_id: str
    message_type: str = "chat"

# --- Orchestrator ---

class ZTOOrchestrator:
    def __init__(self, project_slug: str = "ZTO_Demo", api_key: Optional[str] = None):
        self.project_slug = project_slug
        # Depending on how this is run, __file__ might ideally be relative to project root
        # For now, we keep it consistent with the existing structure or slightly improved
        self.project_path = Path.cwd() / "user_projects" / project_slug 
        
        # Initialize AI Service
        self.ai_service = AIService(api_key)

        self.agents: Dict[str, Agent] = {}
        self.message_queue = queue.Queue()
        self.communication_log = []
        self.audit_trail = []
        self.company_state = {
            "revenue": 0.0,
            "cash_burn": 0.0,
            "runway_days": 180,
            "phase": "Phase 0 - Idea Intake",
            "days_elapsed": 0,
            "product_status": "concept",
            "team_morale": 100,
            "code_quality": 85,
            "customer_satisfaction": 0
        }
        self.running = False
        self.simulation_speed = 1.0  # Real-time simulation
        
        self._init_agents()
        self._init_audit_system()
        
    def _init_agents(self):
        """Initialize all 25 AI agents with their personalities and roles"""
        
        # Development Team (10 agents)
        self.agents["DEV-001"] = Agent(
            role_id="DEV-001",
            title="Principal Full-Stack Architect",
            seniority="L7",
            fte_percentage=100,
            primary_tools=["VS Enterprise", "VS Code", "C#", "TypeScript", "React", "Node", "Go", "Rust"],
            personality="10× engineer, allergic to meetings. Exceptional at system design but gets frustrated with bureaucracy. Prefers async communication and deep work blocks.",
            role=AgentRole.DEVELOPMENT
        )
        
        self.agents["DEV-002"] = Agent(
            role_id="DEV-002",
            title="Senior Back-End Engineer",
            seniority="L6",
            fte_percentage=100,
            primary_tools=["VS", ".NET 8", "Postgres", "Redis", "gRPC"],
            personality="Writes DDD before breakfast. Domain-driven design enthusiast who believes every problem can be solved with proper architecture. Coffee-powered.",
            role=AgentRole.DEVELOPMENT
        )
        # ... (Abbreviated for brevity, normally we'd list all 25, but ensuring we have key ones for logic)
        self.agents["CEO-001"] = Agent(
            role_id="CEO-001",
            title="Chief Executive Officer",
            seniority="C-Level",
            fte_percentage=100,
            primary_tools=["Email", "Calendar", "Spreadsheets", "Strategy Decks"],
            personality="Visionary leader focused on growth and product-market fit. Decisive but collaborative.",
            role=AgentRole.CEO
        )
        
    def _init_audit_system(self):
        """Initialize the audit trail system"""
        self.audit_trail.append({
            "timestamp": datetime.now().isoformat(),
            "event_type": "SYSTEM_INIT",
            "message": "ZTO Orchestrator Kernel Initialized",
            "agent_id": "KERNEL",
            "hash": hashlib.sha256(b"init").hexdigest()
        })

    def _log_event(self, event_type: str, message: str, agent_id: str = "KERNEL"):
        """Log an event to the audit trail with SHA-256 hash"""
        prev_hash = self.audit_trail[-1]["hash"] if self.audit_trail else ""
        payload = f"{event_type}{message}{agent_id}{prev_hash}".encode()
        event_hash = hashlib.sha256(payload).hexdigest()
        
        self.audit_trail.append({
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "message": message,
            "agent_id": agent_id,
            "hash": event_hash
        })
        logger.info(f"[{agent_id}] {event_type}: {message}")

    def send_message(self, from_agent: str, to_agent: str, message: str, message_type: str = "chat"):
        """Send a message between agents"""
        msg_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        msg_obj = Message(from_agent, to_agent, timestamp, message, msg_id, message_type)
        self.message_queue.put(msg_obj)
        self.communication_log.append(msg_obj)
        
        self._log_event("COMMUNICATION", f"{from_agent} -> {to_agent}: {message[:50]}...", from_agent)

    def process_owner_request(self, request: str):
        """Process a request from the human owner (via CEO)"""
        self._log_event("OWNER_REQUEST", f"Received: {request}", "OWNER")
        
        # CEO processes the request and delegates
        if "CEO-001" in self.agents:
            ceo = self.agents["CEO-001"]
            ceo.memory_buffer.append(f"Owner request: {request}")
        
        # Create project idea document if actionable
        if "idea" in request.lower() or "product" in request.lower():
            # Use AI Service to enrich the idea, then create doc
            enriched_idea = self.ai_service.generate_content(
                system_prompt="You are a startup consultant. Refine this product idea into a clear value proposition.",
                user_prompt=request
            )
            self._create_project_idea(enriched_idea)
            self.send_message("CEO-001", "#internal", f"New project idea received and processed: {request}")
        
        # Update company state
        self.company_state["days_elapsed"] += 1
        self._update_financials()

    def generate_business_plan(self, project_name: str, description: str) -> str:
        """Generate a business plan using the AI service."""
        system_prompt = f"You are an expert business strategist. Write a comprehensive business plan for a startup named '{project_name}'."
        return self.ai_service.generate_content(system_prompt, description)

    def generate_legal_documents(self, project_name: str) -> Dict[str, str]:
        """Generate legal documents."""
        docs = {}
        docs['terms_of_service.md'] = self.ai_service.generate_content(
            "You are a lawyer. Write Terms of Service.", 
            f"Terms of Serevice for {project_name}"
        )
        docs['privacy_policy.md'] = self.ai_service.generate_content(
            "You are a lawyer. Write Privacy Policy.", 
            f"Privacy Policy for {project_name}"
        )
        return docs

    def _create_project_idea(self, idea: str):
        """Create the initial project idea document"""
        # Ensure directory exists
        docs_dir = self.project_path / ".docs"
        docs_dir.mkdir(parents=True, exist_ok=True)
        
        idea_file = docs_dir / "project-idea.md"
        try:
            with open(idea_file, 'w') as f:
                f.write(f"# Project Idea\n\n")
                f.write(f"**Received**: {datetime.now().isoformat()}\n")
                f.write(f"**From**: Company Owner\n\n")
                f.write(f"## Idea Description\n{idea}\n\n")
                f.write(f"## Initial Status\nPhase 0: Idea Intake (Completed)\n")
        except Exception as e:
            logger.error(f"Failed to write project idea file: {e}")

    def _update_financials(self):
        """Update company financial state"""
        burn_rate = 2500  # Fixed daily burn
        self.company_state["cash_burn"] += burn_rate / 24  # Hourly burn update if called frequently
        
        # Revenue logic could go here
        
    def _process_agent_message(self, msg: Message):
        """Process an agent message and determine response"""
        # Simple echo/acknowledgment logic for simulation depth
        if msg.to_agent in self.agents:
            recipient = self.agents[msg.to_agent]
            # Probabilistic response
            if random.random() < 0.2:
                response = f"Acknowledged, {msg.from_agent}. Will look into it."
                # Don't infinitely loop
                if "Acknowledged" not in msg.message:
                     self.send_message(recipient.role_id, msg.from_agent, response)

    def run_simulation_step(self):
        """Run one step of the simulation"""
        # Process messages
        messages_processed = 0
        while not self.message_queue.empty() and messages_processed < 10:
            try:
                msg = self.message_queue.get_nowait()
                self._process_agent_message(msg)
                messages_processed += 1
            except queue.Empty:
                break
        
        # Update simulation time
        if self.running:
            self.company_state["days_elapsed"] += self.simulation_speed / 24  # Simulate hours
            self._update_financials()

    def start_simulation(self):
        self.running = True
        logger.info("Simulation started")

    def stop_simulation(self):
        self.running = False
        logger.info("Simulation stopped")

# Global instance factory
_orchestrator = None

def get_orchestrator(project_slug="ZTO_Demo", api_key=None):
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = ZTOOrchestrator(project_slug, api_key)
    return _orchestrator

if __name__ == "__main__":
    # Test the orchestrator
    zto = get_orchestrator()
    zto.process_owner_request("Create a mobile app for local farmers to sell fresh produce directly to consumers")
    print("ZTO Kernel initialized successfully!")
    print(f"Company State: {zto.company_state}")