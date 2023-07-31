# VenomConnect App

VenomConnect is a Django web application that allows users to connect their wallets to the Venom network. It provides an interface for users to select their wallets and optionally use proxies for the connection.

## Getting Started

### Prerequisites

Before running VenomConnect, you need the following:

- Python (>=3.6)
- Django (>=4.2)
- Chrome browser (for web scraping functionality)

### Running the App

Create a virtual environment and install dependencies (example with pipenv):  

```bash
pipenv install
```

To run the Django app locally, execute the following commands:

```bash
python manage.py migrate
python manage.py runserver
```

Now, the app will be available at `http://localhost:8000/`.

## Usage

### Connecting Wallets

1. Navigate to the app's home page.
2. Select the wallets you want to connect by checking the corresponding checkboxes.
3. Optionally, select the "Use Proxies" checkbox if you want to use proxies for the connection.
4. Click the "Connect Wallets" button.
5. The app will run a background task using Celery to connect the selected wallets to the Venom network.
6. You will see a confirmation message once the task is initiated successfully.

## Configuration

The app's behavior can be configured using the following environment variables:

- `DEBUG`: Set to `True` for development and `False` for production.
- `SECRET_KEY`: Django secret key for secure sessions. It is recommended to keep this secret.
- `CELERY_BROKER_URL`: URL for the Celery broker. Default is `redis://localhost:6379/0`.
- `CELERY_RESULT_BACKEND`: URL for the Celery result backend. Default is `redis://localhost:6379/0`.