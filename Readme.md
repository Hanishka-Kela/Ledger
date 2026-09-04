# Ledger

A full-stack double-entry ledger application built with **FastAPI, SQLAlchemy, PostgreSQL, React, and Vite**.

Ledger implements financial transactions using proper debit/credit accounting instead of storing mutable account balances directly. Every balance is derived from immutable ledger entries, and transactions are validated before being persisted.

The project was built primarily to explore backend architecture, authentication, authorization, database transactions, double-entry accounting, persistence, and automated testing.

---

## Features

### Authentication

- User signup
- User login
- Argon2 password hashing
- JWT access tokens
- Bearer-token authentication
- Protected API routes
- Authenticated user retrieval through `/auth/me`

### Accounts

Users can create and manage different accounting account types:

- `ASSET`
- `LIABILITY`
- `EQUITY`
- `REVENUE`
- `EXPENSE`

Each account belongs to the authenticated user.

The client never supplies `owner_id`; ownership is derived from the authenticated JWT identity.

### Double-Entry Ledger

Every financial operation is represented using ledger entries.

A transaction must:

- contain at least two entries
- contain positive amounts
- have total debits equal total credits
- reference valid accounts

Example:

```text
Debit  Cash          1,000
Credit Owner Equity  1,000
```

This represents an initial capital contribution.

The ledger does not directly mutate a stored balance. Account balances are calculated from their entries.

### Transfers

Users can transfer value from one account to another.

The service:

1. validates the source account
2. verifies source-account ownership
3. validates the destination account
4. checks the source balance
5. determines the required debit/credit entries
6. creates a balanced transaction
7. persists the transaction and entries atomically

Transfers to accounts owned by another user are supported.

### General Journal Entries

The application also exposes an advanced journal interface where users can explicitly construct debit and credit entries.

Example:

```json
{
  "description": "Owner capital",
  "entries": [
    {
      "account_id": "asset-account-uuid",
      "type": "DEBIT",
      "amount": 1000
    },
    {
      "account_id": "equity-account-uuid",
      "type": "CREDIT",
      "amount": 1000
    }
  ]
}
```

The backend remains responsible for validating whether the transaction is balanced.

### Balances

Balances are derived from ledger entries according to normal accounting rules.

| Account Type | Increase | Decrease |
|---|---|---|
| Asset | Debit | Credit |
| Expense | Debit | Credit |
| Liability | Credit | Debit |
| Equity | Credit | Debit |
| Revenue | Credit | Debit |

For example:

```text
Asset debits:   1,000
Asset credits:    300
---------------------
Balance:           700
```

### Transaction History

Users can:

- retrieve a transaction by ID
- view transaction history for one of their accounts
- inspect every debit and credit entry belonging to the transaction

Transaction histories are returned newest first.

### Authorization

Authentication answers:

> Who is making this request?

Authorization answers:

> Is this user allowed to perform this operation?

Examples:

- users may only debit accounts they own
- users cannot inspect another user's account balance
- users cannot inspect another user's account history
- users may receive transfers from other users
- a transaction may be retrieved by a user participating in that transaction

---

# Architecture

The backend uses a layered architecture:

```text
HTTP Request
     │
     ▼
FastAPI Route
     │
     ▼
Application Service
     │
     ▼
Repository
     │
     ▼
SQLAlchemy
     │
     ▼
PostgreSQL
```

The project separates API concerns, business logic, domain models, persistence, and security.

```text
src/
├── api/
│   ├── routes/
│   ├── schemas/
│   └── dependencies.py
│
├── application/
│   ├── auth_service.py
│   ├── account_service.py
│   └── ledger_service.py
│
├── domain/
│   ├── user.py
│   ├── account.py
│   ├── transaction.py
│   └── entry.py
│
├── infrastructure/
│   ├── database/
│   ├── repositories/
│   ├── security/
│   └── config.py
│
├── tests/
│   ├── api/
│   ├── application/
│   ├── domain/
│   ├── repositories/
│   └── security/
│
└── main.py
```

---

# Transaction Boundaries

Database transaction ownership follows this rule:

