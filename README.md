[![CI/CD](https://github.com/yousef-rezaei/ai-sql-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/yousef-rezaei/ai-sql-agent/actions/workflows/ci.yml)

# AI SQL Agent

An AI-powered SQL Agent that allows users to query relational business data using natural language.

Built with **Azure OpenAI, FastAPI, PostgreSQL, React/TypeScript, Docker, Azure Container Apps, Azure Container Registry, and GitHub Actions**.

## Features

* Natural-language to SQL generation
* Schema-aware SQL generation
* Azure OpenAI tool calling
* Automated SQL execution
* SQLGlot query validation
* PostgreSQL read-only execution user
* Automatic SQL error recovery
* AI-generated result summaries
* Dynamic React result tables
* Dockerized frontend and backend
* Azure Database for PostgreSQL deployment
* Azure Container Registry
* Azure Container Apps
* GitHub Actions CI/CD
* OIDC-based passwordless Azure deployment

## Architecture

```mermaid
flowchart TD
    U[User] --> F[React Frontend]

    F --> N[Nginx]

    N --> B[FastAPI Backend]

    B --> OAI[Azure OpenAI]
    B --> V[SQLGlot Validator]

    V --> DB[(Azure PostgreSQL)]

    DB --> B
    B --> N
    N --> F

    GH[GitHub Actions] --> ACR[Azure Container Registry]
    ACR --> FE[Frontend Container App]
    ACR --> BE[Backend Container App]

    FE --> F
    BE --> B
```

## Tech Stack

### Backend

* Python
* FastAPI
* SQLAlchemy
* SQLGlot
* Azure OpenAI

### Frontend

* React
* TypeScript
* Nginx

### Database

* PostgreSQL
* Azure Database for PostgreSQL Flexible Server

### DevOps & Cloud

* Docker
* Docker Compose
* Azure Container Registry
* Azure Container Apps
* GitHub Actions
* GitHub OIDC
* Azure CLI

## Security

The SQL Agent includes multiple safeguards before executing AI-generated SQL:

* Read-only PostgreSQL database user
* SQL parsing and validation using SQLGlot
* Restricted SQL operations
* Schema-aware SQL generation
* Database permission controls
* Environment-based secret management
* Passwordless GitHub-to-Azure authentication using OIDC

## CI/CD

GitHub Actions automatically validates and builds the application.

The deployment pipeline follows:

```text
GitHub
   |
   v
GitHub Actions
   |
   | OIDC Authentication
   v
Azure
   |
   v
Azure Container Registry
   |
   +-------------------+
   |                   |
   v                   v
Frontend Image     Backend Image
   |                   |
   v                   v
Azure Container Apps
```

## Screenshots

### AI SQL Agent

![AI SQL Agent](docs/screenshots/app.png)

### Query Result

![Query Result](docs/screenshots/query-result.png)

### CI/CD

![GitHub Actions](docs/screenshots/github-actions.png)

## Project Structure

```text
ai-sql-agent/
├── backend/
│   ├── Dockerfile
│   ├── app/
│   └── .dockerignore
│
├── frontend/
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── src/
│   └── .dockerignore
│
├── docs/
│   └── screenshots/
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── docker-compose.yml
└── README.md
```

## Running Locally

Clone the repository:

```bash
git clone https://github.com/yousef-rezaei/ai-sql-agent.git
cd ai-sql-agent
```

Start the application using Docker Compose:

```bash
docker compose up --build
```

The application consists of:

* React frontend
* FastAPI backend
* PostgreSQL database

## Environment Variables

The backend requires environment variables for database connectivity and Azure OpenAI configuration.

Example:

```env
DATABASE_URL=postgresql://user:password@host:5432/database

AZURE_OPENAI_ENDPOINT=...
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_DEPLOYMENT=...
AZURE_OPENAI_API_VERSION=...
```

Do not commit real credentials or secrets to the repository.

## Author

**Yousef Rezaei**
