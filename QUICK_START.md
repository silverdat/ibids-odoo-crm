# 🚀 Quick Start Guide - ibiDs CRM

## **Step 1: Start Docker Desktop**
1. Open Docker Desktop on your Mac
2. Wait for it to fully start (green light in status bar)

## **Step 2: Deploy the Application**
```bash
./deploy.sh
```

This will:
- Start PostgreSQL database
- Start Odoo with your custom module
- Wait for everything to be ready
- Give you the access URL

## **Step 3: Access Your CRM**
1. Open your browser
2. Go to: `http://localhost:8069`
3. You'll see the Odoo database creation screen

## **Step 4: Create Database**
1. **Database Name**: `ibidscrm` (or any name you want)
2. **Email**: Your email address
3. **Password**: Choose a strong password
4. **Master Password**: `admin123`
5. Click "Create Database"

## **Step 5: Install Your Module**
1. Go to **Apps** menu
2. Click **Update Apps List** (refresh icon)
3. Search for "Government CRM" or "govcon"
4. Click **Install** on the "Government CRM" module

## **Step 6: Configure API**
1. Go to **Government CRM > Configuration > Sync Services**
2. Create a new sync service:
   - **Name**: ibiDs API
   - **API URL**: Your ibiDs API endpoint
   - **API Key**: Your ibiDs API key
3. Test the connection

## **Step 7: Start Using Your CRM**
1. Go to **Government CRM > Tenders**
2. Create your first tender or sync from API
3. Start managing your government contracts!

## **Troubleshooting**

### If Odoo doesn't start:
```bash
docker-compose logs odoo
```

### If you need to restart:
```bash
docker-compose down
./deploy.sh
```

### If you need to update the module:
```bash
docker-compose restart odoo
```

## **Access URLs**
- **Main CRM**: http://localhost:8069
- **Database Manager**: http://localhost:8069/web/database/manager

## **Default Credentials**
- **Master Password**: admin123
- **Your Database**: Use the password you created

## **Next Steps After Setup**
1. Configure your ibiDs API credentials
2. Set up email processing
3. Import initial data
4. Train your team

---

**Need Help?** Check the logs or restart the deployment script. 