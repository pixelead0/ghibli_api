# Ghibli API

This project is a FastAPI-based API that interacts with the Studio Ghibli API and provides user management and authentication functionality. The backend uses Postgres as its database, Redis for caching, and Docker for containerization.

## Features

- Role-based access control (RBAC)
- JWT Authentication
- Redis caching for API responses
- Full user management (CRUD operations)
- Integration with Studio Ghibli API
- Automated testing with pytest
- Docker containerization
- Database migrations with Alembic

## Requirements

Before you start, make sure you have the following installed:

- Docker
- Docker Compose
- Python 3.11+
- `make` command (optional for easy management)

## Setup

### Development Environment

1. **Clone the repository**

    ```bash
    git clone git@github.com:pixelead0/ghibli_api.git
    cd ghibli-api
    ```

2. **Environment Configuration**

    Copy the example environment file and adjust as needed:
    ```bash
    cp .env.example .env
    ```

3. **Build and Start**

    Use the provided Makefile commands:
    ```bash
    # Build containers
    make build

    # Start services
    make up

    # Install dependencies
    make requirements

    # Run migrations
    make upgrade
    ```

4. **Initial Data (Optional)**

    For development, you can create initial data by setting in `.env`:
    ```
    CREATE_INITIAL_DATA=true
    ```

### Testing Environment

Run all tests:
```bash
make test
```

Run specific tests:
```bash
make test path=tests/api/test_auth.py
```

### Production Environment

1. **Configure Production Settings**

    Update `.env`:
    ```bash
    ENVIRONMENT=production
    
    # Database settings
    POSTGRES_USER=your_prod_user
    POSTGRES_PASSWORD=your_prod_password
    POSTGRES_DB=your_prod_db
    
    # Redis settings
    REDIS_HOST=your_redis_host
    REDIS_PORT=6379
    REDIS_TTL=3600  # Cache duration in seconds
    ```

2. **Deploy**
    ```bash
    make build
    make up
    ```

## API Documentation

When running, the API documentation is available at:
- Swagger UI: `http://localhost:8881/docs`
- ReDoc: `http://localhost:8881/redoc`


## Development Tools

### PgAdmin
Access the database management interface at `http://localhost:8484`:
- Default email: admin@correo.com
- Default password: toor

### Pre-commit Hooks
The project uses pre-commit hooks for code quality. Install with:
```bash
pip install pre-commit
pre-commit install
```

## Project Structure

```
.
├── app/
│   ├── api/            # API endpoints and routes
│   │   └── v1/         # API version 1 implementations
│   ├── core/           # Core functionality (config, security, etc.)
│   ├── crud/           # Database CRUD operations
│   ├── models/         # SQLModel/Pydantic models
│   └── services/       # Business logic and external services
├── containers/         # Docker configurations
│   ├── api/           # API container setup
│   └── pgadmin/       # PgAdmin container setup
├── tests/             # Test suites
│   ├── api/           # API endpoint tests
│   └── services/      # Service layer tests
├── .env               # Environment variables
├── docker-compose.yml # Docker services configuration
└── Makefile          # Development and deployment commands
```

## Makefile Commands

- `make build`: Build all containers
- `make up`: Start all services
- `make down`: Stop all services
- `make clean`: Remove all containers and volumes
- `make logs`: View all container logs
- `make logs_api`: View API container logs
- `make test`: Run test suite
- `make upgrade`: Run database migrations
- `make downgrade`: Rollback database migrations
- `make revision msg="message"`: Create new migration
- `make requirements`: Install Python dependencies
- `make lint`: Run pre-commit hooks

## Cache Configuration

The Redis cache is configured with the following default settings in `.env`:
```
REDIS_HOST=ghibli_redis
REDIS_PORT=6379
REDIS_TTL=3600  # 1 hour cache duration
```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Run tests and ensure they pass
4. Commit your changes
5. Push to your branch
6. Create a Pull Request

For more information, refer to the project's official documentation or contact the maintainers.

## License

This project is licensed under the GNU General Public License v3.0