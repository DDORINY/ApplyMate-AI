Write-Host "Reset uses a separate Compose project. Existing volumes are not deleted by this script."
docker compose -f docker-compose.yml -f docker-compose.e2e.yml -p applymate_e2e --env-file .env.e2e.example down
docker compose -f docker-compose.yml -f docker-compose.e2e.yml -p applymate_e2e --env-file .env.e2e.example up --build -d
