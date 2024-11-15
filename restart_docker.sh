#!/bin/bash

docker build -t hiro-ai .
docker stop hiro-ai-container    # 기존 컨테이너 중지
docker rm hiro-ai-container      # 기존 컨테이너 삭제
docker run -d -p 8000:8000 --name hiro-ai-container hiro-ai
echo "Container restarted"