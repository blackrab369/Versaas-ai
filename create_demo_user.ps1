#set DATABASE_URL=postgresql://postgres.<ref>:<password>@aws-0-us-east-1.pooler.supabase.com:6543/postgres
$env:DATABASE_URL="postgresql://postgres.[ref]:[pass]@..."
set DATABASE_URL=postgresql://postgres.jaqiwwvwskixowgaojif:Zx9NlTi583jETvla@aws-1-us-east-1.pooler.supabase.com:6543/postgres?sslmode=require
Select-String -Path zto_enterprise_platform.py -Pattern 'metadata\s*=.*db\.Column'
python launch_enterprise.py --setup-remote --demo-data