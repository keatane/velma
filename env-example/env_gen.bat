@echo off

REM Step 1: Start services using docker-compose
echo [*] Starting services...
docker-compose up -d

REM Step 2: Wait for MySQL container to be ready
echo [*] Waiting for MySQL container to be ready...
:WAIT_LOOP
docker exec env-example-db-1 mysql --user="user" --password="password" --execute="SELECT 1;" > $null 2>&1
if errorlevel 1 (
    timeout /t 5 >nul
    goto :WAIT_LOOP
)
del $null
echo [*] MySQL container is ready.

REM Step 3: Install WordPress CLI (wp) in the WordPress container
echo [*] Installing WordPress CLI (wp) in the WordPress container...
docker exec env-example-wordpress_vuln-1 /bin/bash -c "if [ ! -f /usr/local/bin/wp ]; then curl -O https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar && chmod +x wp-cli.phar && mv wp-cli.phar /usr/local/bin/wp; fi"

REM Step 4: Install WordPress: notice this will install the LATEST version of WordPress
echo [*] Installing WordPress...
docker exec env-example-wordpress_vuln-1 /bin/bash -c "wp core install --url=http://localhost --title='Your WordPress Site' --admin_user=admin --admin_password=admin_password --admin_email=admin@example.com --allow-root"
echo [*] WordPress installation complete.

REM Step 5: Install Joomla using Joomla CLI
echo [*] Installing Joomla CLI...
docker exec env-example-joomla-1 /bin/bash -c "php installation/joomla.php install --site-name='Your Joomla Site' --admin-user=admin --admin-username=admin --admin-password=admin_password --admin-email=admin@example.com --db-type=mysql --db-host=db --db-user=user --db-pass=password --db-name=generic_db --db-prefix=joomla_"
echo [*] Joomla installation complete.


echo [*] Setup complete.
