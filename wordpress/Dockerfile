# Tamil.de – WordPress als ein Container für Coolify (Build-Pack „Dockerfile“, Port 80).
# Apache + PHP 8.3 + SQLite (kein MySQL). Build-Kontext = Repo-Wurzel:
#   docker build -f wordpress/Dockerfile -t tamil-web .
# Welche Dateien in den Kontext kommen, steht in wordpress/Dockerfile.dockerignore (BuildKit liest sie statt der
# .dockerignore an der Wurzel).
#
# Persistent Storage in Coolify – nur diese zwei Pfade, alles andere kommt bei jedem Start frisch aus dem Image:
#   /var/www/html/wp-content/database   (SQLite-Datenbank, Salts, Merker)
#   /var/www/html/wp-content/uploads    (Medien)
# Variablen (Erklärung in docker/start.sh): WP_URL_PUBLIC, WP_ADMIN_PASSWORD (Pflicht bei der Erstinstallation),
# WP_ADMIN_USER, WP_ADMIN_EMAIL, WP_TITLE, RADAR_APP_PASSWORD, MIGRATION_APP_PASSWORD, RADAR_COCKPIT_URL.
FROM wordpress:6-php8.3-apache

ARG WP_CLI_VERSION=2.12.0
ARG WP_CLI_SHA512=be928f6b8ca1e8dfb9d2f4b75a13aa4aee0896f8a9a0a1c45cd5d2c98605e6172e6d014dda2e27f88c98befc16c040cbb2bd1bfa121510ea5cdf5f6a30fe8832
ARG SQLITE_VERSION=3.1.3
ARG SQLITE_SHA256=f6ce35e8419d0b9326221a907627d905e25c2a5ba2afc86492811f14c851efe0

ENV TZ=Europe/Berlin

# curl für den Healthcheck von Coolify, rsync für den Code-Abgleich bei jedem Start
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl less unzip rsync \
    && rm -rf /var/lib/apt/lists/*

# wp-cli (feste Version, Prüfsumme)
RUN curl -fsSL -o /usr/local/bin/wp \
        "https://github.com/wp-cli/wp-cli/releases/download/v${WP_CLI_VERSION}/wp-cli-${WP_CLI_VERSION}.phar" \
    && echo "${WP_CLI_SHA512}  /usr/local/bin/wp" | sha512sum -c - \
    && chmod 0755 /usr/local/bin/wp \
    && wp --allow-root --version

# SQLite-Plugin + db.php-Drop-in (wie wordpress/dev/setup.sh); alles nach /usr/src/wordpress, der Quelle für jeden Start
RUN set -eux; \
    src=/usr/src/wordpress/wp-content; \
    curl -fsSL -o /tmp/sqlite.zip "https://downloads.wordpress.org/plugin/sqlite-database-integration.${SQLITE_VERSION}.zip"; \
    echo "${SQLITE_SHA256}  /tmp/sqlite.zip" | sha256sum -c -; \
    unzip -q /tmp/sqlite.zip -d "$src/plugins/"; \
    rm /tmp/sqlite.zip; \
    grep -q '{SQLITE_IMPLEMENTATION_FOLDER_PATH}' "$src/plugins/sqlite-database-integration/db.copy"; \
    sed -e 's#{SQLITE_IMPLEMENTATION_FOLDER_PATH}#/var/www/html/wp-content/plugins/sqlite-database-integration#' \
        -e 's#{SQLITE_PLUGIN}#sqlite-database-integration/load.php#' \
        "$src/plugins/sqlite-database-integration/db.copy" > "$src/db.php"; \
    rm -rf "$src/plugins/akismet" "$src/plugins/hello.php"

# Deutsche Sprachdateien für den Core gleich ins Image (zur Laufzeit geladen wären sie beim nächsten Deploy weg)
RUN set -eu; \
    v="$(php -r 'include "/usr/src/wordpress/wp-includes/version.php"; echo $wp_version;')"; \
    mkdir -p /usr/src/wordpress/wp-content/languages; \
    if curl -fsSL -o /tmp/de_DE.zip "https://downloads.wordpress.org/translation/core/${v}/de_DE.zip"; then \
        unzip -q -o /tmp/de_DE.zip -d /usr/src/wordpress/wp-content/languages/ && rm /tmp/de_DE.zip; \
    else \
        echo "Hinweis: de_DE für WordPress ${v} nicht geladen – Backend bleibt Englisch."; \
    fi

# PHP: Bilder kommen vom Radar als Base64 im REST-Aufruf – Grenzen dafür anheben
RUN { \
        echo 'upload_max_filesize = 32M'; \
        echo 'post_max_size = 48M'; \
        echo 'memory_limit = 256M'; \
        echo 'max_execution_time = 120'; \
        echo 'expose_php = Off'; \
    } > /usr/local/etc/php/conf.d/tamil.ini

# Apache: Datenbank-Ordner nie ausliefern, in Uploads kein PHP ausführen, Server-Version nicht verraten
RUN { \
        echo '<Directory /var/www/html/wp-content/database>'; \
        echo '    Require all denied'; \
        echo '</Directory>'; \
        echo '<Directory /var/www/html/wp-content/uploads>'; \
        echo '    <FilesMatch "\.(?i:php[0-9]?|phtml|phar)$">'; \
        echo '        Require all denied'; \
        echo '    </FilesMatch>'; \
        echo '</Directory>'; \
        echo 'ServerName localhost'; \
        echo 'ServerTokens Prod'; \
        echo 'ServerSignature Off'; \
    } > /etc/apache2/conf-available/tamil.conf \
    && a2enconf tamil

# Theme und Plugins aus dem Repo – Code gehört root, www-data liest nur
COPY wordpress/themes/tamil /usr/src/wordpress/wp-content/themes/tamil
COPY wordpress/plugins/tamil-site /usr/src/wordpress/wp-content/plugins/tamil-site
COPY wordpress/plugins/tamil-radar /usr/src/wordpress/wp-content/plugins/tamil-radar
RUN chown -R root:root /usr/src/wordpress \
    && find /usr/src/wordpress -type d -exec chmod 0755 {} + \
    && find /usr/src/wordpress -type f -exec chmod 0644 {} +

# Start-Skript (Code-Abgleich, wp-config, Installation, Zugänge) und sein PHP-Helfer
COPY wordpress/docker/start.sh wordpress/docker/wp-helfer.php /opt/tamil/
RUN chmod 0755 /opt/tamil/start.sh && chmod 0644 /opt/tamil/wp-helfer.php

EXPOSE 80
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD curl -fsS -o /dev/null http://127.0.0.1/wp-login.php || exit 1

ENTRYPOINT ["/opt/tamil/start.sh"]
CMD ["apache2-foreground"]