```text
Repository
    └── persist objects
        NO commit

Application Service
    └── business logic
        NO commit

API Route
    └── commit / rollback
```

This is particularly important for double-entry posting.

A transaction and all of its entries must succeed together:

```text
Transaction
   +
Debit Entry
   +
Credit Entry
```

If persistence fails midway, the API rolls the operation back rather than leaving a partially written ledger.

---

# Frontend

The project includes a React frontend under:

```text
frontend/
```

The frontend is built using:

- React
- React Router
- Vite
- JavaScript
- CSS

No large UI or state-management framework is required.

## Pages

The application currently contains:

```text
/login
/signup
/dashboard
/accounts
/accounts/:accountId
/transfer
/journal
/transactions/:transactionId
```

### Dashboard

Displays:

- authenticated user
- accounts
- account types
- current balances
- navigation to common ledger operations

### Accounts

Allows users to:

- list their accounts
- create accounts
- inspect account balances
- open account transaction histories

### Transfer

Allows a user to choose one of their accounts as the source and transfer value to another account UUID.

### Journal

Provides direct access to the general double-entry journal interface.

This page is intended as the advanced accounting interface rather than a simplified consumer banking workflow.

### Transaction Detail

Displays:

- transaction ID
- description
- timestamp
- debit entries
- credit entries
- account IDs
- amounts

---

# Frontend API Architecture

Frontend API calls are centralized under:

```text
frontend/src/api/
├── client.js
├── auth.js
├── accounts.js
└── transactions.js
```

`client.js` handles:

- API base URL configuration
- JWT attachment
- JSON parsing
- backend error parsing
- expired/invalid authentication handling

The JWT is stored in browser `localStorage` under the frontend authentication layer.

Authoritative user information is still retrieved from:

```text
GET /auth/me
```

rather than being inferred by decoding the JWT on the frontend.

---

# Technology Stack

## Backend

- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- Pydantic
- PyJWT
- Argon2
- python-dotenv
- pytest

## Frontend

- React
- React Router
- Vite
- JavaScript
- CSS

## Development

- Git
- GitHub
- PostgreSQL
- FastAPI Swagger/OpenAPI

---

# API

The backend runs locally at:

```text
http://localhost:8000
```

Interactive API documentation is available at:

```text
http://localhost:8000/docs
```

---

## Authentication

### Create user

```http
POST /auth/signup
```

Example:

```json
{
  "email": "user@example.com",
  "password": "Password123!",
  "confirm_password": "Password123!"
}
```

Successful response:

```text
201 Created
```

---

### Login

```http
POST /auth/login
```

Example:

```json
{
  "email": "user@example.com",
  "password": "Password123!"
}
```

Response:

```json
{
  "access_token": "<JWT>",
  "token_type": "bearer"
}
```

Authenticated requests use:

```http
Authorization: Bearer <JWT>
```

---

### Current user

```http
GET /auth/me
```

Requires authentication.

---

# Accounts

### Create account

```http
POST /accounts
```

Example:

```json
{
  "name": "Cash",
  "account_type": "ASSET"
}
```

Successful response:

```text
201 Created
```

The authenticated user automatically becomes the owner.

---

### List accounts

```http
GET /accounts
```

Returns accounts owned by the authenticated user.

---

### Account balance

```http
GET /accounts/{account_id}/balance
```

Example response:

```json
{
  "account_id": "uuid",
  "balance": 700
}
```

---

### Account transactions

```http
GET /accounts/{account_id}/transactions
```

Returns transactions containing entries for the requested account.

---

# Transactions

### Create transfer

```http
POST /transactions
```

Example:

```json
{
  "source_account_id": "uuid",
  "destination_account_id": "uuid",
  "amount": 300,
  "description": "Transfer"
}
```

Successful response:

```text
201 Created
```

For an Asset-to-Asset transfer, the resulting entries are typically:

```text
Source       CREDIT  300
Destination  DEBIT   300
```

---

### Create journal transaction

```http
POST /transactions/journal
```

Example:

