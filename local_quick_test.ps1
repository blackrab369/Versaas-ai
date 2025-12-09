# 1. install new deps
pip install -r requirements_enterprise.txt

# 2. forward Stripe webhooks (so you can test checkout)
stripe listen --forward-to localhost:5000/stripe/webhook
# copy the webhook secret → add as STRIPE_WEBHOOK_SECRET in Vercel

# 3. run
python launch_enterprise.py