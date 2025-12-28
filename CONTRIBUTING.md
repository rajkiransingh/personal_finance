# Contributing to Personal Finance Tracker

Thank you for considering contributing to Personal Finance Tracker! This document provides guidelines and best practices
for contributing to the project.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Submit Contribution](#submitting-contributions)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Enhancements](#suggesting-enhancements)

## Code of Conduct

This project follows a simple code of conduct:

- Be respectful and inclusive
- Focus on constructive feedback
- Help others when you can
- Keep discussions professional and on-topic

## How Can I Contribute?

### Types of Contributions

We welcome various types of contributions:

- 🐛 **Bug Reports**: Help us identify and fix issues
- ✨ **Feature Requests**: Suggest new features or improvements
- 📝 **Documentation**: Improve or expand documentation
- 💻 **Code Contributions**: Fix bugs or implement features
- 🌐 **Translations**: Add support for new languages
- 🧪 **Testing**: Write tests to improve code coverage

## Development Setup

### Prerequisites

- Docker and Docker Compose
- Git
- Python 3.10+ (for local development)
- Node.js 18+ (for local development)

### Setting Up Your Development Environment

1. **Fork and Clone**

```bash
git clone https://github.com/rajkiransingh/personal_finance.git
cd personal_finance
```

2. **Configure Environment**

```bash
cp .env.example .env
```

3. **Start Development Environment**

```bash
# Using Docker
robot start_application.robot

# Or manually:
docker-compose -f docker-compose.infra.yml up -d
docker-compose -f docker-compose.app.yml up -d
```

4. **Verify Setup**

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/docs

### Local Development Without Docker

**Backend:**

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn backend.main:app --reload --log-level debug --port 8000
```

**Frontend:**

```bash
cd frontend
npm install
npm run dev
```

## Coding Standards

### Python (Backend)

- **Style Guide**: PEP 8
- **Formatter**: Black
- **Linter**: Ruff
- **Type Hints**: Use type hints for all function signatures

**Example:**

```python
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session


async def get_transactions(
        db: Session = Depends(get_db),
        limit: int = 100
) -> List[Transaction]:
    """
    Fetch recent transactions from database.

    Args:
        db: Database session
        limit: Maximum number of transactions to return

    Returns:
        List of Transaction objects
    """
    return db.query(Transaction).limit(limit).all()
```

**Before Committing:**

```bash
# Format code
black backend/

# Check linting
ruff check backend/
```

### TypeScript/JavaScript (Frontend)

- **Style Guide**: Airbnb JavaScript Style Guide
- **Formatter**: Prettier
- **Framework**: Next.js 13+ (App Router)
- **State Management**: React Context + hooks

**Example:**

```typescript
"use client";

import { useState, useEffect } from "react";

interface Transaction {
  id: number;
  amount: number;
  date: string;
}

export default function TransactionsList() {
  const [transactions, setTransactions] = useState<Transaction[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      const response = await fetch("/api/transactions");
      const data = await response.json();
      setTransactions(data);
    };

    fetchData();
  }, []);

  return (
    <div>
      {transactions.map((txn) => (
        <div key={txn.id}>{txn.amount}</div>
      ))}
    </div>
  );
}
```

**Before Committing:**

```bash
# Format code
npm run format

# Type checking
npm run type-check
```

### Commit Messages

Follow **Conventional Commits** specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Build process or auxiliary tool changes

**Examples:**

```
feat(transactions): add CSV import feature

- Implement CSV parser for bank statements
- Add preview modal before importing
- Support HDFC, ICICI, and SBI formats

Closes #123
```

```
fix(api): resolve CORS issue with /api proxy

Update next.config.js rewrites configuration to properly
handle API proxy requests.

Fixes #456
```

## Submitting Contributions

### Pull Request Process

1. **Create a Branch**

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

2. **Make Your Changes**

- Write clean, well-documented code
- Follow coding standards
- Add tests if applicable
- Update documentation

3. **Test Your Changes**

```bash
# Run backend tests
cd backend
pytest

# Run frontend build
cd frontend
npm run build
```

4. **Commit Your Changes**

```bash
git add .
git commit -m "feat(scope): description"
```

5. **Push and Create PR**

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub with:

- Clear title and description
- Reference related issues
- Screenshots (if UI changes)
- Testing steps

### PR Review Process

- Maintainers will review your PR
- Address any feedback or requested changes
- Once approved, your PR will be merged

## Reporting Bugs

### Before Submitting a Bug Report

1. **Check existing issues**: Your bug might already be reported
2. **Verify it's reproducible**: Ensure you can consistently reproduce the bug
3. **Test on latest version**: Make sure you're using the latest version

### Submitting a Bug Report

Create an issue with:

**Title**: Brief, descriptive summary

**Template:**

```markdown
## Bug Description

A clear description of the bug.

## Steps to Reproduce

1. Go to '...'
2. Click on '...'
3. See error

## Expected Behavior

What you expected to happen.

## Actual Behavior

What actually happened.

## Environment

- OS: [e.g., Windows 11, macOS 13]
- Browser: [e.g., Chrome 120]
- Version: [e.g., v1.0.0]

## Screenshots

If applicable, add screenshots.

## Additional Context

Any other relevant information.
```

## Suggesting Enhancements

### Before Suggesting an Enhancement

1. **Check existing feature requests**
2. **Consider if it aligns with project goals**
3. **Think about implementation complexity**

### Submitting an Enhancement Suggestion

Create an issue with:

**Title**: Brief description of enhancement

**Template:**

```markdown
## Enhancement Description

Clear description of the proposed feature.

## Motivation

Why is this enhancement needed? What problem does it solve?

## Proposed Solution

How you envision this feature working.

## Alternatives Considered

Other approaches you've thought about.

## Additional Context

Mockups, examples, or references.
```

## Development Guidelines

### Adding a New Feature

1. **Discuss First**: Open an issue to discuss the feature
2. **Plan Implementation**: Outline your approach
3. **Create Branch**: `feature/feature-name`
4. **Implement**:
    - Backend changes (if needed)
    - Frontend changes (if needed)
    - Tests
    - Documentation
5. **Submit PR**: Follow PR process above

### Adding a New API Endpoint

1. **Backend** (`backend/routes/`):

    - Create route file or add to existing
    - Define Pydantic schemas
    - Implement business logic in services
    - Add database models if needed

2. **Frontend**:
    - Use `/api` proxy for all API calls
    - Handle loading/error states
    - Add TypeScript types

**Example:**

```python
# backend/routes/example.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

router = APIRouter(prefix="/example")


@router.get("/items")
async def get_items(db: Session = Depends(get_db)):
    return {"items": []}
```

```typescript
// frontend/src/app/example/page.tsx
const fetchItems = async () => {
  const response = await fetch("/api/example/items");
  const data = await response.json();
  return data;
};
```

### Database Schema Changes

If you need to modify the database schema:

1. Update SQLAlchemy models in `backend/models/`
2. Document the change in PR description
3. Consider migration strategy for existing users

## Testing

### Backend Tests

```bash
cd backend
pytest

# With coverage
pytest --cov=backend
```

### Frontend Tests

```bash
cd frontend
npm test

# Build test
npm run build
```

## Need Help?

- 📖 **Documentation**: Check the [README](README.md) first
- 💬 **Discussions**: Use GitHub Discussions for questions
- 🐛 **Issues**: Search existing issues or create a new one

Thank you for contributing! 🎉