```json
{
  "description": "Opening capital",
  "entries": [
    {
      "account_id": "asset-account-uuid",
      "type": "DEBIT",
      "amount": 1000
    },
    {
      "account_id": "equity-account-uuid",
      "type": "CREDIT",
      "amount": 1000
    }
  ]
}
```

Successful response:

```text
201 Created
```

---

### Retrieve transaction

```http
GET /transactions/{transaction_id}
```

A user may retrieve the transaction when they own at least one account referenced by its entries.

---

# Running Locally

## 1. Clone the repository

```bash
git clone <your-repository-url>
cd Ledger
```

---

## 2. Create a Python virtual environment

```bash
python -m venv venv
```

Activate it on macOS/Linux:

```bash
source venv/bin/activate
```

Windows:

```bash
venv\Scripts\activate
```

---

## 3. Install backend dependencies

The backend requires FastAPI, SQLAlchemy, PostgreSQL support, authentication libraries, and testing dependencies.

```bash
pip install fastapi uvicorn sqlalchemy pydantic email-validator python-dotenv argon2-cffi PyJWT "psycopg[binary]" pytest httpx
```

For a public repository, generating and committing a dependency file is recommended:

```bash
pip freeze > requirements.txt
```

Then future installations can use:

```bash
pip install -r requirements.txt
```

---

# PostgreSQL Setup

Make sure PostgreSQL is running.

Open PostgreSQL:

```bash
psql postgres
```

Create the database:

```sql
CREATE DATABASE ledger;
```

Exit:

```sql
\q
```

---

# Backend Environment Variables

Create a `.env` file in the project root.

Example:

```env
JWT_SECRET_KEY=replace-with-a-long-random-secret
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
DATABASE_URL=postgresql+psycopg://postgres-user@localhost:5432/ledger
```

For example, on a local PostgreSQL installation:

```env
DATABASE_URL=postgresql+psycopg://your_username@localhost:5432/ledger
```

Do not commit the real `.env` file.

---

# Initialize the Database

Run:

```bash
python -m src.infrastructure.database.init_db
```

The initializer registers the ORM models and creates the database tables through SQLAlchemy.

Expected tables:

```text
users
accounts
transactions
entries
```

---

# Run the Backend

```bash
uvicorn src.main:app --reload
```

Backend:

```text
http://localhost:8000
```

Swagger:

```text
http://localhost:8000/docs
```

---

# Run the Frontend

Open another terminal:

```bash
cd frontend
```

Install packages:

```bash
npm install
```

Copy the environment example:

```bash
cp .env.example .env
```

The development configuration uses:

```env
VITE_API_BASE_URL=/api
```

Run:

```bash
npm run dev
```

Vite proxies `/api` requests to:

```text
http://localhost:8000
```

so the frontend can communicate with the local backend without modifying backend CORS configuration.

---

# Production Frontend Build

Run:

```bash
cd frontend
npm run build
```

The production files are generated under:

```text
frontend/dist/
```

For deployment, configure:

```env
VITE_API_BASE_URL=<public-api-url>
```

at build time.

The current backend does not configure browser CORS directly, so a same-origin reverse proxy is the simplest deployment architecture unless CORS is configured separately.

Example:

```text
Browser
   │
   ▼
example.com
   │
   ├── /            → React frontend
   │
   └── /api/*       → FastAPI
                         │
                         ▼
                     PostgreSQL
```

---

# Testing

Run the complete backend test suite from the project root:

```bash
python -m pytest
```

Current verified result:

```text
94 passed
```

The test suite covers multiple layers of the application.

### Domain

- ORM relationships
- transaction validation
- debit/credit behavior

### Security

- password hashing
- password verification
- JWT creation
- JWT validation

### Repositories

- user persistence
- account persistence
- transaction persistence
- entry persistence

### Application Services

- signup
- login
- account creation
- authorization
- balance calculation
- journal posting
- transfers
- transaction retrieval

### API

- authentication requirements
- account creation
- account listing
- balances
- transfers
- cross-user transfers
- insufficient funds
- missing accounts
- authorization
- journal validation
- transaction retrieval
- account transaction history
- rollback behavior

