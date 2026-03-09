#!/bin/sh
set -e

# Arrancar CUPS en segundo plano
/usr/sbin/cupsd

# Esperar a que CUPS acepte conexiones
i=0
while ! lpstat -r 2>/dev/null; do
  i=$((i + 1))
  [ $i -ge 30 ] && exit 1
  sleep 1
done

# Agregar impresora PDF (cups-pdf escribe en /output)
if [ -f /usr/share/ppd/cups-pdf/CUPS-PDF.ppd ]; then
  lpadmin -p PDF -E -v cups-pdf:/ -P /usr/share/ppd/cups-pdf/CUPS-PDF.ppd 2>/dev/null || true
else
  lpadmin -p PDF -E -v cups-pdf:/ -m drv:///cups-pdf/cups-pdf.ppd 2>/dev/null || true
fi

# Mantener CUPS en primer plano
exec /usr/sbin/cupsd -f
