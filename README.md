# Ghibli API

This project is a FastAPI-based API that interacts with the Studio Ghibli API and provides user management and authentication functionality. The backend uses PostgreSQL as its database, Redis for caching, Docker for containerization, and supports separate configurations for development and production environments.

## Features

- Role-based access control (RBAC)
- JWT authentication
- Redis caching for API responses
- Full user management (CRUD operations)
- Integration with the Studio Ghibli API
- Automated testing with pytest
- Containerization with Docker and Docker Compose
- Database migrations with Alembic
- Nginx load balancer for production
- Health check endpoint
- Multi-environment configuration (development and production)
- Custom logging system with formatted and colored output (in development)

## Requirements

Before starting, ensure you have the following installed:

- Docker
- Docker Compose
- Python 3.11+
- `make` command (optional for easier management)

## Installation and Configuration

![GIF mostrando la funcionalidad](assets/demo_users.gif)

### Development Environment

1. **Clone the repository**

   ```bash
   git clone git@github.com:pixelead0/ghibli_api.git
   cd ghibli_api
   ```

2. **Configure the environment**

   Copy the `.env.example` file and adjust the necessary configurations:
   
   ```bash
   cp .env.example .env
   ```

3. **Build and start services**

   ```bash
   # Build containers
   make build ENV=dev

   # Start services
   make up ENV=dev

   # Install dependencies
   make requirements

   # Run database migrations
   make upgrade
   ```

4. **Initial Data**

   If `CREATE_INITIAL_DATA=true` is enabled, sample data will be created automatically. 
   If no user exists in the system, the **first user created** will automatically have superuser privileges.


5. **Access PgAdmin** (optional)

   - URL: `http://localhost:8484`
   - Email: `admin@correo.com`
   - Password: `toor`

### Production Environment

1. **Configure environment variables**

   Update the `.env` file:

   ```env
   ENVIRONMENT=production
   CREATE_INITIAL_DATA=false
   
   # Database configuration
   POSTGRES_USER=your_prod_user
   POSTGRES_PASSWORD=your_prod_password
   POSTGRES_DB=your_prod_db
   
   # Redis configuration
   REDIS_HOST=ghibli_redis_prd
   REDIS_PORT=6379
   REDIS_TTL=3600
   ```

2. **Deploy to production**

   ```bash
   make build ENV=prd
   make up ENV=prd
   ```

## Project Structure

```
.
├── app/
│   ├── api/            # API endpoints and routes
│   │   └── v1/         # Version 1 implementations
│   ├── core/           # Core configurations and functionality
│   ├── crud/           # CRUD operations
│   ├── models/         # SQLModel and Pydantic models
│   └── services/       # Business logic and external services
├── containers/
│   ├── api/            # API Dockerfiles
│   ├── nginx/          # Load balancer configuration
│   └── pgadmin/        # PgAdmin configuration
├── tests/              # Automated tests
├── docker-compose.dev.yml  # Development configuration
├── docker-compose.prd.yml  # Production configuration
├── Makefile            # Development and deployment commands
└── README.md           # Project documentation
```

## Available Commands

### Development Commands

```bash
make build ENV=dev        # Build development containers
make up ENV=dev           # Start development services
make down ENV=dev         # Stop development services
make test                 # Run tests
make test-cov             # Run tests with coverage report
make lint                 # Run pre-commit hooks
```

### Production Commands

```bash
make build ENV=prd        # Build production containers
make up ENV=prd           # Start production services
make down ENV=prd         # Stop production services
make clean ENV=prd        # Remove production containers and images
make clean-all            # Clean both development and production environments
```

### Database Commands

```bash
make upgrade              # Run database migrations
make downgrade            # Roll back database migrations
make revision msg="message" # Create a new migration
```

## API Documentation

When running, the API documentation is available at:

- Development: `http://localhost:8881/docs`
- Production: `http://localhost/docs`

### Main Endpoints

#### Authentication
```
POST /api/v1/login       # Obtain JWT token
```

#### Users
```
POST   /api/v1/users     # Create user
GET    /api/v1/users     # List users (admin only)
GET    /api/v1/users/me  # Get current user
GET    /api/v1/users/{id} # Get user by ID
PUT    /api/v1/users/{id} # Update user
DELETE /api/v1/users/{id} # Delete user
```

#### Ghibli Data
```
GET /api/v1/ghibli       # Get data based on user role
```

#### Health Check
```
GET /health              # Verify API status
```

## User Roles

- **admin**: Full access to all endpoints and data
- **films**: Access to movie information
- **people**: Access to character information
- **locations**: Access to location information
- **species**: Access to species information
- **vehicles**: Access to vehicle information

## Contributing

1. Fork the repository
2. Create your feature branch
3. Ensure tests pass
4. Commit your changes
5. Push to your branch
6. Submit a Pull Request

## License

This project is licensed under the **GNU General Public License v3.0**
