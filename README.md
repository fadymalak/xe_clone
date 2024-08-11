# XE Clone Project

## Introduction

This project is a clone of the XE currency converter, allowing users to retrieve and convert currency values also register and send money. The application is built with Django, Django REST Framework, HTML, CSS and uses external APIs for currency data.

## How to Use the Project

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/fadymalak/xe_clone
   ```

2. **Create a Virtual Environment and activate it:**

   ```bash
   python -m venv venv

   source venv\Scripts\activate
   ```

3. **Install Dependencies:**

   ```bash
   pip install -r requirements.txt

   pre-commit install
   ```

4. **Set Up the Database:**
   If you want to use MySQL as the database, start the database using Docker Compose:

   ```bash
   docker-compose up
   ```

5. **Set Environment Variables:**

   - Copy the .env-example file to .env and set the necessary environment variables.
   - if you used docker-compose set `REDIS_ACTIVE=True` `and MYSQL_ACTIVE=True`

6. **Apply Migrations and run the server:**

   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

   Visit `http://localhost:8000` in your browser.

7. **To run the test:**

   ```bash
   pytest
   ```

8. **To see manage.py available commands:**
   ```bash
   python manage.py
   ```
   - There are some commands to seed the database with currency.

## Usage

- To use the site access `http://127.0.0.1:8000/app/`
- For the documentmentation of existing rest apis visit `http://127.0.0.1:8000/api/docs/`
