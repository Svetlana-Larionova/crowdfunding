#!/bin/bash

echo "=== Building and starting Crowdfunding App ==="

# Build and start containers
docker-compose up --build -d

echo "=== Containers are starting... ==="
echo "=== Web server will be available at http://localhost:8000 ==="
echo "=== To view logs: docker-compose logs -f ==="