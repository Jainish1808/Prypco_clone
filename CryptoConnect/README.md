# CryptoConnect - Tokenized Real Estate Investment Platform

A full-stack tokenized real estate investment platform built with React frontend and FastAPI Python backend, integrated with XRP Ledger for blockchain functionality and MongoDB for data storage.

## 🏗️ Architecture

- **Frontend**: React with TypeScript, Vite, TailwindCSS
- **Backend**: FastAPI with Python
- **Database**: MongoDB with Beanie ODM
- **Blockchain**: XRP Ledger (XRPL) for tokenization
- **Authentication**: JWT tokens

## 📁 Project Structure

```
CryptoConnect/
├── client/                 # React frontend (unchanged)
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   └── lib/
│   └── index.html
├── backend/               # FastAPI Python backend (new)
│   ├── app/
│   │   ├── models/       # MongoDB models
│   │   ├── routers/      # API endpoints
│   │   ├── services/     # Business logic
│   │   ├── auth.py       # Authentication
│   │   ├── config.py     # Configuration
│   │   ├── database.py   # Database connection
│   │   └── main.py       # FastAPI app
│   ├── requirements.txt
│   ├── run.py
│   ├── start.bat
│   └── start.ps1
└── package.json          # Updated for new setup
```

## 🚀 Quick Start

### Prerequisites

1. **Python 3.8+** with pip
2. **Node.js 18+** with npm
3. **MongoDB** (local or cloud)
4. **Git**

### 1. Clone and Setup

```bash
cd CryptoConnect
npm install
```

### 2. Backend Setup

#### Option A: Using your existing Python environment
```powershell
# Activate your environment
C:\Users\jaini\IntellijIdea\IGenerate_PYTHON_INTERN\env\Scripts\Activate.ps1

# Install Python dependencies
cd backend
pip install -r requirements.txt
```

#### Option B: Using the provided scripts
```bash
# Windows Command Prompt
backend\start.bat

# Or PowerShell
backend\start.ps1
```

### 3. Environment Configuration

Create `backend/.env` file:
```env
MONGODB_URL=mongodb://localhost:27017/cryptoconnect
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=30

# XRPL Configuration (for testnet)
XRPL_NETWORK=testnet
ISSUER_WALLET_SEED=your-xrpl-issuer-wallet-seed
ISSUER_WALLET_ADDRESS=your-xrpl-issuer-wallet-address

API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True
```

### 4. Start the Application

#### Option A: Start both frontend and backend together
```bash
npm run dev:full
```

#### Option B: Start separately
```bash
# Terminal 1 - Backend
npm run dev:backend

# Terminal 2 - Frontend  
npm run dev
```

The application will be available at:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## 🔧 API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - User login
- `GET /auth/me` - Get current user
- `POST /auth/kyc-submit` - Submit KYC information

### Properties (Investors)
- `GET /properties` - List all approved properties
- `GET /properties/{id}` - Get property details
- `POST /properties/{id}/invest` - Invest in property

### Seller Panel
- `POST /seller/property/submit` - Submit new property
- `GET /seller/properties` - Get seller's properties
- `GET /seller/property/{id}` - Get specific property

### Investor Dashboard
- `GET /investor/holdings` - Get token holdings
- `GET /investor/transactions` - Get transaction history
- `GET /investor/income-statements` - Get rental income statements
- `GET /investor/portfolio-summary` - Get portfolio summary

### Admin Panel
- `GET /admin/properties/pending` - Get pending properties
- `PUT /admin/properties/{id}/status` - Update property status
- `POST /admin/properties/{id}/tokenize` - Tokenize property
- `POST /admin/properties/{id}/distribute-income` - Distribute rental income

## 🏦 Mathematical Formulas Implemented

The platform implements the following precise formulas:

1. **Token Price (P)**: `P = V / N`
   - V = Property value in AED
   - N = Total number of tokens

2. **Total Tokens (N)**: `N = S × 10,000`
   - S = Property size in square meters

3. **Ownership Fraction (F)**: `F = k / N`
   - k = Number of tokens purchased
   - N = Total tokens

4. **Rental Income Share (I)**: `I = (k / N) × R`
   - k = Tokens owned
   - N = Total tokens
   - R = Total rental income

## 🔗 XRPL Integration

The platform integrates with XRP Ledger for:

- **Token Creation**: Each property gets a unique fungible token
- **Trust Lines**: Automatic trust line creation for investors
- **Token Distribution**: Secure token transfers to investor wallets
- **Transaction Recording**: All blockchain transactions are logged

### XRPL Setup

1. Create an XRPL wallet for the issuer account
2. Fund it on testnet using the faucet
3. Add the wallet seed and address to your `.env` file

## 📊 Database Models

### User Model
- Authentication and profile data
- KYC verification status
- XRPL wallet information

### Property Model
- Property details and financials
- Tokenization information
- Seller information
- Status tracking

### Transaction Model
- All platform transactions
- XRPL transaction hashes
- Investment and distribution records

## 🛡️ Security Features

- JWT-based authentication
- Password hashing with bcrypt
- Role-based access control
- XRPL wallet integration
- Environment variable configuration

## 🎯 User Flows

### Investor Flow
1. Register → KYC → Browse Properties → Invest → View Dashboard

### Seller Flow
1. Register → KYC → Access Seller Panel → Submit Property → Track Status

### Admin Flow
1. Review Properties → Approve/Reject → Tokenize → Manage Income Distribution

## 🔄 Development Workflow

1. **Frontend Development**: The React frontend remains unchanged and continues to work as before
2. **Backend Development**: All server logic is now in Python with FastAPI
3. **Database**: MongoDB replaces the previous database
4. **Blockchain**: XRPL integration for real tokenization

## 📝 Environment Variables

Copy `backend/.env.example` to `backend/.env` and configure:

- MongoDB connection string
- JWT secret key
- XRPL network and wallet credentials
- API configuration

## 🚨 Important Notes

- This is a development/demo setup - not for production deployment
- XRPL testnet is used for blockchain operations
- KYC verification is simplified for demo purposes
- All regulatory concepts are abstracted to generic terms

## 🆘 Troubleshooting

### Common Issues

1. **MongoDB Connection**: Ensure MongoDB is running locally or update connection string
2. **Python Dependencies**: Make sure all requirements are installed in your environment
3. **XRPL Wallet**: Generate a testnet wallet and fund it before tokenization
4. **CORS Issues**: Backend is configured to allow frontend origins

### Getting Help

1. Check the FastAPI docs at http://localhost:8000/docs
2. Review the console logs for both frontend and backend
3. Ensure all environment variables are properly set

## 📄 License

MIT License - See LICENSE file for details