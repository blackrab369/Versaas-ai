# grab the host-only part (without port)
nslookup aws-0-us-east-1.pooler.supabase.com
# if it times out, use Google's DNS
nslookup aws-0-us-east-1.pooler.supabase.com 8.8.8.8
python launch_enterprise.py --setup-remote --demo-data