stripe login
stripe listen --forward-to localhost:5000/stripe/webhook
# copy the ***Webhook signing secret*** → add to env as STRIPE_WEBHOOK_SECRET
stripe products create --name="Virsaas AI Messages" --unit-label="message"
# copy product id prod_xxx

stripe prices create \
  -d product=prod_xxx \
  -d unit_amount=10 \
  -d currency=usd \
  -d "recurring[usage_type]"=metered \
  -d "recurring[interval]"=month
# copy price id → STRIPE_PRICE_METERED env var