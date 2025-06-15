# ResponSync

ResponSync is a emergency response optimization system that leverages machine learning and routing algorithms to improve emergency response times and resource allocation.

## Project Overview

This project consists of several key components:

- **Backend Service**: A Flask-based API service that handles data processing and model predictions
- **Frontend Application**: A web-based interface for visualizing and interacting with the system
- **OSRM Data Processor**: A service for processing and managing routing data
- **Machine Learning Models**: Predictive models for emergency response optimization

## Prerequisites

- Python 3.8+
- Docker and Docker Compose
- Node.js (for frontend development)

## Installation

1. Clone the repository:

```bash
git clone [https://github.com/AryanAngiras31/ResponSync]
cd ResponSync
```

2. Install Python dependencies:

```bash
pip install -r requirements.txt
```

3. Start the services using Docker Compose:

```bash
docker-compose up -d
```

## Project Structure

```
ResponSync/
├── src/                    # Source code
│   ├── backend/           # Backend API service
│   ├── frontend/          # Frontend application
│   ├── database/          # Database related code
│   └── model/             # Machine learning models
├── data/                  # Data storage
├── osrm-data/            # OSRM routing data
├── osrm-data-processor/  # OSRM data processing service
├── docker-compose.yml    # Docker configuration
└── requirements.txt      # Python dependencies
```

## Running the Application

### Using Docker (Recommended)

The application can be run using Docker Compose:

```bash
docker-compose up -d
```

This will start all services:

- Backend API: http://localhost:5000
- Frontend: http://localhost:3000
- OSRM Data Processor: http://localhost:5002

### Manual Setup

1. Start the backend:

```bash
./run_backend.bat
```

2. Start the frontend (from the frontend directory):

```bash
cd "src\frontend\map"
npm install
npm start
```

## Dependencies

### Backend Dependencies

- Flask 3.1.1
- Flask-Cors 6.0.0
- pandas 2.2.3
- scikit-learn 1.6.1
- joblib 1.5.1
- geopy 2.4.1
- requests 2.32.3

## License

MIT
