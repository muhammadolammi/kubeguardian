docker run -p 8085:8085 \
  -e KUBERNETES_SERVICE_HOST=<api-server-host> \
  -e KUBERNETES_SERVICE_PORT=<api-server-port> \
  --network kubeguardian-net \
  kubeguardian/publisher
