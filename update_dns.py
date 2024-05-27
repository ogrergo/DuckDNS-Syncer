import schedule
import time
import requests
import os
from dotenv import load_dotenv
import logging

# Load environment variables from .env file
load_dotenv()

# DNS check interval in minutes
CHECK_INTERVAL = os.getenv("DNS_UPDATE_INTERVAL_MIN", default=10)

# DuckDNS API token
DUCKDNS_TOKEN = os.getenv("DUCKDNS_TOKEN")

# DuckDNS subdomain (e.g., ogrergo.duckdns.org)
DOMAIN = os.getenv("DUCKDNS_HOST")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

logger = logging.getLogger(__name__)


# Function to get the current public IP
def get_public_ip():
    try:
        response = requests.get("https://api.ipify.org?format=json")
        response.raise_for_status()
        ip = response.json().get("ip")
        return ip
    except requests.RequestException as e:
        logger.error(f"Error fetching public IP: {e}", exc_info=True)
        return None


# Function to update the DNS record
def update_dns_record(ip):
    try:
        url = f"https://www.duckdns.org/update?domains={DOMAIN}&token={DUCKDNS_TOKEN}&ip={ip}"
        response = requests.get(url)
        response.raise_for_status()
        return "OK" in response.text
    except requests.RequestException as e:
        logger.error(f"Error updating DNS record: {e}", exc_info=True)
        return False


def check_and_update_ip():
    public_ip = get_public_ip()
    if public_ip is None:
        logger.error("Public IP fetch failed; skipping DNS update.")
        return

    logger.info(f"Current public IP: {public_ip}")

    if update_dns_record(public_ip):
        logger.info(f"DNS record updated to {public_ip}")
    else:
        logger.error("Failed to update DNS record")


def main():
    schedule.every(CHECK_INTERVAL).minutes.do(check_and_update_ip)

    logger.info("Starting DNS updater service")

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()
