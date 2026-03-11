#!/bin/sh
set -e

# Asegurar configuración permisiva
mkdir -p /etc/cups
cat > /etc/cups/cupsd.conf <<EOF
LogLevel warn
PageLogFormat
Port 631
Listen /run/cups/cups.sock
Browsing On
BrowseLocalProtocols dnssd
DefaultAuthType Basic
WebInterface Yes
DefaultEncryption Never
ServerAlias *

<Location />
  Order allow,deny
  Allow all
</Location>

<Location /admin>
  Order allow,deny
  Allow all
</Location>

<Location /admin/conf>
  AuthType Default
  Require user @SYSTEM
  Order allow,deny
  Allow all
</Location>
EOF

# Configurar cups-pdf para guardar en /output y ser permisivo con los nombres
if [ -f /etc/cups/cups-pdf.conf ]; then
  sed -i 's|^#*Out .*|Out /output|' /etc/cups/cups-pdf.conf
  sed -i 's|^#*AnonDirName .*|AnonDirName /output|' /etc/cups/cups-pdf.conf
  sed -i 's|^#*Label .*|Label 2|' /etc/cups/cups-pdf.conf # Usa el título del trabajo como nombre de archivo
  echo "GrubPrivacy 0" >> /etc/cups/cups-pdf.conf
fi

# Asegurar permisos de la carpeta de salida para el usuario lp (CUPS)
mkdir -p /output
chmod 1777 /output
chown root:lpadmin /output

# Arrancar CUPS en segundo plano para configurar
/usr/sbin/cupsd

# Esperar a que el scheduler esté listo
i=0
while ! lpstat -r >/dev/null 2>&1; do
  i=$((i + 1))
  [ $i -ge 20 ] && break
  sleep 1
done

# 1. Agregar impresora PDF
echo "Registrando impresora PDF..."
lpadmin -p PDF -v cups-pdf:/ -E -m lsbd:cups-pdf/CUPS-PDF.ppd || \
lpadmin -p PDF -v cups-pdf:/ -E -m drv:///cups-pdf/cups-pdf.ppd || \
lpadmin -p PDF -v cups-pdf:/ -E || true

# 2. Agregar impresora Zebra (Raw)
echo "Registrando impresora Zebra..."
lpadmin -p Zebra -E -v file:/dev/null -m raw || true

# Compartir impresoras en la red
cupsctl --remote-admin --remote-any --share-printers || true

# Matar instancia de fondo
kill $(cat /var/run/cups/cupsd.pid)
sleep 2

# Mantener CUPS en primer plano definitivamente
echo "Servidor CUPS listo."
exec /usr/sbin/cupsd -f