# Flow for Run


## Development Setup

1. Make sure you have Docker and Docker Compose installed
2. Clone this repository:
   ```bash
   git clone <repository-url>
    cd Fast-API
   cd backend
   ```
3. Create a `.env` file based on the example (ask a team member for the values)
4. Run the application:
   ```bash
   docker-compose up --build
   ```
5. The API will be available at `http://localhost:8000`

## Project Structure

- `app/` - Main application code
- `static/` - Static files (mounted in Docker)
- `Dockerfile` - Docker configuration
- `docker-compose.yml` - Service definitions
- `requirements.txt` - Python dependencies
