# Army AFT Assistant

AI-powered Army Fitness Test (AFT) application for managing Soldier
profiles, calculating AFT scores, tracking results, and answering
AFT-related questions using Retrieval-Augmented Generation (RAG).

## Features

- Soldier profile management
- AFT score calculation using official scoring standards
- AFT test history stored in PostgreSQL
- AI-powered AFT assistant
- RAG using LangChain and FAISS
- Amazon Bedrock / Amazon Nova integration
- Mem0 long-term memory
- React frontend
- Flask REST API
- PostgreSQL database
- Dockerized local development environment
- AWS production deployment
- Infrastructure as Code with Terraform
- Automated CI/CD with GitHub Actions

## Technology Stack

### Frontend
- React
- Vite
- JavaScript
- Nginx (local Docker deployment)

### Backend
- Python
- Flask
- SQLAlchemy
- Pytest
- LangChain

### AI
- Amazon Bedrock
- Amazon Nova
- Amazon Titan Embeddings
- FAISS
- Retrieval-Augmented Generation (RAG)
- Mem0

### Database
- PostgreSQL
- Amazon RDS

### DevOps / Cloud
- Docker
- Docker Compose
- GitHub Actions
- Terraform
- Amazon ECS / Fargate
- Amazon ECR
- Application Load Balancer
- Amazon S3
- Amazon CloudFront
- AWS Secrets Manager
- Amazon CloudWatch

## Architecture

### Local Development

Browser
  |
  v
React / Nginx
  |
  | /api/*
  v
Flask API
  |
  v
PostgreSQL

The complete local environment is orchestrated using Docker Compose.

### AWS Production

User
 |
 v
CloudFront
 |
 +-------------------+
 |                   |
 v                   v
S3                 /api/*
React                 |
                      v
                     ALB
                      |
                      v
                 ECS / Fargate
                 Flask Backend
                  /       \
                 v         v
               RDS      Bedrock
            PostgreSQL     |
                           v
                     FAISS / RAG

AWS Secrets Manager securely provides application credentials.

## CI/CD Pipeline

Push to main
    |
    v
GitHub Actions CI
    |
    +-- Install dependencies
    +-- Run Pytest
    +-- Build React
    +-- Validate Docker configuration
    |
    v
CI Success
    |
    v
GitHub Actions CD
    |
    +-- Build backend Docker image
    +-- Push image to Amazon ECR
    +-- Deploy to ECS/Fargate
    +-- Build React frontend
    +-- Upload frontend to S3
    +-- Invalidate CloudFront cache
    |
    v
Production

Deployment occurs only after the CI workflow completes successfully.

## Local Setup

### Prerequisites

- Python 3.12+
- Node.js
- Docker
- Docker Compose
- AWS CLI

### Clone Repository

git clone <repository-url>
cd army-aft-assistant

### Start with Docker

docker compose up --build

The local application is available at:

http://localhost:8080

## Testing

Run backend tests:

cd backend
pytest -v

## Terraform

AWS infrastructure is managed using Terraform.

cd terraform

terraform init
terraform fmt
terraform validate
terraform plan

Review the Terraform plan before applying:

terraform apply

Terraform provisions resources including:

- VPC
- Public/private subnets
- Security groups
- Amazon RDS PostgreSQL
- Amazon ECR
- Amazon ECS/Fargate
- Application Load Balancer
- Amazon S3
- Amazon CloudFront
- AWS Secrets Manager
- CloudWatch
- IAM roles and policies

## Security

Sensitive credentials are not stored in source control.

AWS Secrets Manager stores runtime secrets including:

- PostgreSQL credentials
- Mem0 API key

ECS retrieves these secrets at runtime using IAM permissions.

GitHub Actions uses GitHub repository secrets for deployment credentials.

## CI/CD

Two GitHub Actions workflows are used:

### Continuous Integration

Triggered by pushes and pull requests to `main`.

The CI workflow:

1. Installs backend dependencies
2. Runs Pytest
3. Installs frontend dependencies
4. Builds the React application
5. Validates Docker Compose

### Continuous Deployment

Deployment runs only after CI completes successfully.

The CD workflow:

1. Authenticates with AWS
2. Builds the Flask Docker image
3. Pushes the image to Amazon ECR
4. Deploys the backend to ECS/Fargate
5. Builds the React frontend
6. Uploads the build to Amazon S3
7. Invalidates Amazon CloudFront

## Project Structure

army-aft-assistant/
├── backend/
│   ├── src/
│   ├── tests/
│   ├── scripts/
│   ├── data/
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   ├── Dockerfile
│   └── nginx.conf
│
├── terraform/
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   └── providers.tf
│
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── deploy.yml
│
├── docker-compose.yml
└── README.md

## Production Application

The production application is distributed through Amazon CloudFront.

## Author

Ying Deng