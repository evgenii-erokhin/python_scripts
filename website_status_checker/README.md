## Simple resource monitor

This script checks the availability of the website every 5 minutes and sends notifications to the Telegram chat if the website status has changed from available to unavailable. And if the website is working again, the script notifies that the website is working again.

This script can be used as a simple additional monitoring tool.
### Requirements
- requests
- python-dotenv

### Usage

1. Clone the repository and go to working directory

```
git clone git@github.com:evgenii-erokhin/python_scripts.git
cd python_scripts
```

2. Create and activate a virtual environment
```
python3 -m venv venv
source venv/bin/activate
```

3. Install the required packages
```
pip install -r ./python_scripts/website_status_checker/requirements.txt
```
4. Create a .env file in the project directory of the repository
```
touch ./python_scripts/website_status_checker/.env
```

5. 5. Set environment variables in the `.env` file as shown in the `example.env` file located in the project directory.

```
TOKEN=your_telegram_bot_token
CHAT_ID=your_telegram_chat_id
```

6. Create a `config.json` file with your resources for monitoring:
```
{
  "urls": [
    "https://example.com",
    "https://another-site.com"
  ],
  "interval": 300
}
```
7. Run the script
```

python3 ./python_scripts/website_status_checker/main.py
```