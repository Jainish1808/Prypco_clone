# CryptoConnect Troubleshooting Guide

## Property Submission Not Working - Step by Step Fix

### Step 1: Start MongoDB
Make sure MongoDB is running:
```bash
# On Windows
net start MongoDB
# Or if installed manually
mongod --dbpath "C:\data\db"
```

### Step 2: Test Backend Independently
```bash
cd CryptoConnect/backend
python test_backend.py
```
This should show "🎉 All tests passed! Backend is working correctly."

### Step 3: Start Backend Server
```bash
cd CryptoConnect/backend
python run.py
```
You should see:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 4: Test Backend API
Open browser and go to:
- http://localhost:8000/health (should show {"status": "healthy"})
- http://localhost:8000/docs (should show API documentation)

### Step 5: Start Frontend
In a new terminal:
```bash
cd CryptoConnect
npm run dev
```

### Step 6: Test Frontend-Backend Connection
Open the test file in browser:
```
file:///path/to/CryptoConnect/test_frontend_backend_connection.html
```
All tests should pass.

### Step 7: Test Property Submission in App

1. **Register a new user** with role "seller"
2. **Login** with the user
3. **Submit a property** - check browser console for errors

### Common Issues and Solutions

#### Issue 1: Backend not starting
**Error**: `ModuleNotFoundError` or import errors
**Solution**: 
```bash
cd CryptoConnect/backend
pip install -r requirements.txt
```

#### Issue 2: MongoDB connection error
**Error**: `ServerSelectionTimeoutError`
**Solution**: 
- Make sure MongoDB is running
- Check MongoDB URL in `.env` file

#### Issue 3: CORS errors in browser
**Error**: `Access to fetch at 'http://localhost:8000' from origin 'http://localhost:5173' has been blocked by CORS policy`
**Solution**: Backend already has CORS configured, but make sure both servers are running

#### Issue 4: 401 Unauthorized errors
**Error**: Property submission returns 401
**Solution**: 
- Make sure user is logged in
- Check if JWT token is being sent in requests
- Check browser localStorage for 'token'

#### Issue 5: Property not saving to database
**Error**: Property appears to submit but doesn't show up
**Solution**: 
- Check backend logs for errors
- Test with debug endpoint: `POST /api/seller/property/submit-debug`

### Debug Commands

#### Check if backend is receiving requests:
```bash
# In backend directory
python -c "
import asyncio
from app.main import app
import uvicorn
uvicorn.run(app, host='0.0.0.0', port=8000, log_level='debug')
"
```

#### Check database contents:
```bash
# In backend directory
python -c "
import asyncio
from app.database import connect_to_mongo
from app.models.property import Property
from app.models.user import User

async def check_db():
    await connect_to_mongo()
    users = await User.find().to_list()
    properties = await Property.find().to_list()
    print(f'Users: {len(users)}')
    print(f'Properties: {len(properties)}')
    for prop in properties:
        print(f'  - {prop.title} by {prop.seller_name}')

asyncio.run(check_db())
"
```

### Quick Start Script
Use the provided script to start everything:
```bash
# Double-click or run:
CryptoConnect/start_full_development.bat
```

This will:
1. Check if MongoDB is running
2. Start backend in a new window
3. Start frontend in a new window
4. Show you the URLs to access

### Expected Behavior After Fix

1. **Property Submission Form**: Should accept all data
2. **Submit Button**: Should show loading state
3. **Success**: Should redirect to "my-properties" page
4. **Backend Logs**: Should show property creation logs
5. **Database**: Should contain the new property
6. **Frontend**: Should show success message

### If Still Not Working

1. **Check browser console** for JavaScript errors
2. **Check backend logs** for Python errors
3. **Check network tab** in browser dev tools for failed requests
4. **Verify authentication** - make sure user is logged in
5. **Test with debug endpoint** first to isolate the issue

### Contact Information
If you're still having issues, provide:
1. Browser console errors
2. Backend log output
3. Network tab showing the failed request
4. Steps you followed