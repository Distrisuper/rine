# CUPS con impresora virtual PDF (cups-pdf). Salida en /output (montar .data/cups-pdf).
FROM debian:bookworm-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        cups \
        printer-driver-cups-pdf \
        procps \
    && rm -rf /var/lib/apt/lists/*

# Escuchar en todas las interfaces para que app/workers en Docker se conecten
RUN sed -i 's/Listen localhost:631/Listen 0.0.0.0:631/' /etc/cups/cupsd.conf || true

# Salida de cups-pdf a /output (montar volumen ahí)
RUN mkdir -p /output && chmod 1777 /output
RUN sed -i 's|^#*Out .*|Out /output|' /etc/cups/cups-pdf.conf || echo 'Out /output' >> /etc/cups/cups-pdf.conf

COPY docker/cups/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 631
ENTRYPOINT ["/entrypoint.sh"]