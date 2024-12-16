# Ghibli API

This project is a FastAPI-based API that interacts with the Studio Ghibli API and provides user management and authentication functionality. The backend uses Postgres as its database and Docker for containerization.

## Requirements

Before you start, make sure you have the following installed:

- Docker
- Docker Compose
- Python 3.11+
- `make` command (optional for easy management)

## Setup

### Development Environment

To set up the project in a development environment, follow these steps:

1. **Clone the repository**

    ```bash
    git clone git@github.com:pixelead0/ghibli_api.git
    cd ghibli-api
    ```

2. **Build the Docker containers**

    Use the `Makefile` to build the application:

    ```bash
    make build
    ```

3. **Start the containers**

    Start the application containers using Docker Compose:

    ```bash
    make up
    ```

4. **Install dependencies**

    Install Python dependencies within the container:

    ```bash
    make requirements
    ```

5. **Run the database migrations**

    Apply the migrations to the database:

    ```bash
    make upgrade
    ```

6. **Create initial data (optional)**

    For development purposes, you can create initial data by setting the `CREATE_INITIAL_DATA` flag to `true` in the `.env` file and running the app:

    ```bash
    make up
    ```

7. **Start the development server**

    You can now access the API at `http://localhost:8881` and use the following endpoint for health check:

    ```bash
    curl http://localhost:8881/health
    ```

### Production Environment

To set up the project for production, follow these steps:

1. **Set the environment to production**

    Update the `.env` file and set the `ENVIRONMENT` variable to `production`:

    ```bash
    ENVIRONMENT=production
    ```

2. **Configure your database credentials**

    Update the `.env` file with your production database credentials:

    ```bash
    POSTGRES_USER=your_prod_user
    POSTGRES_PASSWORD=your_prod_password
    POSTGRES_DB=your_prod_db
    ```

3. **Build the Docker containers for production**

    Build the application containers in production mode:

    ```bash
    make build
    ```

4. **Start the containers**

    Run the application in production mode:

    ```bash
    make up
    ```

### Running Tests

To run the tests, use the following command:

```bash
make test
```

You can also run tests for a specific path:

```bash
make test path=your_test_path
```

### Stopping the Application

To stop the application, run:

```bash
make down
```

### Cleaning the Environment

To stop the application and remove all containers and volumes:

```bash
make clean
```

## Logging

Logs are handled by the logging configuration in `app/core/logging.py`. The logs are printed to the console and can be configured for file output.

### Log Levels

- **DEBUG**: Detailed information, typically useful only when diagnosing problems.
- **INFO**: Confirmations that things are working as expected.
- **WARNING**: Indications that something unexpected happened, but the application is still working as expected.
- **ERROR**: The application is not working as expected.
- **CRITICAL**: A very serious error, potentially causing the application to crash.

## File Structure

```
.
├── app/                          # Backend application code
├── containers/                   # Docker configurations
│   ├── api/                      # API container configurations
│   ├── pgadmin/                  # pgAdmin container configurations
├── tests/                        # Unit tests
├── .env                          # Environment variables for development
├── .env.example                  # Example environment configuration
├── docker-compose.yml            # Docker Compose configuration
├── Makefile                      # Task automation for Docker and other processes
└── requirements.txt              # Python dependencies
```

## Contributing

Feel free to fork the repository, create branches, and submit pull requests. Please ensure that any changes are well tested.

---

For more information, refer to the project's official documentation or contact the maintainers.
