import http
import json
import logging
import os
import time
from typing import Dict

import requests
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_API_TOKEN = os.getenv("TOKEN")
TELEGRAM_CHAT_ID = os.getenv("CHAT_ID")
TELEGRAM_API_URL = "https://api.telegram.org/bot"


def check_telegram_credentials() -> bool:
    """
    Checks if all required environment variables for Telegram are set.

    Returns:
        bool: True if all required environment variables are set, False otherwise.
    """
    return all([TELEGRAM_API_URL, TELEGRAM_API_TOKEN, TELEGRAM_CHAT_ID])


def load_config(config_path: str) -> dict:
    """
    Loads configuration from a JSON file.

    Args:
        config_path (str): The path to the JSON file containing the configuration.

    Returns:
        dict: The loaded configuration as a dictionary.

    Raises:
        FileNotFoundError: If the config file is not found.
        json.JSONDecodeError: If the config file is not valid.
    """
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        return config
    except FileNotFoundError as error:
        logging.error(f"Config file not found - {error}")
        raise error
    except json.JSONDecodeError as error:
        logging.error(f"Config file is not valid - {error}")
        raise error


def send_to_telegram(message: str) -> bool:
    """
    Sends a message to Telegram chat.

    Args:
        message (str): The message to send.

    Returns:
        bool: True if the message was sent successfully, False otherwise.

    Raises:
        requests.exceptions.RequestException: If the request fails.
    """
    try:
        url = f"{TELEGRAM_API_URL}{TELEGRAM_API_TOKEN}/sendMessage"
        params = {"chat_id": TELEGRAM_CHAT_ID, "text": message}

        response = requests.post(url=url, params=params, timeout=5)
        if response.status_code != http.HTTPStatus.OK:
            logging.error(f"Message not sent to Telegram. Status code: {response.status_code}, response: {response.text}")
            return False
        logging.info("Message sent to Telegram successfully.")
        return True
    except requests.exceptions.RequestException as error:
        logging.error(f"Message not sent to Telegram. Error is - {error}")
        return False


def check_status(status: int) -> bool:
    """
    Checks if the status code is 200 OK.

    Args:
        status (int): The status code to check.

    Returns:
        bool: True if the status code is 200 OK, False otherwise.
    """
    if status == http.HTTPStatus.OK:
        return True
    return False


def request_to_host(url: str) -> int | None:
    """
    Sends a GET request to the specified URL and returns the status code.

    Args:
        url (str): The URL to send the request to.

    Returns:
        int | None: The HTTP status code if the request was successful, otherwise None.


    Raises:
        requests.exceptions.RequestException: If the request fails.
    """
    try:
        response = requests.get(url, timeout=5)
        logging.info(f"Request to url: {url}")
        return response.status_code
    except requests.exceptions.RequestException as error:
        logging.error(f"Request to url: {url} failed. Error is - {error}")


def notify_status_change(url: str, is_ok: bool, site_status: Dict[str, bool]) -> None:
    """
    Notifies the user via Telegram if the status of a website has changed.

    Args:
        url (str): The URL of the website.
        is_ok (bool): True if the website is up, False otherwise.
        site_status (Dict[str, bool]): A dictionary that stores the status of each website.
    """
    if not is_ok and site_status[url]:
        text = f"Resource is down! URL: {url}"
        if send_to_telegram(message=text):
            site_status[url] = is_ok
    elif is_ok and not site_status[url]:
        text = f"Resource is up! URL: {url}"
        if send_to_telegram(message=text):
            site_status[url] = is_ok


def main() -> None:
    """
    The main function of the script.

    1. Checks if all required environment variables are set
    2. Loads configuration from a JSON file
    3. Set interval to check websites every 5 minutes
    4. Sends a GET request to each URL and checks the status code
    5. Sends notifications to Telegram chat if the status of a website has changed(Down to Up).

    Raises:
        Exception if happens any error via execution
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    if not check_telegram_credentials():
        logging.error("TELEGRAM_API_TOKEN, TELEGRAM_API_URL or TELEGRAM_CHAT_ID not found")
        raise SystemExit("Credentials not found")

    config = load_config("./config.json")
    urls = config["urls"]
    interval = config.get("interval", 300)
    site_status = {url: True for url in urls}

    while True:
        for url in urls:
            try:
                status = request_to_host(url)
                is_ok = check_status(status)
                notify_status_change(url, is_ok, site_status)
            except Exception as e:
                logging.error(f"Request to url: {url} failed. Error is - {e}")
        time.sleep(interval)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info("Script stopped by user.")
        raise SystemExit(0)
