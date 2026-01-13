#!/bin/bash

set -a
source .env
set +a


vals eval -f vault-values-secret.yaml | helm upgrade --install vault-foodgram ../helm -n foodgram -f ../helm/values.yaml -f -

# helm secrets upgrade --install vault-foodgram ../helm -n foodgram -f ../helm/values.yaml -f <(vals eval -f vault-values-secret.yaml) 
 