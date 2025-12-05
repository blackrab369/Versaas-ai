#!/usr/bin/env python3
"""
Zero-to-One Virtual Software Inc. - Financial Dashboard Generator
Creates real-time financial dashboard with company metrics and progress tracking
"""

import json
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from zto_kernel import get_orchestrator

class FinancialDashboard:
    """Generate comprehensive financial dashboard"""
    
    def __init__(self):
        self.orchestrator = get_orchestrator()
        self.dashboard_path = Path(".finance/dashboard.html")
        self.data_path = Path(".finance/data")
        self.data_path.mkdir(parents=True, exist_ok=True)
        
    def generate_dashboard(self):
        """Generate the complete financial dashboard"""
        state = self.orchestrator.company_state
        
        # Create subplots
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=[
                'Revenue Growth', 'Cash Flow & Runway',
                'Project Progress', 'Team Performance',
                'Development Metrics', 'Market Position'
            ],
            specs=[
                [{"secondary_y": False}, {"secondary_y": True}],
                [{"type": "indicator"}, {"type": "bar"}],
                [{"type": "scatter"}, {"type": "pie"}]
            ]
        )
        
        # 1. Revenue Growth Chart
        self._add_revenue_chart(fig, state)
        
        # 2. Cash Flow & Runway
        self._add_cashflow_chart(fig, state)
        
        # 3. Project Progress Indicator
        self._add_progress_indicator(fig, state)
        
        # 4. Team Performance
        self._add_team_performance(fig, state)
        
        # 5. Development Metrics
        self._add_dev_metrics(fig, state)
        
        # 6. Market Position
        self._add_market_metrics(fig, state)
        
        # Update layout
        fig.update_layout(
            title={
                'text': f'ZTO Inc. Financial Dashboard - Day {state["days_elapsed"]:.0f}',
                'x': 0.5,
                'font': {'size': 24, 'color': '#2c3e50'}
            },
            height=800,
            showlegend=True,
            template='plotly_white',
            font=dict(family="Arial, sans-serif", size=12),
            margin=dict(t=80, b=50, l=50, r=50)
        )
        
        # Save dashboard
        fig.write_html(self.dashboard_path)
        
        # Generate summary data
        self._generate_summary_data(state)
        
        return str(self.dashboard_path)
    
    def _add_revenue_chart(self, fig, state):
        """Add revenue growth chart"""
        # Generate sample revenue data
        days = list(range(0, int(state['days_elapsed']) + 1))
        revenue = [min(1000000, (day ** 2) * 100) for day in days]
        
        fig.add_trace(
            go.Scatter(
                x=days,
                y=revenue,
                mode='lines+markers',
                name='Revenue ($)',
                line=dict(color='#27ae60', width=3),
                marker=dict(size=6),
                hovertemplate='Day %{x}<br>Revenue: $%{y:,.0f}<extra></extra>'
            ),
            row=1, col=1
        )
        
        # Add milestone markers
        milestones = [
            (30, 'MVP Launch', '#e74c3c'),
            (60, 'Beta Release', '#f39c12'),
            (90, 'Public Launch', '#3498db'),
            (180, '$1M Target', '#9b59b6')
        ]
        
        for day, label, color in milestones:
            if day <= len(days):
                fig.add_vline(
                    x=day,
                    line=dict(color=color, width=2, dash='dash'),
                    annotation_text=label,
                    annotation_position="top",
                    row=1, col=1
                )
    
    def _add_cashflow_chart(self, fig, state):
        """Add cash flow and runway chart"""
        days = list(range(0, 181))  # Full 180 days
        burn_rate = 2500  # Daily burn rate
        
        # Cash flow simulation
        expenses = [burn_rate * day for day in days]
        revenue = [min(1000000, (day ** 2.5) * 50) if day > 30 else 0 for day in days]
        net_cash = [rev - exp for rev, exp in zip(revenue, expenses)]
        
        fig.add_trace(
            go.Scatter(
                x=days,
                y=expenses,
                mode='lines',
                name='Expenses',
                line=dict(color='#e74c3c', width=2),
                fill='tonexty',
                hovertemplate='Day %{x}<br>Expenses: $%{y:,.0f}<extra></extra>'
            ),
            row=1, col=2
        )
        
        fig.add_trace(
            go.Scatter(
                x=days,
                y=revenue,
                mode='lines',
                name='Revenue',
                line=dict(color='#27ae60', width=2),
                fill='tozeroy',
                hovertemplate='Day %{x}<br>Revenue: $%{y:,.0f}<extra></extra>'
            ),
            row=1, col=2
        )
        
        # Add break-even point
        for i, net in enumerate(net_cash):
            if net > 0:
                fig.add_vline(
                    x=i,
                    line=dict(color='#f39c12', width=3, dash='dot'),
                    annotation_text="Break-even",
                    annotation_position="top",
                    row=1, col=2
                )
                break
    
    def _add_progress_indicator(self, fig, state):
        """Add project progress indicator"""
        progress = min(100, (state['days_elapsed'] / 180) * 100)
        
        fig.add_trace(
            go.Indicator(
                mode="gauge+number+delta",
                value=progress,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Project Progress (%)"},
                delta={'reference': 0},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "#3498db"},
                    'steps': [
                        {'range': [0, 25], 'color': "#ecf0f1"},
                        {'range': [25, 50], 'color': "#d5dbdb"},
                        {'range': [50, 75], 'color': "#b8c6c6"},
                        {'range': [75, 100], 'color': "#9b59b6"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 90
                    }
                }
            ),
            row=2, col=1
        )
    
    def _add_team_performance(self, fig, state):
        """Add team performance metrics"""
        agents = self.orchestrator.agents
        
        # Count agents by role
        role_counts = {}
        for agent in agents.values():
            role = agent.role.value.title()
            role_counts[role] = role_counts.get(role, 0) + 1
        
        roles = list(role_counts.keys())
        counts = list(role_counts.values())
        
        fig.add_trace(
            go.Bar(
                x=roles,
                y=counts,
                name='Team Composition',
                marker_color=['#3498db', '#e74c3c', '#f39c12', '#27ae60', '#9b59b6'],
                hovertemplate='%{x}: %{y} agents<extra></extra>'
            ),
            row=2, col=2
        )
    
    def _add_dev_metrics(self, fig, state):
        """Add development metrics"""
        days = list(range(0, int(state['days_elapsed']) + 1))
        
        # Simulate code quality over time
        code_quality = [max(50, 95 - day * 0.1 + random.randint(-5, 5)) for day in days]
        
        # Simulate bugs found and fixed
        bugs_found = [max(0, day * 0.5 + random.randint(-2, 2)) for day in days]
        bugs_fixed = [max(0, day * 0.45 + random.randint(-3, 1)) for day in days]
        
        fig.add_trace(
            go.Scatter(
                x=days,
                y=code_quality,
                mode='lines',
                name='Code Quality (%)',
                line=dict(color='#27ae60', width=2),
                hovertemplate='Day %{x}<br>Quality: %{y:.1f}%<extra></extra>'
            ),
            row=3, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=days,
                y=bugs_found,
                mode='lines',
                name='Bugs Found',
                line=dict(color='#e74c3c', width=2),
                hovertemplate='Day %{x}<br>Bugs Found: %{y:.0f}<extra></extra>'
            ),
            row=3, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=days,
                y=bugs_fixed,
                mode='lines',
                name='Bugs Fixed',
                line=dict(color='#3498db', width=2),
                hovertemplate='Day %{x}<br>Bugs Fixed: %{y:.0f}<extra></extra>'
            ),
            row=3, col=1
        )
    
    def _add_market_metrics(self, fig, state):
        """Add market position metrics"""
        # Market share simulation
        labels = ['Our Product', 'Competitor A', 'Competitor B', 'Others']
        values = [15, 35, 25, 25]  # Starting market share
        
        # Adjust based on progress
        progress_factor = min(1, state['days_elapsed'] / 180)
        values[0] = 15 + (35 * progress_factor)  # Our market share grows
        values[1] = 35 - (15 * progress_factor)  # Competitor shrinks
        values[2] = 25 - (10 * progress_factor)  # Another competitor shrinks
        values[3] = 25 - (10 * progress_factor)  # Others shrink
        
        # Normalize to 100%
        total = sum(values)
        values = [v / total * 100 for v in values]
        
        fig.add_trace(
            go.Pie(
                labels=labels,
                values=values,
                name='Market Share',
                marker_colors=['#27ae60', '#e74c3c', '#f39c12', '#95a5a6'],
                hovertemplate='%{label}: %{percent}<extra></extra>'
            ),
            row=3, col=2
        )
    
    def _generate_summary_data(self, state):
        """Generate summary data for CSV export"""
        summary_data = {
            'timestamp': datetime.now().isoformat(),
            'day': state['days_elapsed'],
            'phase': state['phase'],
            'revenue': state['revenue'],
            'cash_burn': state['cash_burn'],
            'runway_days': state['runway_days'],
            'team_morale': state['team_morale'],
            'code_quality': state['code_quality'],
            'customer_satisfaction': state['customer_satisfaction'],
            'agent_count': len(self.orchestrator.agents)
        }
        
        # Save to JSON
        with open(self.data_path / f"dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", 'w') as f:
            json.dump(summary_data, f, indent=2)
        
        # Append to CSV
        csv_file = self.data_path / "dashboard_history.csv"
        df = pd.DataFrame([summary_data])
        
        if csv_file.exists():
            df.to_csv(csv_file, mode='a', header=False, index=False)
        else:
            df.to_csv(csv_file, index=False)
    
    def generate_executive_summary(self):
        """Generate executive summary report"""
        state = self.orchestrator.company_state
        
        summary = f"""# ZTO Inc. Executive Summary
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Company Overview
- **Current Day**: {state['days_elapsed']:.0f} of 180
- **Phase**: {state['phase']}
- **Team Size**: {len(self.orchestrator.agents)} AI agents

## Financial Performance
- **Revenue**: ${state['revenue']:,.0f}
- **Cash Burn**: ${state['cash_burn']:,.0f}
- **Runway**: {state['runway_days']:.0f} days
- **Burn Rate**: $2,500/day

## Operational Metrics
- **Team Morale**: {state['team_morale']}/100
- **Code Quality**: {state['code_quality']}/100
- **Customer Satisfaction**: {state['customer_satisfaction']}/100

## Key Milestones
- ✅ Phase 0: Idea Intake - Completed
- 🔄 Phase 1: Discovery - In Progress
- ⏳ Phase 2: Architecture - Pending
- ⏳ Phase 3: MVP Development - Pending
- ⏳ Phase 4: Private Beta - Pending
- ⏳ Phase 5: Hardening & Monetization - Pending
- ⏳ Phase 6: Public Launch - Pending
- ⏳ Phase 7: Scale to $1M - Pending

## Risk Assessment
- **Financial Risk**: {'LOW' if state['runway_days'] > 90 else 'MEDIUM' if state['runway_days'] > 30 else 'HIGH'}
- **Technical Risk**: LOW (experienced team)
- **Market Risk**: MEDIUM (validation in progress)

## Next Steps
1. Complete user research and market validation
2. Finalize technical architecture
3. Begin MVP development
4. Establish revenue streams
5. Monitor cash flow closely

---
*This report is generated automatically by the ZTO virtual company system.*
"""
        
        # Save summary
        summary_file = Path(".finance/executive_summary.md")
        with open(summary_file, 'w') as f:
            f.write(summary)
        
        return summary

def main():
    """Generate dashboard"""
    dashboard = FinancialDashboard()
    path = dashboard.generate_dashboard()
    print(f"Dashboard generated: {path}")
    
    # Also generate executive summary
    summary = dashboard.generate_executive_summary()
    print("Executive summary generated")

if __name__ == "__main__":
    main()