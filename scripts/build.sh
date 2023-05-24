#!/bin/bash
set -e

KIND=$1
TAG=$2

if [ -z "$KIND" ]; then
  echo "KIND is empty"
  exit 1
fi

if [ -z "$TAG" ]; then
  echo "TAG is empty"
  exit 1
fi

echo "Building $KIND image with tag $TAG"

if [ "$KIND" == "deployment" ]; then
  docker buildx build --platform=linux/amd64 . -t afiffahreza/autolog-deployment:$TAG
  docker push afiffahreza/autolog-deployment:$TAG
fi

if [ "$KIND" == "training" ]; then
  docker buildx build --platform=linux/amd64 . -t afiffahreza/autolog-training:$TAG
  docker push afiffahreza/autolog-training:$TAG
fi