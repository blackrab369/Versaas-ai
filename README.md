# Virsaas Virtual Software Inc. – Enterprise Platform

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-green.svg)
![Flask](https://img.shields.io/badge/flask-2.3+-orange.svg)
![License](https://img.shields.io/badge/license-Proprietary-red.svg)

> **Mission**: Ship a profitable, million-dollar software product in under 180 days with $0 outside capital using 25 AI agents.

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Features](#features)
4. [Tech Stack](#tech-stack)
5. [Project Structure](#project-structure)
6. [Installation](#installation)
7. [Configuration](#configuration)
8. [Running the Application](#running-the-application)
9. [API Reference](#api-reference)
10. [Database Schema](#database-schema)
11. [AI Agents](#ai-agents)
12. [Payment Integration](#payment-integration)
13. [White-Label Agency System](#white-label-agency-system)
14. [Deployment](#deployment)
15. [Troubleshooting](#troubleshooting)

---

## Overview

Virsaas is a professional SaaS platform that simulates a fully autonomous software development company powered by 25 AI agents. Users can describe their software idea, and the platform orchestrates a virtual team of developers, designers, project managers, legal counsel, and executives to build, test, and deploy the product.

### Key Differentiators

- **2.5D Virtual Office**: Watch AI agents work in a pixel-art isometric office environment
- **Real-Time Simulation**: 1 second = 1 simulated hour of work
- **Multi-Payment Support**: Stripe, PayPal, and Solana crypto payments
- **White-Label Agencies**: Resellers can brand the platform with custom subdomains
- **WebSocket War Room**: Real-time collaboration and agent communication
- **Push Notifications**: Web push for deployment and milestone alerts

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend Layer                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐   │
│  │ Dashboard│ │  Office  │ │ War Room │ │ Enterprise View  │   │
│  │   HTML   │ │ 2.5D View│ │ WebSocket│ │   Project Mgmt   │   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────────┘   │
├─────────────────────────────────────────────────────────────────┤
│                         Flask Backend                           │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐   │
│  │   Auth   │ │   API    │ │SocketIO  │ │   Simulation     │   │
│  │ (Login)  │ │ Routes   │ │ Events   │ │    Manager       │   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────────┘   │
├─────────────────────────────────────────────────────────────────┤
│                        ZTO Orchestrator                         │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  25 AI Agents  │  Task Queue  │  Communication Log       │  │
│  │  Company State │  Audit Trail │  Financial Simulation    │  │
│  └──────────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│                         Data Layer                              │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐   │
│  │PostgreSQL│ │  Redis   │ │  Stripe  │ │     Supabase     │   │
│  │ (SQLite) │ │  Cache   │ │ Payments │ │   (Production)   │   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Features

### Core Platform

| Feature | Description |
|---------|-------------|
| **User Registration** | Email/password or magic-link authentication |
| **Project Management** | Create, view, and manage software projects |
| **AI Simulation** | 25 AI agents working on your project in real-time |
| **Document Generation** | Auto-generate business plans, legal docs, contracts |
| **Source Code Export** | Download complete project as ZIP |

### Monetization

| Feature | Description |
|---------|-------------|
| **Stripe Subscriptions** | Recurring billing with metered usage |
| **PayPal Checkout** | One-time and subscription payments |
| **Solana Crypto** | Accept USDC payments via Phantom wallet |
| **Usage-Based Billing** | Track API calls and sync to Stripe |

### Enterprise Features

| Feature | Description |
|---------|-------------|
| **White-Label Agencies** | Custom subdomains (`agency.virsaas.app`) |
| **Agency Dashboard** | MRR tracking, downstream user management |
| **Stripe Connect** | Agency revenue sharing |
| **Referral System** | 20% commission on referred users |

### Real-Time Features

| Feature | Description |
|---------|-------------|
| **WebSocket Events** | Agent status, task updates, office positions |
| **Push Notifications** | VAPID-based web push for alerts |
| **CEO Voice Chat** | Whisper-powered voice transcription |

---

## Tech Stack

### Backend

| Technology | Purpose |
|------------|---------|
| **Python 3.11+** | Core runtime |
| **Flask 2.3+** | Web framework |
| **Flask-SQLAlchemy** | ORM / Database |
| **Flask-Login** | Authentication |
| **Flask-SocketIO** | WebSocket support |
| **Flask-Mail** | Email notifications |
| **Eventlet** | Async WebSocket handling |

### Database

| Technology | Purpose |
|------------|---------|
| **PostgreSQL** | Production database (Supabase) |
| **SQLite** | Local development fallback |
| **Redis** | Session cache, rate limiting |

### Payments

| Technology | Purpose |
|------------|---------|
| **Stripe** | Subscriptions, metered billing, Connect |
| **PayPal** | Sandbox checkout |
| **Solana** | Crypto payments via RPC |

### AI/ML

| Technology | Purpose |
|------------|---------|
| **OpenAI GPT-4** | Document generation, CEO chat |
| **Kimi AI** | Code generation |
| **Whisper** | Voice-to-text transcription |
| **Puter API** | 32-bit pixel art sprite generation |

### Deployment

| Technology | Purpose |
|------------|---------|
| **Vercel** | Serverless Python hosting |
| **Docker** | Container deployment |
| **Gunicorn + Gevent** | Production WSGI server |

---

## Project Structure

```
Versaas-ai/
├── app.py                          # Application entry point
├── zto_enterprise_platform.py      # Main Flask application (1600+ lines)
├── zto_saas_platform.py            # Alternative SaaS platform variant
├── launch_enterprise.py            # Enterprise launcher script
│
├── ZTO_Projects/                   # Simulation kernel
│   └── ZTO_Demo/
│       └── zto_kernel.py           # ZTOOrchestrator class (25 AI agents)
│
├── templates/                      # Jinja2 HTML templates
│   ├── base.html                   # Base layout with nav
│   ├── index.html                  # Landing page
│   ├── login.html                  # Login form
│   ├── register.html               # Registration form
│   ├── dashboard.html              # User dashboard
│   ├── project.html                # Project view
│   ├── enterprise_project.html     # Enhanced project view (69KB)
│   ├── subscribe.html              # Subscription page
│   ├── agency_dashboard.html       # White-label agency dashboard
│   ├── war_room.html               # Real-time collaboration
│   └── office_view.html            # 2.5D office visualization
│
├── static/
│   ├── css/                        # Stylesheets
│   ├── js/
│   │   ├── ceo-chat.js             # CEO chatbot frontend
│   │   ├── enterprise_animations.js # Office animations
│   │   ├── phantom_pay.js          # Solana Phantom wallet
│   │   ├── push.js                 # Push notification service worker
│   │   ├── war_room.js             # WebSocket war room
│   │   └── sw.js                   # Service worker
│   ├── img/                        # Images and sprites
│   └── manifest.json               # PWA manifest
│
├── api/                            # Vercel serverless functions
│   ├── index.py                    # API index
│   ├── ceo/                        # CEO chat endpoints
│   └── debugger/                   # Debug endpoints
│
├── user_projects/                  # Generated project files
│   └── {project_uuid}/
│       ├── frontend/src/
│       ├── backend/src/
│       ├── docs/
│       └── output/
│
├── requirements_enterprise.txt     # Python dependencies
├── requirements_saas.txt           # Alternative requirements
├── vercel.json                     # Vercel deployment config
├── .env.development.local          # Environment variables (development)
├── .env.local                      # Environment variables (local)
└── README.md                       # This file
```

---

## Installation

### Prerequisites

- Python 3.11 or higher
- Node.js 18+ (for frontend tooling, optional)
- PostgreSQL 14+ (or use SQLite for development)
- Redis (optional, for caching)

### Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/Versaas-ai.git
   cd Versaas-ai
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   source .venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements_enterprise.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.development.local .env
   # Edit .env with your configuration
   ```

5. **Initialize database**
   ```bash
   python -c "from zto_enterprise_platform import app, db; app.app_context().push(); db.create_all()"
   ```

---

## Configuration

### Required Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host:5432/db` |
| `SECRET_KEY` | Flask secret key (auto-generated if missing) | `your-secret-key-here` |
| `FERNET_KEY` | Encryption key for API keys (auto-generated if missing) | `base64-encoded-32-byte-key` |

### Optional Environment Variables

| Variable | Description |
|----------|-------------|
| `STRIPE_SECRET_KEY` | Stripe API secret key |
| `STRIPE_WEBHOOK_SECRET` | Stripe webhook signing secret |
| `STRIPE_PRICE_METERED` | Stripe metered price ID |
| `OPENAI_API_KEY` | OpenAI API key for GPT-4 |
| `PAYPAL_CLIENT_ID` | PayPal sandbox client ID |
| `PAYPAL_CLIENT_SECRET` | PayPal sandbox secret |
| `SOLANA_RPC_URL` | Solana RPC endpoint |
| `UPSTASH_REDIS_REST_URL` | Redis connection URL |
| `VAPID_PRIVATE` | VAPID private key for push |
| `VAPID_PUBLIC` | VAPID public key for push |
| `FIGMA_TOKEN` | Figma API token for imports |

---

## Running the Application

### Development Mode

```bash
python app.py
```

The application will start on `http://localhost:5000`.

### Production Mode

```bash
gunicorn --worker-class eventlet -w 1 zto_enterprise_platform:app --bind 0.0.0.0:5000
```

### Docker

```bash
docker-compose up -d
```

Docker Compose configuration (from comments in source):

```yaml
version: "3.9"
services:
  app:
    build: .
    ports: ["5000:5000"]
    environment:
      - DATABASE_URL=sqlite:///virsaas.db
      - FERNET_KEY=your-32-url-safe-base64-key
      - OPENAI_API_KEY=sk-xxx
      - STRIPE_SECRET_KEY=sk_test_xxx
    volumes:
      - ./user_projects:/app/user_projects
  redis:
    image: redis:7-alpine
```

---

## API Reference

### Authentication

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/register` | POST | Register new user |
| `/login` | POST | Login with username/password |
| `/logout` | GET | Logout current user |
| `/login/email` | POST | Request magic link |
| `/login/magic/<token>` | GET | Verify magic link |

### Projects

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/create_project` | POST | Create new project |
| `/project/<uuid:project_id>` | GET | View project |
| `/api/project/<uuid:project_id>/status` | GET | Get project status |
| `/api/project/<uuid:project_id>/message` | POST | Send message to CEO |
| `/api/project/<uuid:project_id>/generate_documents` | POST | Generate business plan & legal docs |
| `/api/project/<uuid:project_id>/download` | GET | Download project ZIP |

### CEO Chat

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/ceo/chat` | POST | Chat with AI CEO (public, rate-limited) |
| `/api/ceo/voice` | POST | Voice transcription via Whisper |

### Payments

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/create_checkout_session` | POST | Create Stripe checkout |
| `/stripe/create-customer` | POST | Create Stripe customer |
| `/stripe/webhook` | POST | Stripe webhook handler |
| `/stripe/portal` | POST | Customer billing portal |
| `/paypal/create-order` | POST | Create PayPal order |
| `/paypal/capture-order` | POST | Capture PayPal payment |
| `/crypto/capture` | POST | Verify Solana transaction |

### Agency (White-Label)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/agency/create` | POST | Create new agency |
| `/agency/dashboard` | GET | Agency owner dashboard |
| `/agency/white-label` | POST | Update branding |
| `/referral/create` | POST | Generate referral code |

### Cron Jobs

| Endpoint | Schedule | Description |
|----------|----------|-------------|
| `/cron/usage-sync` | Daily 4 AM | Sync usage to Stripe |
| `/cron/agency-mrr` | Daily 6 AM | Calculate agency MRR |

---

## Database Schema

### Core Models

| Model | Description | Key Fields |
|-------|-------------|------------|
| `User` | Platform users | `username`, `email`, `subscription_type`, `push_sub` |
| `Project` | User projects | `project_id` (UUID), `simulation_data`, `revenue`, `current_phase` |
| `Agent` | AI agents per project | `agent_id`, `role`, `location_x/y`, `energy`, `morale` |
| `Task` | Project tasks | `title`, `status`, `priority`, `estimated_hours`, `code_files` |
| `Communication` | Agent messages | `from_agent`, `to_agent`, `message`, `thread_id` |
| `Document` | Generated documents | `document_type`, `file_path`, `content_hash`, `version` |

### Payment Models

| Model | Description |
|-------|-------------|
| `Payment` | Payment records |
| `StripeCustomer` | Stripe customer mapping |
| `UsageRecord` | Metered usage tracking |
| `PayPalPayment` | PayPal order tracking |
| `CryptoPayment` | Solana transaction verification |

### Agency Models

| Model | Description |
|-------|-------------|
| `Agency` | White-label agencies |
| `AgencyUser` | Agency membership |
| `AgencyMRR` | Monthly recurring revenue |
| `Referral` | Referral codes and commissions |

---

## AI Agents

The platform includes 25 specialized AI agents organized into departments:

### Development Team (10 agents)

| ID | Role | Personality |
|----|------|-------------|
| DEV-001 | Principal Full-Stack Architect | 10× engineer, allergic to meetings |
| DEV-002 | Senior Back-End Engineer | DDD enthusiast, coffee-powered |
| DEV-003 | Senior Front-End Engineer | Pixel-perfect or death |
| DEV-004 | Senior Mobile Engineer | iOS & Android parity zealot |
| DEV-005 | Senior Cloud Engineer | Infra-as-caffeine, cost optimization ninja |
| DEV-006 | Senior DevOps / SRE | Five-nines or bust |
| DEV-007 | Senior API Engineer | Swagger-first |
| DEV-008 | Senior Data Engineer | Data is the new oil |
| DEV-009 | Senior Security Engineer | Paranoid by profession |
| DEV-010 | Senior QA Automation | Green bar addict |

### Design Team (2 agents)

| ID | Role | Personality |
|----|------|-------------|
| UX-001 | Lead UX Researcher | Talks to humans so devs don't have to |
| UX-002 | Senior UI Designer | Dark-mode evangelist |

### Management (4 agents)

| ID | Role | Personality |
|----|------|-------------|
| DOC-001 | Senior Technical Writer | If it isn't documented, it ships |
| PM-001 | Scrum Project Manager | Story-point sommelier |
| PM-002 | Waterfall Project Manager | Gantt-chart ninja |
| MGT-001 | COO | Process polymath |

### Administration (3 agents)

| ID | Role | Personality |
|----|------|-------------|
| ADMIN-001 | Legal Counsel | NDA dragon |
| ADMIN-002 | CFO | Cash-flow clairvoyant |
| ADMIN-003 | People & Compliance | Culture curator |

### Executive (5 agents)

| ID | Role | Personality |
|----|------|-------------|
| CEO-001 | Chief Executive Officer | Human-facing interface |
| BOARD-001 | VC Chair (ex-Sequoia) | Exit-focused |
| BOARD-002 | Fortune 50 CTO | Risk-averse on tech debt |
| BOARD-003 | Harvard Law Governance | Ethics guardian |
| BOARD-004 | Angel Investor | GTM strategist |

---

## Payment Integration

### Stripe Setup

1. Create products and prices in Stripe Dashboard
2. Set `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `STRIPE_PRICE_METERED`
3. Configure webhook endpoint: `https://yourdomain.com/stripe/webhook`
4. Events to subscribe: `customer.subscription.created`, `customer.subscription.deleted`

### PayPal Setup

1. Create sandbox application at developer.paypal.com
2. Set `PAYPAL_CLIENT_ID` and `PAYPAL_CLIENT_SECRET`
3. Uses sandbox API: `api-m.sandbox.paypal.com`

### Solana Setup

1. Set `SOLANA_RPC_URL` (default: mainnet-beta)
2. Users pay via Phantom wallet
3. Frontend: `static/js/phantom_pay.js`

---

## White-Label Agency System

Agencies can resell the platform with custom branding:

1. **Create Agency**: POST to `/agency/create` with name, subdomain, color
2. **Stripe Connect**: Automatic Express account creation and onboarding
3. **Custom Branding**: Logo URL and primary color applied via subdomain
4. **Revenue Share**: Tracked via `AgencyMRR` model

Subdomain format: `{agency-name}.virsaas.app`

---

## Deployment

### Vercel (Recommended)

The project includes `vercel.json` configuration:

```json
{
  "functions": {
    "zto_enterprise_platform.py": {
      "runtime": "vercel-python-v3",
      "maxDuration": 30
    }
  },
  "routes": [
    { "src": "/socket.io/(.*)", "dest": "zto_enterprise_platform.py" },
    { "src": "/(.*)", "dest": "zto_enterprise_platform.py" }
  ],
  "crons": [
    { "path": "/cron/usage-sync", "schedule": "0 4 * * *" },
    { "path": "/cron/agency-mrr", "schedule": "0 6 * * *" }
  ]
}
```

### Manual Deployment

1. Set up PostgreSQL (e.g., Supabase, Neon, AWS RDS)
2. Set up Redis (e.g., Upstash, Redis Cloud)
3. Configure environment variables
4. Run with Gunicorn:
   ```bash
   gunicorn --worker-class eventlet -w 1 zto_enterprise_platform:app
   ```

---

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| `NameError: ZTOOrchestrator` | Ensure `ZTO_Projects/ZTO_Demo/zto_kernel.py` exists or mock is active |
| `RuntimeError: FERNET_KEY not set` | Set `FERNET_KEY` env var or auto-generation will create temporary key |
| `Redis unavailable` | Application continues with in-memory fallback |
| `Stripe webhook signature fail` | Verify `STRIPE_WEBHOOK_SECRET` matches dashboard |
| WebSocket not connecting | Ensure Eventlet is installed and used as async mode |

### Logging

Logs are output to stdout with format:
```
%(asctime)s | %(levelname)s | %(name)s | %(message)s
```

Enable debug mode by setting `FLASK_ENV=development`.

---

## License

Proprietary – Virsaas Virtual Software Inc. All rights reserved.

---

## Contact

- **Email**: alex@virsaas.app
- **Website**: https://virsaas.app

---

*Last updated: December 7, 2025*
