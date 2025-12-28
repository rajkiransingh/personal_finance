# 💰 Personal Finance Tracker

> A comprehensive full-stack application for tracking and managing your personal finances with real-time data
> integration, advanced analytics, and portfolio rebalancing.

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Architecture](#architecture)
- [Usage Guide](#usage-guide)
- [Development](#development)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Overview

Personal Finance Tracker is a modern, customizable, feature-rich application designed to help you take control of your
financial life. Track income, expenses, and investments across multiple asset classes with real-time market data,
intelligent categorization, and powerful analytics.

### Key Features

✨ **Multi-Asset Investment Tracking**

- Stocks (Indian & International)
- Mutual Funds
- ETFs
- Precious Metals (Gold & Silver)
- Real Estate
- Cryptocurrency

📊 **Advanced Analytics**

- Portfolio visualization and breakdown
- Investment performance metrics (XIRR, ROI, absolute returns)
- Asset allocation tracking
- Rebalancing recommendations
- Stock screening and scoring system

💳 **Transaction Management**

- Income and expense tracking
- CSV bank statement import
- Auto-categorization with machine learning (Plan for the future)
- Recurring transaction support (in alpha phase)

🎨 **Modern UI/UX**

- Multiple theme support (Bronze, Light Purple, Anime)
- Responsive design
- Interactive charts and visualizations
- Real-time data updates

## Prerequisites

Before you begin, ensure you have the following installed:

- **Docker**: Version 20.10 or higher
- **Docker Compose**: Version 2.0 or higher
- **Git**: For cloning the repository

Optional (for local development without Docker):

- **Node.js**: Version 18.x or higher
- **Python**: Version 3.10 or higher
- **MySQL**: Version 8.0 or higher

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/rajkiransingh/personal_finance.git
cd personal_finance
```

### 2. Set Up Environment Variables

Copy the example environment file and configure it:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys and database credentials. See [Configuration](#configuration) for details.

**Required configurations:**

- MySQL database credentials
- Exchange rate API key ([get free key](https://www.exchangerate-api.com/))
- RapidAPI key ([get free key](https://rapidapi.com/auth/login))
- Coin Market Cap ([get free key](https://coinmarketcap.com/api/))

### 3. Start the Application

Using Robot Framework (recommended):

```bash
robot start_application.robot
```

Or using Docker Compose directly:

```bash
# Start infrastructure (database, Redis)
docker-compose -f docker-compose.infra.yml up -d

# Wait for database to be ready (~30 seconds)

# Start application (backend + frontend)
docker-compose -f docker-compose.app.yml up -d
```

### 4. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### 5. Initialize Master Data

On first launch, navigate to **Settings > Supporting Data** to configure:

1. **Users**: Add household members
2. **Currencies**: Add currencies you use (INR, USD, EUR, etc.)
3. **Regions**: Add regions/countries for your investments
4. **Income Sources**: Define your income streams (Salary, Freelance, etc.)
5. **Expense Categories**: Set up expense categories (Utilities, Groceries, etc.)
6. **Investment Categories**: Automatically configured (Stocks, MF, Gold, etc.)

Note: A scheduler script runs every hour to take the DB backup, if you restart the application before that scripts takes
the backup, your data will not be restored. keep this in mind and change the scheduler script to take frequent backups.

## Configuration

### Environment Variables

The `.env` file contains all configuration. See `.env.example` for a complete template with descriptions.

**Critical Variables:**

| Variable                  | Description               | Example               | Required |
|---------------------------|---------------------------|-----------------------|----------|
| `MYSQL_ROOT_PASSWORD`     | MySQL root password       | `SecurePass123!`      | Yes      |
| `MYSQL_DATABASE`          | Database name             | `personal_finance_db` | Yes      |
| `MYSQL_USER`              | Database user             | `finance_user`        | Yes      |
| `MYSQL_PASSWORD`          | User password             | `UserPass456!`        | Yes      |
| `EXCHANGE_RATE_API_KEY`   | Currency exchange API key | `abc123...`           | Yes      |
| `RAPID_API_MF_HOST`       | Mutual fund data API host | `DEMO123...`          | Yes      |
| `RAPID_MF_API_KEY`        | Mutual fund data API key  | `DEMO123...`          | Yes      |
| `RAPID_API_BULLION_HOST`  | Bullion data API host     | `DEMO123...`          | Yes      |
| `RAPID_API_KEY`           | Bullion data API key      | `DEMO123...`          | Yes      |
| `COIN_MARKET_URL`         | crypto data API host      | `DEMO123...`          | Yes      |
| `COIN_MARKET_CAP_API_KEY` | crypto data API key       | `DEMO123...`          | Yes      |

### Configuration Files

#### `stock-score-config.json`

Defines scoring strategies for stock screening:

- **Core**: Stable, high-quality blue-chip stocks
- **Accelerators**: Fast-growing, consistent performers
- **Gem**: High-potential small/mid-cap stocks

**Configuring via UI**: Navigate to **Configurations > Stock Scoring Strategy**

**Configuring via JSON**: Edit `frontend/stock-score-config.json` directly. Each strategy has weighted metrics (ROCE,
ROI, PE, etc.) that determine stock scores.

#### `portfolio-config.json`

Defines target asset allocation and rebalancing rules:

- Asset allocation targets (e.g., 20% ETFs, 15% Stocks, 10% Gold)
- Monthly SIP amounts
- Rebalancing thresholds
- Specific holdings per category

**Configuring via UI**: Navigate to **Configurations > Portfolio Allocation**

**Configuring via JSON**: Edit `frontend/portfolio-config.json` directly.

### Validating Your Configuration

Run the validation script to check your environment:

```bash
python scripts/validate_env.py
```

This will verify all required variables are set and properly formatted.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         User Browser                        │
└────────────────────────────┬────────────────────────────────┘
                             │
                             │ HTTP/HTTPS
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                 Next.js Frontend (Port 3000)                │
│  ┌──────────────┐  ┌───────────────┐  ┌──────────────┐      │
│  │  Dashboard   │  │  Transactions │  │  Analytics   │      │
│  │    Pages     │  │     Pages     │  │    Pages     │      │
│  └──────────────┘  └───────────────┘  └──────────────┘      │
│                                                             │
│  API Proxy (/api/* → http://backend:8000/api/*)             │
└────────────────────────────┬────────────────────────────────┘
                             │
                             │ Internal Network
                             ▼
┌─────────────────────────────────────────────────────────────┐
│              FastAPI Backend (Port 8000)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │     API      │  │  Business    │  │  Background  │       │
│  │   Routes     │  │    Logic     │  │   Tasks      │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│                                                             │
│  External integrations: RapidAPI,ExchangeRateAPI,           |
|  CoinMarketCap                                              │
└───────┬────────────────────────────────┬────────────────────┘
        │                                │
        │                                │
        ▽                                ▽
┌─────────────────┐              ┌─────────────────┐
│  MySQL DB       │              │  Redis Cache    │
│  (Port 3399)    │              │  (Port 6379)    │
│                 │              │                 │
│  - Transactions │              │  - Stock Data   │
│  - Investments  │              │  - Analytics    │
│  - User Data    │              │  - API Cache    │
└─────────────────┘              └─────────────────┘
        │
        │ Backups (Cron)
        ▼
┌─────────────────┐
│  Scheduler      │
│  (Ofelia)       │
│                 │
│  - Daily Backup │
│  - Data Refresh │
└─────────────────┘
```

**Component Breakdown:**

- **Frontend (Next.js)**: React-based UI with server-side rendering
- **Backend (FastAPI)**: Python REST API with async support
- **Database (MySQL)**: Persistent storage for all financial data
- **Cache (Redis)**: High-speed caching for market data and analytics
- **Scheduler (Ofelia)**: Automated tasks (backups, data fetching)

## Usage Guide

### Adding Transactions

1. Click **+ New Transaction** button
2. Select tab: Income, Expense, or Investment
3. Fill in the form:
    - User
    - Currency
    - Amount
    - Category/Source
    - Date
4. Click **Save**

**Pro tip**: Use the **Import CSV** feature to bulk-import bank statements!

### Importing Bank Statements

1. Click **Import CSV** button
2. Select user and bank (HDFC, ICICI, SBI, etc.)
3. Upload CSV file
4. **Review** parsed transactions
5. **Edit categories** if needed (auto-learning enabled will remember your choices!)
6. Click **Confirm & Import**

### Viewing Analytics

- **Dashboard**: Overview of net worth, investment breakdown, recent activity
- **Portfolio**: Detailed portfolio analysis with allocation pie chart
- **Screen & Discover**:
    - **Invested**: Scores for stocks you already own
    - **Candidates**: Discover new investment opportunities
- **Investment Breakdown**: Category-wise analysis with XIRR and returns

### Managing Configurations

- **Supporting Data**: Add master data (users, currencies, categories)
- **Portfolio Allocation**: Set target asset allocation
- **Stock Scoring**: Customize stock screening criteria
- **Environment Config**: Manage API keys (view only from UI)
- **Theme**: Switch between Bronze, Light Purple, and Anime themes

## Development

### Running Locally (Without Docker)

#### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

#### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Project Structure

```
personal_finance/
├── backend/             # FastAPI backend
│   ├── models/          # SQLAlchemy database models
│   ├── routes/          # API endpoints
│   ├── services/        # Business logic
│   ├── schemas/         # Pydantic request/response schemas
│   └── main.py          # Application entry point
├── frontend/            # Next.js frontend
│   ├── src/
│   │   ├── app/         # Next.js 13+ app directory
│   │   └── components/  # React components
│   ├── stock-score-config.json
│   └── portfolio-config.json
├── utilities/           # Shared utilities
│   ├── analytics/       # Analytics calculators
│   ├── common/          # Common utilities
│   └── dashboard/       # Dashboard helpers
├── scripts/             # Data fetching scripts
├── docker-compose.*.yml # Docker configurations
└── start_application.robot  # Startup script
```

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests (if implemented)
cd frontend
npm test
```

## Troubleshooting

### Common Issues

**Issue**: Application won't start - "Can't connect to MySQL"

**Solution**:

1. Check `.env` file has correct database credentials
2. Ensure infrastructure is running: `docker-compose -f docker-compose.infra.yml ps`
3. Wait 30 seconds after starting database before starting app

---

**Issue**: API calls return 404 or CORS errors

**Solution**:

1. Verify backend is running on port 8000
2. Check `next.config.js` rewrites are configured
3. Restart frontend: `docker-compose -f docker-compose.app.yml restart frontend`

---

**Issue**: "Missing API key" errors

**Solution**:

1. Run `python scripts/validate_env.py` to check configuration
2. Ensure `.env` file has all required API keys
3. Get free keys from:
    - Exchange Rate API: https://www.exchangerate-api.com/
    - RapidAPI: https://rapidapi.com/
    - Coin Market Cap: https://coinmarketcap.com/api/

---

**Issue**: Database backup not working

**Solution**:

```bash
cd backup_config
chmod +x backup.sh
docker exec database /backup.sh
```

---

**Issue**: Import CSV not working

**Solution**:

1. Ensure your bank is supported (check `backend/configurations/bank_config.py`)
2. Verify CSV format matches expected format
3. Check backend logs: `docker logs mera_paisa`

## Contributing

Contributions are welcome! Please follow these guidelines:

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Commit** your changes: `git commit -m 'Add amazing feature'`
4. **Push** to the branch: `git push origin feature/amazing-feature`
5. **Open** a Pull Request

### Code Style

- **Python**: Follow PEP 8, use Black formatter
- **TypeScript/JavaScript**: Follow Airbnb style guide, use Prettier
- **Commits**: Use conventional commit messages

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **Rapid API** for stock/mutual fund/bullion data APIs
- **Coin Market cap** for cryptocurrency data APIs
- **Exchange Rate API** for currency conversion data
- **Next.js** and **FastAPI** communities

## Support

- **Issues**: https://github.com/yourusername/personal_finance/issues
- **Discussions**: https://github.com/yourusername/personal_finance/discussions

---

Happy tracking! 💪📊
