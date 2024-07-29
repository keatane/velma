#!/bin/bash

echo "[*] Vulnerability Exploitation and Log Management Application -- VELMA"
echo "[*] Starting the Vulnerability Assessment Tool..."
echo

# Check if the Docker image exists
if ! docker images velma | grep -q '^velma'; then
    echo "[*] Building the Docker image..."
    echo
    docker build -t velma .
fi
echo

# Check if the first argument is "use_external"
ALL_BUT_FIRST_AND_SECOND="$@"
external_tools=0
if [ "$1" = "use_external" ]; then
    external_tools=1
    url="$2"
    ALL_BUT_FIRST_AND_SECOND="${@:3}"
fi

echo "[*] Running the Docker container..."
docker run -it --rm --network=host --name velma_vuln_assessment velma $ALL_BUT_FIRST_AND_SECOND
echo "[*] Vulnerability Assessment completed."

if [ "$external_tools" -ne "1" ]; then
    exit
fi

echo "#######################################################################"
echo "[*] Starting the Vulnerability Assessment with the following external tools:"
echo "- WP-Scan"
echo "- Dirbuster"

echo "[*] Setting up the environment for WP-Scan..."
folder="dvwp"
if [ ! -d "$folder" ]; then
    echo "Cloning the repository for WP-Scan and starting the containers..."
    git clone https://github.com/vavkamil/dvwp.git
    cd "$folder" || exit
    docker-compose up -d --build
    docker-compose run --rm wp-cli install-wp
    docker-compose up -d
    cd ..
else
    echo "Folder $folder already exists. Exiting..."
fi

echo "[*] Starting WPScan..."
docker run -it --rm --network=host wpscanteam/wpscan --url "$url" --enumerate p --api-token vLIpohNSmJ8pscEtQJq6Doyb9s3TspqHvwHXNBxCznA > wp_scan_report.txt
echo "[*] WPScan completed."

echo "[*] Starting Dirbuster"
docker run --rm --network=host hypnza/dirbuster -u "$url" >> dirbuster_report.txt
echo "[*] Dirbuster completed."

echo "[*] External Vulnerability Assessment completed."