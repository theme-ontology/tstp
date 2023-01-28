cmd /c aws-ecr-push.bat

docker context use totolo
docker compose -f docker-compose.yaml -f docker-compose.prod.yaml up
docker context use default
