FROM nginx:1.25-alpine

RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d

RUN mkdir -p /vol/static && \
    mkdir -p /vol/media && \
    chmod -R 755 /vol

# Run as non-root user
RUN adduser -D -u 1000 nginxuser && \
    chown -R nginxuser:nginxuser /vol /var/cache/nginx /var/run /var/log/nginx
USER nginxuser