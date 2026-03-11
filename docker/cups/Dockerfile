# CUPS con impresora virtual PDF (cups-pdf). Salida en /output (montar .data/cups-pdf).
FROM debian:bookworm-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        cups \
        printer-driver-cups-pdf \
        procps \
        ghostscript \
    && rm -rf /var/lib/apt/lists/*

# Crear usuario administrador para la UI de CUPS (User: admin / Pass: admin)
# Esto es vital para que te deje entrar a la administración web
RUN useradd -m -G lpadmin admin && echo "admin:admin" | chpasswd

# Configuración básica para permitir acceso remoto a la UI y red de Docker
RUN sed -i 's/Listen localhost:631/Listen 0.0.0.0:631/' /etc/cups/cupsd.conf && \
    sed -i 's/Browsing Off/Browsing On/' /etc/cups/cupsd.conf && \
    echo "DefaultEncryption Never" >> /etc/cups/cupsd.conf

# Salida de cups-pdf a /output
RUN mkdir -p /output && chmod 1777 /output
RUN sed -i 's|^#*Out .*|Out /output|' /etc/cups/cups-pdf.conf || echo 'Out /output' >> /etc/cups/cups-pdf.conf

COPY docker/cups/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 631
ENTRYPOINT ["/entrypoint.sh"]