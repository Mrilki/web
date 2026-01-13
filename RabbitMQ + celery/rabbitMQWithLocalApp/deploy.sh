#!/bin/bash

set -a
source .env
set +a


vals eval -f values.yaml | helm upgrade --install rabbitmq-foodgram oci://registry-1.docker.io/cloudpirates/rabbitmq -n foodgram -f values.yaml -f -

