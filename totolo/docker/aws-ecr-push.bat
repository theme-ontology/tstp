
docker compose -f docker-compose.yaml build

aws ecr-public get-login-password --region us-east-1 | docker login --username AWS --password-stdin public.ecr.aws/m8o2v6v7

docker tag totolo-m4:latest public.ecr.aws/m8o2v6v7/totolo-m4:latest
docker tag totolo-es:latest public.ecr.aws/m8o2v6v7/totolo-sphinx:latest
docker push public.ecr.aws/m8o2v6v7/totolo-m4:latest
docker push public.ecr.aws/m8o2v6v7/totolo-sphinx:latest
