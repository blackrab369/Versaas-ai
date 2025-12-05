from zto_enterprise_platform import app    # import your real Flask app
from werkzeug.middleware.proxy_fix import ProxyFix
app.wsgi_app = ProxyFix(app.wsgi_app)      # optional, handles Vercel’s proxy
app = app                                    # export as “app”