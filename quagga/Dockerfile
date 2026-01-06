# Baza: gotowy obraz pierky/quagga
FROM pierky/quagga

# Instalujemy tylko edytor (opcjonalnie) i bash (już jest)
# Głównie dodajemy prosty entrypoint script

# Kopiujemy entrypoint script do kontenera
#COPY entrypoint.sh /usr/local/bin/entrypoint.sh
#RUN chmod +x /usr/local/bin/entrypoint.sh

# Volume na konfigurację (jak w oryginale + nasze dodatki)
#VOLUME /etc/quagga

# Nowy entrypoint – uruchomi daemony i dołączy extra config jeśli istnieje
#ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

# Domyślna komenda: uruchamia zebra i ospfd w tle (jak w wielu obrazach quagga)
#CMD ["zebra", "-d", "ospfd", "-d"]