# Tokenized Real Estate Platform

## Overview

A full-stack tokenized real estate investment platform that enables fractional ownership of real-world properties through digital tokens on the XRP Ledger. The application allows investors to purchase property tokens for fractional ownership and receive proportional rental income distributions, while enabling property sellers to list and tokenize their assets for crowdfunding.

The platform features a comprehensive investment dashboard, property catalog, secondary market for token trading, and automated income distribution systems. Built with React frontend, Express.js backend, PostgreSQL database with Drizzle ORM, and integrated with XRP Ledger testnet for blockchain operations.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: React with TypeScript using Vite for build tooling
- **UI Library**: shadcn/ui components built on Radix UI primitives with Tailwind CSS
- **State Management**: TanStack React Query for server state and caching
- **Routing**: Wouter for client-side routing with protected route guards
- **Authentication**: Session-based auth with JWT tokens and context provider pattern
- **Form Handling**: React Hook Form with Zod validation for type-safe forms

### Backend Architecture
- **Framework**: Express.js with TypeScript
- **Authentication**: Passport.js with local strategy and express-session
- **API Design**: RESTful endpoints with proper error handling middleware
- **Password Security**: Crypto module with scrypt for password hashing
- **Session Storage**: In-memory store with connect-pg-simple for production PostgreSQL sessions
- **Development**: Hot reload with Vite middleware integration

### Database Architecture
- **Primary Database**: PostgreSQL with Drizzle ORM for type-safe database operations
- **Schema Management**: Drizzle Kit for migrations and schema evolution
- **Connection**: Neon serverless PostgreSQL driver for cloud database connectivity
- **Data Models**: Zod schemas shared between frontend and backend for type consistency

### Core Data Models
- **Users**: Authentication, KYC status, investor/seller roles, wallet addresses
- **Properties**: Real estate listings with tokenization details, approval workflow
- **Transactions**: Investment records, token transfers, blockchain transaction hashes
- **Holdings**: User token ownership tracking with investment amounts
- **Market Orders**: Secondary market buy/sell orders with matching engine
- **Income Distributions**: Automated rental income calculations and distributions

### Blockchain Integration
- **Platform**: XRP Ledger testnet for token operations
- **Token Model**: Fungible tokens representing property fractions (1 token per $1 of property value divided by property size in square meters × 10,000)
- **Operations**: Trust line establishment, token minting, secure transfers, transaction recording
- **Wallet Integration**: User wallet address management for token custody

### Mathematical Engine
- **Token Price**: P = V / N (property value divided by total tokens)
- **Total Tokens**: N = S × 10,000 (property size in square meters × 10,000)
- **Ownership Fraction**: F = k / N (tokens purchased divided by total tokens)
- **Income Distribution**: I = (k / N) × R (ownership fraction × total rental income)

### Security Architecture
- **Authentication**: Session-based with secure password hashing using crypto.scrypt
- **Authorization**: Role-based access control (investor/seller) with protected routes
- **Data Validation**: Comprehensive Zod schema validation on all inputs
- **Session Management**: Secure session storage with configurable session store

## External Dependencies

### Core Dependencies
- **@neondatabase/serverless**: Serverless PostgreSQL database connection
- **drizzle-orm**: Type-safe ORM for database operations
- **drizzle-zod**: Integration between Drizzle and Zod for schema validation
- **express**: Web application framework
- **passport**: Authentication middleware with local strategy
- **@tanstack/react-query**: Server state management and caching

### UI and Styling
- **@radix-ui/***: Headless UI component primitives for accessibility
- **tailwindcss**: Utility-first CSS framework
- **class-variance-authority**: Type-safe CSS class variants
- **cmdk**: Command palette component
- **lucide-react**: Modern icon library

### Development Tools
- **vite**: Fast build tool and development server
- **typescript**: Static type checking
- **@replit/vite-plugin-***: Replit-specific development enhancements
- **tsx**: TypeScript execution for Node.js

### Blockchain Integration (Planned)
- **xrpl-py**: Python library for XRP Ledger operations (backend integration)
- Custom blockchain adapter service for token operations
- Mock blockchain service for development and testing

### Form and Validation
- **react-hook-form**: Performant forms with minimal re-renders
- **@hookform/resolvers**: Zod resolver integration
- **zod**: Runtime type validation and parsing

### Utilities
- **date-fns**: Date manipulation and formatting
- **nanoid**: Unique ID generation
- **clsx**: Conditional CSS class composition