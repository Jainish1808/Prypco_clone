# 🚀 CryptoConnect Setup Guide

This guide will help you set up the complete CryptoConnect tokenized real estate platform with FastAPI backend, React frontend, MongoDB database, and XRPL blockchain integration.

## 📋 Prerequisites

Before starting, ensure you have:

- ✅ **Python 3.8+** installed
- ✅ **Node.js 18+** installed  
- ✅ **MongoDB** running (local or cloud)
- ✅ **Git** installed
- ✅ Your Python virtual environment at: `C:\Users\jaini\IntellijIdea\IGenerate_PYTHON_INTERN\env`

## 🔧 Step-by-Step Setup

### Step 1: Activate Your Python Environment

```powershell
# Activate your existing Python environment
C:\Users\jaini\IntellijIdea\IGenerate_PYTHON_INTERN\env\Scripts\Activate.ps1
```

### Step 2: Install Python Dependencies

```bash
cd CryptoConnect/backend
pip install -r requirements.txt
```

### Step 3: Install Node.js Dependencies

```bash
cd ..  # Back to CryptoConnect root
npm install
```

### Step 4: Set Up MongoDB

#### Option A: Local MongoDB
1. Install MongoDB Community Edition
2. Start MongoDB service
3. MongoDB will be available at `mongodb://localhost:27017`

#### Option B: MongoDB Atlas (Cloud)
1. Create account at https://www.mongodb.com/atlas
2. Create a free cluster
3. Get connection string

### Step 5: Configure Environment Variables

Create `backend/.env` file:

```env
# Database
MONGODB_URL=mongodb://localhost:27017/cryptoconnect

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=30

# XRPL Configuration (will be set in next step)
XRPL_NETWORK=testnet
ISSUER_WALLET_SEED=
ISSUER_WALLET_ADDRESS=

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True
```

### Step 6: Set Up XRPL Wallet

Run the XRPL wallet setup script:

```bash
cd backend
python setup_xrpl_wallet.py
```

This will:
- Create a new XRPL testnet wallet
- Fund it with test XRP
- Display the wallet credentials

**Copy the output and update your `.env` file with the wallet credentials.**

### Step 7: Initialize Database

```bash
python init_db.py
```

This will:
- Connect to MongoDB
- Create database collections
- Create an admin user (admin@cryptoconnect.com / admin123)
- Create a sample property for testing

### Step 8: Start the Application

#### Option A: Start Both Frontend and Backend Together
```bash
cd ..  # Back to CryptoConnect root
npm run dev:full
```

#### Option B: Start Separately
```bash
# Terminal 1 - Backend
npm run dev:backend

# Terminal 2 - Frontend
npm run dev
```

### Step 9: Access the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 🧪 Testing the Setup

### 1. Test API Health
Visit: http://localhost:8000/health

### 2. Test Admin Login
- Email: `admin@cryptoconnect.com`
- Password: `admin123`

### 3. Test Property Listing
Visit the properties page to see the sample property.

### 4. Test User Registration
Create a new investor or seller account.

## 🎯 User Roles and Testing

### Admin User
- **Email**: admin@cryptoconnect.com
- **Password**: admin123
- **Capabilities**: 
  - Approve/reject properties
  - Tokenize properties
  - Distribute rental income
  - View admin dashboard

### Investor Flow Testing
1. Register new user with role "investor"
2. Complete KYC (simplified - auto-approved)
3. Browse properties
4. Invest in a property
5. View portfolio dashboard

### Seller Flow Testing
1. Register new user with role "seller"
2. Complete KYC
3. Submit a new property
4. Track property status
5. View tokenization preview

## 🔍 API Endpoints Overview

### Authentication
- `POST /auth/register` - Register user
- `POST /auth/login` - Login user
- `GET /auth/me` - Get current user
- `POST /auth/kyc-submit` - Submit KYC

### Properties
- `GET /properties` - List properties
- `GET /properties/{id}` - Get property details
- `POST /properties/{id}/invest` - Invest in property

### Seller
- `POST /seller/property/submit` - Submit property
- `GET /seller/properties` - Get seller properties

### Investor
- `GET /investor/holdings` - Get holdings
- `GET /investor/transactions` - Get transactions
- `GET /investor/portfolio-summary` - Get portfolio

### Admin
- `GET /admin/properties/pending` - Pending properties
- `PUT /admin/properties/{id}/status` - Update status
- `POST /admin/properties/{id}/tokenize` - Tokenize property

## 🛠️ Development Commands

```bash
# Install backend dependencies
npm run backend:install

# Start backend only
npm run backend:start

# Start frontend only
npm run dev

# Start both together
npm run dev:full

# Build frontend
npm run build

# Type checking
npm run check
```

## 🔧 Troubleshooting

### Common Issues

#### 1. MongoDB Connection Error
```
Error: MongoServerError: connect ECONNREFUSED
```
**Solution**: Ensure MongoDB is running locally or check connection string.

#### 2. Python Module Not Found
```
ModuleNotFoundError: No module named 'fastapi'
```
**Solution**: Activate your Python environment and install requirements.

#### 3. XRPL Wallet Issues
```
Error: Failed to create wallet
```
**Solution**: Check internet connection and run `setup_xrpl_wallet.py` again.

#### 4. CORS Errors
```
Access to fetch blocked by CORS policy
```
**Solution**: Backend is configured for localhost:5173. Check if frontend is running on correct port.

#### 5. JWT Token Issues
```
Could not validate credentials
```
**Solution**: Check JWT_SECRET_KEY in .env file and ensure it's properly set.

### Debug Mode

Enable debug logging by setting `DEBUG=True` in your `.env` file.

### Database Reset

To reset the database:
```bash
# Connect to MongoDB and drop the database
mongo
use cryptoconnect
db.dropDatabase()

# Re-run initialization
python init_db.py
```

## 📊 Mathematical Formulas

The platform implements these precise formulas:

1. **Total Tokens**: `N = S × 10,000` (S = size in sqm)
2. **Token Price**: `P = V / N` (V = property value, N = total tokens)
3. **Ownership Fraction**: `F = k / N` (k = tokens owned)
4. **Rental Income Share**: `I = (k / N) × R` (R = total rental income)

## 🔐 Security Notes

- JWT tokens expire in 30 minutes (configurable)
- Passwords are hashed with bcrypt
- XRPL wallet seeds should be encrypted in production
- Environment variables contain sensitive data
- CORS is configured for development origins

## 🚀 Next Steps

After successful setup:

1. **Customize the Frontend**: The React frontend remains unchanged and can be customized as needed
2. **Add More Properties**: Use the seller panel to add more properties
3. **Test Investment Flow**: Complete the full investment process
4. **Explore XRPL Integration**: Check transactions on XRPL testnet explorer
5. **Add Features**: Extend the platform with additional features

## 📞 Support

If you encounter issues:

1. Check the console logs (both frontend and backend)
2. Review the API documentation at http://localhost:8000/docs
3. Ensure all environment variables are set correctly
4. Verify MongoDB and XRPL connections

## 🎉 Success!

If everything is working:
- ✅ Frontend loads at http://localhost:5173
- ✅ Backend API responds at http://localhost:8000
- ✅ Database connection is successful
- ✅ XRPL wallet is configured
- ✅ Sample data is loaded

You now have a fully functional tokenized real estate platform! 🏠💎