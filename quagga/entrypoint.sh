#!/bin/bash

# Ścieżka do dodatkowego pliku OSPF (montowanego z hosta)
EXTRA_OSPF_CONF="/etc/quagga/ospf-extra.conf"

# Jeśli plik istnieje – dołącz jego zawartość na koniec ospfd.conf
if [ -f "$EXTRA_OSPF_CONF" ]; then
    echo "Dołączam zawartość $EXTRA_OSPF_CONF do /etc/quagga/ospfd.conf"
    cat "$EXTRA_OSPF_CONF" >> /etc/quagga/ospfd.conf
fi

# Uruchamiamy oryginalną komendę (daemony Quagga)
exec "$@"