FROM metabase/metabase:latest

EXPOSE 3000

ENV MB_DB_TYPE=postgres
ENV MB_DB_DBNAME=metabase
ENV MB_DB_HOST=postgres
ENV MB_DB_PORT=5432
ENV MB_DB_USER=postgres
ENV MB_DB_PASS=postgres

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD curl -f http://localhost:3000/api/health || exit 1
