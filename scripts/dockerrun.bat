docker rm toad
docker run --publish 31985:31985 --name toad toad:1.0 %*
