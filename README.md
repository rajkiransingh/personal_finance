# 💰 Personal Finance Tracker

> A comprehensive application for tracking and managing your individual personal finances with real-time data
> integration.

## 📋 Table of Contents

- Overview
- 🔧 Environment Setup
- 📝 Configuration
- 🔄 Database Backup Setup
- 🔒 Security Notes

## Overview

This application helps you track your personal finances by integrating various data sources including:

- 💱 Currency Exchange Rates - Real-time foreign exchange data
- 🥇 Bullion/Metal Rates - Current precious metal prices
- 📈 Stock Market Data - Live stock prices and market information
- 🏦 Personal Finance Management - Track expenses, income, and investments

## 🔧 Environment Setup

The application requires environment variables for database configuration and API integrations. Follow these steps to
set up your environment:

### Step 1: Create the Environment File

Navigate to your project root directory and create a `.env` file:

```markdown
#! bash
touch .env 
```

### Step 2: Configure Environment Variables

Copy the following template into your .env file and replace the placeholder values with your actual credentials:

```markdown
.env

# Database Configuration

MYSQL_ROOT_PASSWORD=your_root_password
MYSQL_DATABASE=your_database_name
MYSQL_USER=your_database_user
MYSQL_PASSWORD=your_user_password

# Currency Exchange Rates

EXCHANGE_API_URL="your_exchange_api_url"
EXCHANGE_RATE_API_KEY=your_exchange_api_key

# Bullion/Metal Rates

METAL_RATES_WEBSITE="your_metal_rates_website_url"

# Stock Market Data

ALPHA_VANTAGE_API_KEY=your_alpha_vantage_api_key
NSE_WEBSITE_URL="https://www.nseindia.com"
```

## 📝 Configuration

#### Database Configuration Example

```markdown
# Example database configuration

MYSQL_ROOT_PASSWORD=SecureRootPass123!
MYSQL_DATABASE=personal_finance_db
MYSQL_USER=finance_user
MYSQL_PASSWORD=UserSecurePass456!
```

#### API Configuration Example

```markdown
# Example API configuration

EXCHANGE_API_URL="https://api.exchangerate-api.com/v4/latest"
EXCHANGE_RATE_API_KEY=abcd1234567890efgh
METAL_RATES_WEBSITE="https://goldprice.org"
ALPHA_VANTAGE_API_KEY=DEMO1234567890
```

## 🔄 Database Backup Setup

The application includes automated database backup functionality. To enable this feature:
Make Backup Script Executable

Navigate to the backup configuration directory and Grant execute permissions to the backup script

```markdown
cd ~/backup_config
sudo chmod +x backup.sh
```

Verify the permissions:

```markdown
ls -la backup.sh
```

You should see something like: `-rwxr-xr-x 1 user user 1234 date backup.sh`

### Backup Features

- ✅ Automated daily backups
- ✅ Compressed backup files
- ✅ Retention policy (keeps last 4 backups)
- ✅ Error logging and monitoring

## 🔒 Security Notes

> ⚠️ Important Security Guidelines

### Environment File Security

- 🚫 Never commit .env files to version control
- 🔐 Use strong passwords for all database credentials
- 🗂️ Add .env to .gitignore to prevent accidental commits
- 👥 Don't share environment files or credentials

#### Recommended `.gitignore` Entry

Add this line to your `.gitignore` file:

```markdown
# Environment variables

.env
.env.local
.env.*.local
```

## Best Practices

- 🔄 Rotate API keys regularly
- 📝 Document which APIs require keys
- 🧪 Use separate credentials for development and production
- 🔍 Monitor API usage and quotas

## 📦 Installation Guide

Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git

#### Step 1: Install Python and pip

On Ubuntu/Debian:

```markdown
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

On macOS:

```markdown
# Using Homebrew

brew install python3

# Or download from python.org
```

On Windows:

```markdown
# Download Python from python.org

# pip comes bundled with Python 3.4+
```

#### Step 2: Clone the Repository

```markdown
# Create virtual environment

python3 -m venv finance_env

# Alternative: using virtualenv

# pip install virtualenv

# virtualenv finance_env
```

#### Step 3: Create a Virtual Environment

```markdown
# Create virtual environment

python3 -m venv finance_env

# Alternative: using virtualenv

# pip install virtualenv

# virtualenv finance_env
```

#### Step 4: Activate Virtual Environment

On Linux/macOS:

```markdown
source finance_env/bin/activate
```

On Windows:

```markdown
# Command Prompt

finance_env\Scripts\activate

# PowerShell

finance_env\Scripts\Activate.ps1
```

You should see `(finance_env)` in your terminal prompt, indicating the virtual environment is active.

#### Step 5: Install Dependencies

```markdown
# Upgrade pip first

pip install --upgrade pip

# Install project dependencies

pip install -r requirements.txt
```

#### Step 6: Verify Installation

```markdown
# Check installed packages

pip list

# Verify Python version

python --version
```

## AWS LAMBDA::

## 🚀 Getting Started

- Clone the repository
- Set up your .env file following the instructions above
- Make the backup script executable
- Install dependencies (refer to installation guide)
- Run the application

## 🤝 Contributing

When contributing to this project:

- Ensure your .env file is properly configured
- Test with your own API keys
- Don't include sensitive data in commits
- Follow the established coding standards

## 📞 Support

If you encounter issues with:

- Environment setup - Check your .env file configuration
- API connections - Verify your API keys and endpoints
- Database issues - Ensure backup script permissions are correct

Happy tracking! 💪📊