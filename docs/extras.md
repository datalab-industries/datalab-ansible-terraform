# Additional containers

You can run additional services alongside *datalab* on the same server.

1. Add each service as a directory in `./src/extras` (ideally a git submodule) with its own `Dockerfile`, e.g., `./src/extras/service_A/Dockerfile`.
2. Create `./src/extras/docker-compose.yml` to configure all extras, e.g.:
   ```yaml
   name: extras
   services:
     service_A:
       build:
         context: service_A
       restart: unless-stopped
       ports:
         - "5002:5001"

   networks:
     backend:
       driver: bridge
   ```
   For now, services should expose a port rather than use Docker networking directly.
   This may change in future.
3. List the service in the `extras` section of `ansible/inventory.yml`, so that NGINX generates the reverse proxy rules:
   ```yaml
   extras:
     service_A:
       url: service_A.example.com
       port: 5002
   ```
4. Run the playbook with the `extras` and `nginx` tags, or the full playbook:
   ```shell
   make extras
   make nginx
   ```

The inventory example above generates this (abridged) NGINX config:

```nginx
server {
  listen 443 ssl;
  server_name service_A.example.com;

  location / {
    proxy_pass http://localhost:5002;
  }
}
```

Remember to point DNS for each extra URL at the server.
