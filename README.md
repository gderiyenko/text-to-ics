# Telegam bot that queries OpenAI API and returns .ics file

## Why is this useful?
- it simplifies the process of creating calendar events
- it allows you to dictate all parameters of the event in natural language
- no need to manually fill the details
- outcoming .ics file can be imported to any calendar app right after receiving it

## Apple's Current Solution
![alt text](/preview/ios-form.JPEG "Event creation in iOS 17")

## How it works
![alt text](/preview/request.jpg "Request")

## Result
![alt text](/preview/result.jpg "Result")



Pre-requisites:
- Ubuntu 22.04.1 LTS 
- Python 3
- OpenAI API Key
- Telegram Bot Token
- Domain for serving storage of .ics files

# Install Python & Libraries
```
cd /path/to/dir
sudo apt-get update
sudo apt install python3-venv
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

# Config .env file
```
cp .env.example .env
nano .env
```


# Run on server:
```
/path/to/dir/.venv/bin/python /path/to/dir/main.py
```

# Create a daemon

To create a daemon for your Python script and ensure the service is active and enabled on your system, you can use systemd, which is the init system for Ubuntu 22.04 and most modern Linux distributions. Here's how you can do it:

```
sudo nano /etc/systemd/system/telegram_bot.service
```

```
[Unit]
Description=Python ICS Service
After=network.target

[Service]
Type=simple
User=root
Group=root
WorkingDirectory=/path/to/dir
ExecStart=/path/to/dir/.venv/bin/python /path/to/dir/main.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```



**Reload systemd to Read New Service File**:
  - After saving and closing the file, reload systemd to recognize your new service:
    ```
    sudo systemctl daemon-reload
    ```

**Enable and Start Your Service**:
  - Enable the service to start on boot:
    ```
    sudo systemctl enable python_ics.service
    ```
  - Start the service immediately:
    ```
    sudo systemctl start python_ics.service
    ```

**Check the Status of Your Service**:
  - To ensure that your service is active and running, use the following command:
    ```
    sudo systemctl status python_ics.service
    ```
    This command provides information about the service's status, including whether it is currently running, and any recent log messages.

By following these steps, you will have created a systemd service for your Python script, making it behave like a daemon. It will start automatically at boot, and it will be restarted if it fails during execution.