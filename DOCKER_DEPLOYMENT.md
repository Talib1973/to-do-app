# Docker Deployment Guide

This guide covers building and running the Todo App with Docker.

## Prerequisites

- Docker installed and running
- Docker Compose (optional, for easier orchestration)
- OpenRouter API key (for AI chatbot feature)

## Quick Start with Docker Compose

### 1. Create docker-compose.yml

Create a `docker-compose.yml` file in the project root (PHASE_2 directory):

```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:////app/data/todo_app.db
      - BETTER_AUTH_SECRET=test-secret-key-with-at-least-32-characters-for-jwt-signing
      - AI_PROVIDER=openrouter
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
      - AI_MODEL=anthropic/claude-3.5-haiku
    volumes:
      - backend-data:/app/data
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:8000/health')"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 5s

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
    depends_on:
      backend:
        condition: service_healthy

volumes:
  backend-data:
```

### 2. Create .env file

Create a `.env` file in the project root with your OpenRouter API key:

```env
OPENROUTER_API_KEY=your-openrouter-api-key-here
```

### 3. Build and Run

```bash
# Build and start all services
docker-compose up --build

# Or run in detached mode (background)
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v
```

### 4. Access the Application

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Manual Docker Commands (Without Docker Compose)

### Build Images

```bash
# Build backend image
cd backend
docker build -t todo-backend:latest .
cd ..

# Build frontend image
cd frontend
docker build -t todo-frontend:latest .
cd ..
```

### Run Containers

```bash
# Create a shared network
docker network create todo-network

# Run backend container
docker run -d \
  --name todo-backend \
  --network todo-network \
  -p 8000:8000 \
  -e DATABASE_URL=sqlite:////app/data/todo_app.db \
  -e BETTER_AUTH_SECRET=test-secret-key-with-at-least-32-characters-for-jwt-signing \
  -e AI_PROVIDER=openrouter \
  -e OPENROUTER_API_KEY=your-openrouter-api-key \
  -e AI_MODEL=anthropic/claude-3.5-haiku \
  -v todo-data:/app/data \
  todo-backend:latest

# Wait for backend to be healthy (check logs)
docker logs -f todo-backend

# Run frontend container (in a new terminal)
docker run -d \
  --name todo-frontend \
  --network todo-network \
  -p 3000:3000 \
  -e NEXT_PUBLIC_API_URL=http://localhost:8000 \
  todo-frontend:latest

# View logs
docker logs -f todo-frontend
```

### Container Management

```bash
# Stop containers
docker stop todo-backend todo-frontend

# Start containers
docker start todo-backend todo-frontend

# Remove containers
docker rm todo-backend todo-frontend

# Remove network
docker network rm todo-network

# Remove volume (deletes database)
docker volume rm todo-data
```

## Environment Variables

### Backend

- `DATABASE_URL`: SQLite database path (default: `sqlite:////app/data/todo_app.db`)
- `BETTER_AUTH_SECRET`: JWT signing secret (min 32 characters)
- `AI_PROVIDER`: AI provider name (default: `openrouter`)
- `OPENROUTER_API_KEY`: Your OpenRouter API key (required for chatbot)
- `AI_MODEL`: AI model to use (default: `anthropic/claude-3.5-haiku`)

### Frontend

- `NEXT_PUBLIC_API_URL`: Backend API URL (default: `http://localhost:8000`)

## Troubleshooting

### Backend won't start

Check logs:
```bash
docker logs todo-backend
```

Common issues:
- Missing OpenRouter API key
- Port 8000 already in use (stop other services)
- Database initialization errors

### Frontend can't connect to backend

1. Ensure backend is running and healthy:
   ```bash
   curl http://localhost:8000/health
   ```

2. Check network connectivity:
   ```bash
   docker network inspect todo-network
   ```

3. Verify environment variables:
   ```bash
   docker exec todo-frontend env | grep NEXT_PUBLIC_API_URL
   ```

### Database issues

Reset the database:
```bash
# With Docker Compose
docker-compose down -v
docker-compose up --build

# Without Docker Compose
docker volume rm todo-data
docker restart todo-backend
```

### Frontend build failures

Check Node.js version and dependencies:
```bash
docker build --no-cache -t todo-frontend:latest ./frontend
```

## Production Deployment

For production deployment, consider:

1. **Environment Variables**: Use proper secrets management
2. **Database**: Switch to PostgreSQL or MySQL
3. **Reverse Proxy**: Use nginx or Traefik
4. **SSL/TLS**: Configure HTTPS certificates
5. **Monitoring**: Add logging and monitoring solutions
6. **Scaling**: Consider container orchestration (Kubernetes, Docker Swarm)

### Example Production docker-compose.yml

```yaml
version: '3.8'

services:
  backend:
    image: todo-backend:latest
    restart: unless-stopped
    environment:
      - DATABASE_URL=postgresql://user:password@postgres:5432/tododb
      - BETTER_AUTH_SECRET=${BETTER_AUTH_SECRET}
      - AI_PROVIDER=openrouter
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
      - AI_MODEL=anthropic/claude-3.5-haiku
    depends_on:
      - postgres

  frontend:
    image: todo-frontend:latest
    restart: unless-stopped
    environment:
      - NEXT_PUBLIC_API_URL=https://api.yourdomain.com
    depends_on:
      - backend

  postgres:
    image: postgres:15-alpine
    restart: unless-stopped
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=tododb
    volumes:
      - postgres-data:/var/lib/postgresql/data

  nginx:
    image: nginx:alpine
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - frontend
      - backend

volumes:
  postgres-data:
```

## Next Steps

1. Start the application with Docker Compose
2. Create a user account at http://localhost:3000
3. Test the AI chatbot feature
4. Configure additional settings as needed
