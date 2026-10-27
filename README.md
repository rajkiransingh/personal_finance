# 💰 Personal Finance Tracker

> A comprehensive full-stack application for tracking and managing your personal finances with real-time data
> integration, advanced analytics, portfolio rebalancing, and automated database backups.

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Home Server Considerations (Plex, Audiobookshelf, etc.)](#home-server-considerations-plex-audiobookshelf-etc)
- [Quick Start Guide](#quick-start-guide)
  - [1. Clone the Repository](#1-clone-the-repository)
  - [2. Set Up Python Virtual Environment](#2-set-up-python-virtual-environment)
  - [3. Configure Environment Variables (.env)](#3-configure-environment-variables-env)
  - [4. Set Up Database Backup / Golden Image](#4-set-up-database-backup--golden-image)
  - [5. Validate Environment & Readiness](#5-validate-environment--readiness)
  - [6. Start the Application](#6-start-the-application)
  - [7. Access the Application](#7-access-the-application)
  - [8. Stopping the Application](#8-stopping-the-application)
- [Configuration](#configuration)
  - [Environment Variables](#environment-variables)
  - [Port Overrides](#port-overrides)
  - [Strategy Configuration Files](#strategy-configuration-files)
- [Database Backups & Migration](#database-backups--migration)
- [Architecture](#architecture)
- [Usage Guide](#usage-guide)
- [Development (Running Locally Without Docker)](#development-running-locally-without-docker)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

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
- CSV bank statement import (HDFC, IPKO, Millennium, Alior, Axis, Revolut, SBI)
- Auto-categorization learning system
- Recurring transaction support

🎨 **Modern UI/UX**
- Multiple theme support (Bronze, Light Purple, Anime)
- Responsive design
- Interactive charts and visualizations
- Real-time data updates

---

## Prerequisites

Before setting up on Ubuntu (or any Linux distribution), ensure the following requirements are met:

### 1. Docker & Docker Compose
- **Docker**: Version 20.10 or higher
- **Docker Compose**: Docker Compose v2 plugin (`docker compose`) or standalone binary (`docker-compose`)

> [!IMPORTANT]
> **Docker Permissions**: Ensure your user account belongs to the `docker` group so Docker commands run without `sudo`:
> ```bash
> sudo usermod -aG docker $USER
> newgrp docker
> ```
> Verify access with: `docker ps`

### 2. Python 3.10+ & Virtual Environment
- **Python**: Version 3.10, 3.11, or 3.12
- **python3-venv**: Required to create the virtual environment for running the startup automation (`robot start_application.robot`)
  ```bash
  sudo apt-get update && sudo apt-get install -y python3-venv python3-pip git curl
  ```

---

## Home Server Considerations (Plex, Audiobookshelf, etc.)

If you are running this application on a shared home server (e.g., alongside **Plex**, **Audiobookshelf**, **Portainer**, **Home Assistant**, or **Grafana**), note the ports used:

| Service | Internal Container Port | Default Host Port | Common Conflicts | Custom `.env` Variable |
|---|---|---|---|---|
| **Frontend (Next.js)** | 3000 | `3000` | Grafana, AdGuard Home, Audiobookshelf | `FRONTEND_PORT` |
| **Backend (FastAPI)** | 8000 | `8000` | Portainer Agent, Audiobookshelf, media services | `BACKEND_PORT` |
| **Database (MySQL)** | 3306 | `3399` | Other MySQL / MariaDB instances | `DB_PORT` |
| **Redis Cache** | 6379 | `6379` | System Redis instance | `REDIS_HOST_PORT` |

### Check for Port Conflicts
Before starting, check if ports `3000`, `8000`, `3399`, or `6379` are currently in use on your server:
```bash
sudo ss -tulpn | grep -E ':(3000|8000|3399|6379)'
```

### Resolving Port Collisions
If port 8000 or 3000 is already in use by Plex companions, Audiobookshelf, or other server tools, simply configure alternate ports in your `.env` file without altering Docker files:
```env
FRONTEND_PORT=3005
BACKEND_PORT=8008
DB_PORT=3398
REDIS_HOST_PORT=6380
```
Internal container communication (backend to database, frontend to backend proxy) uses Docker internal networks and remains untouched.

---

## Quick Start Guide

Follow these steps when setting up the project on a newly cloned Ubuntu machine:

### 1. Clone the Repository

```bash
git clone https://github.com/rajkiransingh/personal_finance.git
cd personal_finance
```

### 2. Set Up Python Virtual Environment

The startup automation script (`start_application.robot`) uses Robot Framework, which runs in a Python environment. Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

> [!NOTE]
> Always ensure your virtual environment is active (`source .venv/bin/activate`) before running `robot start_application.robot` or `python scripts/validate_env.py`.

### 3. Configure Environment Variables (.env)

If you are migrating from another machine, copy your existing `.env` file to the root of the project:
```bash
# If copying existing .env from another machine:
cp /path/to/copied/.env .env

# Or if configuring fresh from the template:
cp .env.example .env
```

Edit `.env` and verify your credentials and API keys (see [Configuration](#configuration)).

### 4. Set Up Database Backup / Golden Image

The application database schema and initial master data are populated from database backups.

1. Ensure the backup directory exists (created automatically if missing):
   ```bash
   mkdir -p backup_config/db_backups
   ```

2. Copy your database backup file (`.sql.gz` or `.sql`) into `backup_config/db_backups/`:
   ```bash
   cp /path/to/dbbackup_GOLDEN_*.sql.gz backup_config/db_backups/
   ```

> [!TIP]
> **How Automatic Backup Restore Works**:
> - **Migration / Clean Clone**: If you only place a golden backup (e.g., `dbbackup_GOLDEN_20261010.sql.gz`), the startup script automatically detects and restores the golden image.
> - **Regular Restarts**: If newer timestamped backups exist (e.g., `dbbackup_20261020_140000.sql.gz` created by the hourly backup scheduler), the script restores the latest timestamped backup so you never lose recent changes.

### 5. Validate Environment & Readiness

Run the built-in validation script to verify your `.env` settings, port definitions, backup presence, and configuration templates:

```bash
python scripts/validate_env.py
```

Expected output:
```text
✓ .env file found
✓ All required environment variables are configured!
✓ Found database backup(s) in backup_config/db_backups
✓ Bank config found at backend/configurations/bank_config.py
✓ Your environment is ready to use.
```

### 6. Start the Application

Start all services (Infrastructure, Database, Cache, Scheduler, Backend, and Frontend) using Robot Framework:

```bash
robot start_application.robot
```

The script will automatically:
1. Verify Docker and Docker Compose (supports both `docker-compose` and `docker compose`)
2. Ensure local directories (`backup_config/db_backups/`, `logs/`) and permissions
3. Ensure required Docker bridge networks exist (`personal_finance_network`, `intra_connect`)
4. Create the Docker persistent data volume (`personal_finance_data_volume`)
5. Build backend and frontend images if source files changed
6. Launch database and Redis containers
7. Wait for MySQL to become fully ready
8. Restore the latest database backup (golden or timestamped)
9. Launch FastAPI backend and Next.js frontend
10. Health check the frontend and report accessibility URLs

#### Starting Manually via Docker Compose (Alternative)

If you prefer using Docker Compose directly without Robot Framework:

```bash
# Ensure networks and volume exist
docker network create personal_finance_network 2>/dev/null || true
docker network create intra_connect 2>/dev/null || true
docker volume create personal_finance_data_volume 2>/dev/null || true

# 1. Start infrastructure (MySQL, Redis, Ofelia Scheduler)
docker compose -f docker-compose.infra.yml up -d

# 2. Wait ~30 seconds for MySQL to be healthy
docker exec -it database mysqladmin ping -h localhost -u root -p${MYSQL_ROOT_PASSWORD}

# 3. Restore your backup if initial setup
# (Replace with your actual backup filename)
gunzip -c backup_config/db_backups/dbbackup_GOLDEN_*.sql.gz | docker exec -i database mysql -u root -p${MYSQL_ROOT_PASSWORD} personal_finance_db

# 4. Start backend and frontend
docker compose -f docker-compose.app.yml up -d
```

### 7. Access the Application

- **Frontend**: http://localhost:3000 (or `http://<your-server-ip>:3000`)
- **Backend API**: http://localhost:8000 (or `http://<your-server-ip>:8000`)
- **Interactive API Docs (Swagger)**: http://localhost:8000/docs

### 8. Stopping the Application

To cleanly stop all application and infrastructure containers:

```bash
robot stop_application.robot
```

Or via Docker Compose:
```bash
docker compose -f docker-compose.app.yml down
docker compose -f docker-compose.infra.yml down
```

---

## Configuration

### Environment Variables

The `.env` file contains all configuration. See `.env.example` for the complete template with descriptions.

**Critical Variables:**

| Variable | Description | Example | Required |
|---|---|---|---|
| `MYSQL_ROOT_PASSWORD` | MySQL root password | `SecurePass123!` | Yes |
| `MYSQL_DATABASE` | Database name | `personal_finance_db` | Yes |
| `MYSQL_USER` | Database user | `finance_user` | Yes |
| `MYSQL_PASSWORD` | User password | `UserPass456!` | Yes |
| `DATABASE_URL` | Database connection URL | `mysql+pymysql://finance_user:UserPass456!@db:3306/personal_finance_db` | Yes |
| `EXCHANGE_RATE_API_KEY` | Currency exchange API key | `abc123...` | Yes ([Free Key](https://www.exchangerate-api.com/)) |
| `RAPID_API_MF_HOST` | Mutual fund data API host | `nav-indian-mutual-fund.p.rapidapi.com` | Yes |
| `RAPID_MF_API_KEY` | Mutual fund data API key | `rapid_key_here` | Yes ([RapidAPI](https://rapidapi.com/)) |
| `RAPID_API_BULLION_HOST` | Bullion data API host | `gold-silver-live-price-india.p.rapidapi.com` | Yes |
| `RAPID_API_KEY` | Bullion data API key | `rapid_key_here` | Yes ([RapidAPI](https://rapidapi.com/)) |
| `COIN_MARKET_URL` | Crypto data API URL | `https://pro-api.coinmarketcap.com/v1/...` | Yes |
| `COIN_MARKET_CAP_API_KEY` | Crypto data API key | `coinmarketcap_key` | Yes ([CoinMarketCap](https://coinmarketcap.com/api/)) |

### Port Overrides

To customize host ports and avoid clashes on shared servers, add these optional variables to `.env`:

```env
FRONTEND_PORT=3000      # Next.js web interface
BACKEND_PORT=8000       # FastAPI backend API
DB_PORT=3399            # Host access to MySQL
REDIS_HOST_PORT=6379    # Host access to Redis
```

### Strategy Configuration Files

#### `frontend/stock-score-config.json`
Defines scoring strategies for stock screening:
- **Core**: High-quality blue-chip stocks
- **Accelerators**: Growth performers
- **Gem**: Small/mid-cap momentum stocks

*Configurable via UI*: **Configurations > Stock Scoring Strategy**

#### `frontend/portfolio-config.json`
Defines target asset allocation, monthly SIP targets, and rebalancing thresholds.

*Configurable via UI*: **Configurations > Portfolio Allocation**

#### `backend/configurations/bank_config.py`
Defines bank statement CSV column mappings (date, description, amount) and automatic categorization rules. Auto-initialized from `backend/configurations/bank_config.py.example` on first run.

---

## Database Backups & Migration

### Automated Backups
The **Ofelia scheduler** container runs automated database backups every hour and saves compressed `.sql.gz` snapshots to:
```
backup_config/db_backups/dbbackup_YYYYMMDD_HHMMSS.sql.gz
```

### Creating a Manual Backup
To create a manual backup anytime:
```bash
chmod +x backup_config/backup.sh
docker exec database /backup.sh
```

### Creating a Golden Image
When you have configured your master data and transactions and want to create a baseline golden image:
```bash
docker exec database /backup.sh
# Copy latest backup as a golden backup:
LATEST=$(ls -t backup_config/db_backups/dbbackup_*.sql.gz | head -1)
cp "$LATEST" "backup_config/db_backups/dbbackup_GOLDEN_$(date +%Y%m%d).sql.gz"
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         User Browser                        │
└────────────────────────────┬────────────────────────────────┘
                             │
                             │ HTTP/HTTPS (Port 3000 / FRONTEND_PORT)
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
                             │ Internal Network (personal_finance_network)
                             ▼
┌─────────────────────────────────────────────────────────────┐
│              FastAPI Backend (Port 8000)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │     API      │  │  Business    │  │  Background  │       │
│  │   Routes     │  │    Logic     │  │   Tasks      │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│                                                             │
│  External integrations: RapidAPI, ExchangeRateAPI,          │
│  CoinMarketCap                                              │
└───────┬────────────────────────────────┬────────────────────┘
        │                                │
        │ Internal Network               │ Internal Network
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
        │ Hourly Backup Volume
        ▼
┌────────────────────────────────┐
│  Scheduler (Ofelia)            │
│  - Periodic DB Backups (.gz)   │
│  - Data Refresh Tasks          │
└────────────────────────────────┘
```

---

## Usage Guide

### Adding Transactions
1. Click **+ New Transaction** button
2. Select tab: **Income**, **Expense**, or **Investment**
3. Fill in user, currency, amount, category/source, and date
4. Click **Save**

### Importing Bank Statements
1. Click **Import CSV**
2. Select user and bank profile (HDFC, ICICI, SBI, IPKO, Millennium, Alior, Revolut, etc.)
3. Upload statement CSV
4. Review auto-categorized transactions and confirm import (the learning system saves updated category mappings)

### Analytics & Rebalancing
- **Dashboard**: Net worth trend, asset allocation pie charts, recent activity
- **Portfolio**: Real-time value, invested amount, profit/loss, XIRR calculations
- **Screen & Discover**: Stock scores (Core, Accelerators, Gem) based on financial metrics
- **Rebalancing Screener**: Automatic suggestions to align current portfolio with target allocations

---

## Development (Running Locally Without Docker)

If you prefer developing locally without Docker containers:

### 1. Start Infrastructure
Run MySQL and Redis in Docker while developing the backend and frontend locally:
```bash
docker compose -f docker-compose.infra.yml up -d
```

### 2. Backend Setup
```bash
# In project root:
source .venv/bin/activate
# Note: When connecting to Docker MySQL from host, use localhost:3399
export DATABASE_URL="mysql+pymysql://${MYSQL_USER}:${MYSQL_PASSWORD}@localhost:3399/${MYSQL_DATABASE}"
export REDIS_HOST="localhost"
python common_logging_startup.py
```
Backend runs at `http://localhost:8000`.

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Frontend runs at `http://localhost:3000`.

---

## Troubleshooting

### 1. Database Has 0 Tables or "Table doesn't exist"
- **Cause**: MySQL started with an empty database and no backup was restored.
- **Solution**:
  1. Check if your backup file exists in `backup_config/db_backups/`.
  2. Verify the filename ends with `.sql.gz` or `.sql` (e.g., `dbbackup_GOLDEN_20261010.sql.gz`).
  3. Run `python scripts/validate_env.py` to confirm the backup is recognized.
  4. Run `robot start_application.robot`, which will restore the golden backup automatically.

### 2. Port Collision ("port is already allocated" / "bind: address already in use")
- **Cause**: Existing applications on your server (Plex companion tools, Audiobookshelf, Portainer, Grafana) are using port 3000 or 8000.
- **Solution**:
  1. Check what is using the port:
     ```bash
     sudo ss -tulpn | grep -E ':(3000|8000|3399|6379)'
     ```
  2. In `.env`, configure alternate ports:
     ```env
     FRONTEND_PORT=3005
     BACKEND_PORT=8008
     ```
  3. Restart with `robot start_application.robot`.

### 3. Docker Permission Denied ("Got permission denied while trying to connect to Docker daemon")
- **Cause**: Your user is not in the `docker` group.
- **Solution**:
  ```bash
  sudo usermod -aG docker $USER
  newgrp docker
  ```

### 4. `robot: command not found`
- **Cause**: The Python virtual environment is not activated or `requirements.txt` is not installed.
- **Solution**:
  ```bash
  source .venv/bin/activate
  pip install -r requirements.txt
  ```

### 5. Docker Build Fails: `stat app/public: file does not exist`
- **Cause**: The `frontend/public` directory was missing or excluded by git.
- **Solution**:
  Verify `frontend/public/` exists with `ls -la frontend/public/`. If missing, recreate:
  ```bash
  git checkout -- frontend/public/
  ```

### 6. Permission Denied on `logs/application.log`
- **Cause**: Docker ran as root and created `logs/` owned by `root`.
- **Solution**:
  ```bash
  sudo chown -R $USER:$USER logs/ backup_config/
  ```

### 7. Backup Script Not Executable
- **Cause**: Shell scripts in `backup_config/` lost executable permissions during git clone.
- **Solution**:
  ```bash
  chmod +x backup_config/*.sh
  ```

---

## Contributing

Contributions are welcome! Please follow these guidelines:

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Commit** your changes: `git commit -m 'Add amazing feature'`
4. **Push** to the branch: `git push origin feature/amazing-feature`
5. **Open** a Pull Request

---

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **Rapid API** for stock, mutual fund, and bullion market rates
- **Coin Market Cap** for cryptocurrency rates
- **Exchange Rate API** for global forex conversion
- **Next.js** and **FastAPI** open-source communities
