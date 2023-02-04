docker context use default
docker compose -f docker-compose.tr.yaml -f docker-compose.tr.prod.yaml build

aws ecr-public get-login-password --region us-east-1 | docker login --username AWS --password-stdin public.ecr.aws/m8o2v6v7

docker tag totolo-tan-ru:latest public.ecr.aws/m8o2v6v7/totolo-tanru:latest

docker push public.ecr.aws/m8o2v6v7/totolo-tanru:latest
