# Translate App

Translate App is a Django-based web application that allows users to translate text between multiple languages using the MyMemory Translation API.

This project demonstrates API integration, backend processing, and frontend form handling in a simple and structured way.

---

## Overview

The application enables users to:

- Enter text for translation
- Select source and target languages
- Receive translated output instantly

It showcases how to integrate third-party APIs into a Django application and handle responses efficiently.

---

## Features

- Multi-language text translation
- Integration with MyMemory Translation API
- Backend processing using Django views
- Clean frontend using HTML, CSS, and JavaScript
- Error handling for invalid input or API failure

---

## Tech Stack

Backend:
- Django (Python)

Frontend:
- HTML
- CSS
- JavaScript

API:
- MyMemory Translation API

Database:
- SQLite (Default Django configuration)

---

## Installation & Setup

Clone the repository:

git clone https://github.com/aathithiyan45/translate_app.git  
cd translate_app  

Create virtual environment:

python -m venv env  

Activate environment:

Mac/Linux:
source env/bin/activate  

Windows:
env\Scripts\activate  

Install dependencies:

pip install -r requirements.txt  

Run migrations:

python manage.py migrate  

Start development server:

python manage.py runserver  

Open in browser:
http://127.0.0.1:8000

---

## How It Works

1. User submits text through a form.
2. Django view processes the request.
3. Backend sends a request to MyMemory API.
4. API returns translated text.
5. Result is displayed on the webpage.

---

## Learning Outcomes

- Django request-response cycle
- API integration using Python
- Handling JSON responses
- Form submission and validation
- Structured backend logic

---

## Future Improvements

- Add automatic language detection
- Store translation history
- Improve UI styling
- Add authentication system

---

## License

MIT License