The rollback test verifies that a persistence failure does not leave a partial transaction or only one side of a double-entry operation in the database.

---

# Example Ledger Flow

A user creates:

```text
Cash          ASSET
Owner Equity  EQUITY
```

To add initial capital:

```text
Debit  Cash          1,000
Credit Owner Equity  1,000
```

Balances:

```text
Cash          1,000
Owner Equity  1,000
```

This does **not** mean there is 2,000 in cash.

It represents the accounting equation:

```text
Assets = Liabilities + Equity

1,000 = 0 + 1,000
```

If 300 is moved from Cash to another Asset account:

```text
Credit Cash  300
Debit  Bank  300
```

Balances become:

```text
Cash           700
Bank           300
Owner Equity 1,000
```

and the ledger remains balanced.

---

# Important Design Decisions

## Balances are derived

The database does not treat the balance as an independently mutable source of truth.

Instead:

```text
Account
   │
   ▼
Ledger Entries
   │
   ▼
Debit/Credit Calculation
   │
   ▼
Balance
```

This reduces the risk of the account balance becoming inconsistent with its transaction history.

## Identity comes from JWT

Endpoints do not trust client-supplied ownership information.

```text
JWT
 │
 ▼
get_current_user()
 │
 ▼
current_user.user_id
 │
 ▼
authorization
```

## Atomic ledger writes

Repositories and services do not individually commit ledger entries.

The API controls the transaction boundary so that:

```text
transaction + debit + credit
```

either all persist or all roll back.

## Cross-user transfers

The source account must belong to the requester.

The destination account only needs to exist.

This allows legitimate transfers between users without allowing one user to spend another user's funds.

---

# HTTP Status Conventions

| Situation | Status |
|---|---:|
| Resource created | `201` |
| Successful retrieval | `200` |
| Invalid business operation | `400` |
| Missing/invalid authentication | `401` |
| Authenticated but unauthorized | `403` |
| Resource not found | `404` |

---

# Current Scope

The project intentionally focuses on ledger fundamentals rather than attempting to implement an entire banking platform.

Included:

- authentication
- account ownership
- double-entry transactions
- journal entries
- transfers
- balances
- transaction history
- PostgreSQL persistence
- full-stack UI
- automated tests

Not currently included:

- payment-gateway integration
- real bank deposits or withdrawals
- currency conversion
- refresh tokens
- role-based administration
- database migrations
- production monitoring
- background jobs
- reconciliation with external financial institutions

The Journal interface also exposes accounting concepts directly and is therefore better suited as an advanced ledger interface than as consumer-facing banking UX.

---

# Project Structure

```text
Ledger/
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   ├── auth/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── utils/
│   │   ├── App.jsx
│   │   └── main.jsx
│   │
│   ├── package.json
│   ├── vite.config.js
│   └── .env.example
│
├── src/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── auth.py
│   │   │   ├── account.py
│   │   │   └── transaction.py
│   │   ├── schemas/
│   │   └── dependencies.py
│   │
│   ├── application/
│   │   ├── auth_service.py
│   │   ├── account_service.py
│   │   └── ledger_service.py
│   │
│   ├── domain/
│   │   ├── user.py
│   │   ├── account.py
│   │   ├── entry.py
│   │   └── transaction.py
│   │
│   ├── infrastructure/
│   │   ├── database/
│   │   ├── repositories/
│   │   ├── security/
│   │   └── config.py
│   │
│   ├── tests/
│   └── main.py
│
├── .env
├── .gitignore
└── README.md
```

---

# What I Learned

This project was built to go beyond basic CRUD APIs and understand how backend systems maintain correctness.

Major concepts explored include:

- layered backend architecture
- domain models vs ORM models
- repository pattern
- service-layer business logic
- JWT authentication
- authorization
- password hashing
- database transaction boundaries
- atomicity and rollback
- double-entry accounting
- debit/credit semantics
- derived balances
- relational database design
- PostgreSQL
- REST API design
- API status codes
- frontend/backend integration
- automated testing

---

## License

This project is intended for learning and portfolio use.