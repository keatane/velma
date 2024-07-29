@echo off
echo [*] Vulnerability Exploitation and Log Management Application -- VELMA  
echo [*] Starting the Vulnerability Assessment Tool...
echo.
REM Check if the Docker image exists
docker images velma | findstr /R /C:"^velma"
IF %ERRORLEVEL% NEQ 0 (
    echo [*] Building the Docker image...
    echo.
    docker build -t velma .
)
echo.

REM Check if the first argument is "use_external"
set ALL_BUT_FIRST_AND_SECOND=%*
set external_tools=0
IF "%1"=="use_external" (
    set external_tools=1
    set url="%2
    for /f "tokens=2,* delims= " %%a in ("%*") do set ALL_BUT_FIRST_AND_SECOND=%%b
)

echo [*] Running the Docker container...
docker run -it --rm --network=host --name velma_vuln_assessment velma %ALL_BUT_FIRST_AND_SECOND%
echo [*] Vulnerability Assessment completed.

if not "%external_tools%" == "1" exit /b

echo "#######################################################################"
echo [*] Starting the Vulnerability Assessment with the following external tools:
echo - WP-Scan
echo - Dirbuster

echo [*] Setting up the environment for WP-Scan...
set folder="dvwp"
if not exist %folder% (
    echo "Cloning the repository for WP-Scan and starting the containers..."
    git clone https://github.com/vavkamil/dvwp.git
    cd %folder%
    docker-compose up -d --build
    docker-compose run --rm wp-cli install-wp
    docker-compose up -d
) else (
    echo "Folder %folder% already exists. Exiting..."
)

echo [*] Starting WPScan...
docker run -it --rm --network=host wpscanteam/wpscan --url %url% --enumerate p --api-token vLIpohNSmJ8pscEtQJq6Doyb9s3TspqHvwHXNBxCznA > wp_scan_report.txt
echo [*] WPScan completed.

echo [*] Starting Dirbuster
docker run --rm --network=host hypnza/dirbuster -u %url% >> dirbuster_report.txt
echo [*] Dirbuster completed.

echo [*] External Vulnerability Assessment completed.