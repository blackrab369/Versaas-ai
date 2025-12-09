#!/usr/bin/env python3
"""
Virsaas Virtual Software Inc. - Quick Demo
Demonstrates the core functionality of the virtual company system
"""

import sys
import time
import random
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from zto_kernel import get_orchestrator

def run_demo():
    """Run a quick demonstration of ZTO Inc."""
    print("🚀 Virsaas Virtual Software Inc. - Demo")
    print("=" * 60)
    print()
    
    # Initialize orchestrator
    print("Initializing virtual company...")
    orchestrator = get_orchestrator()
    
    # Show initial state
    print("\n📊 Initial Company State:")
    state = orchestrator.company_state
    print(f"  • Revenue: ${state['revenue']:.0f}")
    print(f"  • Runway: {state['runway_days']:.0f} days")
    print(f"  • Phase: {state['phase']}")
    print(f"  • Team Size: {len(orchestrator.agents)} AI agents")
    
    # Show team composition
    print(f"\n👥 Team Composition:")
    roles = {}
    for agent in orchestrator.agents.values():
        role = agent.role.value.title()
        roles[role] = roles.get(role, 0) + 1
    
    for role, count in roles.items():
        print(f"  • {role}: {count} agents")
    
    # Simulate owner interaction
    print(f"\n💬 CEO Chat Simulation:")
    print("You: I want to build a mobile app for local farmers to sell fresh produce directly to consumers")
    
    orchestrator.process_owner_request("I want to build a mobile app for local farmers to sell fresh produce directly to consumers")
    
    # Show some sample agent messages
    print(f"\n📨 Sample Agent Communications:")
    sample_messages = [
        "CEO-001 -> #internal: New project idea received - mobile marketplace for local farmers",
        "UX-001 -> CEO-001: Starting user interviews tomorrow. Will have persona profiles ready by end of week.",
        "DEV-001 -> CEO-001: I'll review the architecture requirements and provide recommendations within 24 hours.",
        "PM-001 -> #internal: Initial product backlog created. 47 user stories identified for MVP.",
        "ADMIN-002 -> CEO-001: Financial projections complete. Break-even estimated at day 67."
    ]
    
    for msg in sample_messages:
        print(f"  • {msg}")
        time.sleep(0.5)
    
    # Simulate some time passing
    print(f"\n⏱️  Simulating 7 days of development...")
    for day in range(1, 8):
        orchestrator.company_state['days_elapsed'] += 1
        orchestrator._update_financials()
        
        if day % 2 == 0:
            # Simulate some agent activity
            agent_id = random.choice(list(orchestrator.agents.keys()))
            orchestrator.agents[agent_id].status = "working"
            orchestrator.agents[agent_id].current_task = f"Working on sprint tasks (Day {day})"
    
    # Show updated state
    print(f"\n📊 Updated Company State (Day 7):")
    state = orchestrator.company_state
    print(f"  • Revenue: ${state['revenue']:.0f}")
    print(f"  • Cash Burn: ${state['cash_burn']:.0f}")
    print(f"  • Runway: {state['runway_days']:.0f} days")
    print(f"  • Phase: {state['phase']}")
    
    # Show some working agents
    print(f"\n🔧 Active Agents:")
    working_agents = [a for a in orchestrator.agents.values() if a.status == 'working']
    for agent in working_agents[:5]:
        print(f"  • {agent.role_id}: {agent.current_task}")
    
    # Generate dashboard
    print(f"\n📈 Generating Financial Dashboard...")
    try:
        from .finance.dashboard_generator import FinancialDashboard
        dashboard = FinancialDashboard()
        dashboard_path = dashboard.generate_dashboard()
        print(f"  • Dashboard saved to: {dashboard_path}")
        
        # Generate executive summary
        summary = dashboard.generate_executive_summary()
        print(f"  • Executive summary generated")
        
    except Exception as e:
        print(f"  • Dashboard generation failed: {e}")
    
    print(f"\n✅ Demo Complete!")
    print(f"\nNext Steps:")
    print(f"1. Run 'python launch_zto.py' to start the full simulation")
    print(f"2. Use the interactive menu to explore different components")
    print(f"3. Chat with the CEO to provide your product ideas")
    print(f"4. Watch the 2.5D auditorium simulation show the team in action")
    
    print(f"\n🎯 Mission: Help ZTO Inc. reach $1M revenue in 180 days!")

if __name__ == "__main__":
    run_demo()