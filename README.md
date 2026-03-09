# FlexiLock – Smart Locker Management System
FlexiLock is a smart locker management platform designed to improve the flexibility and convenience of locker usage
## Installation

Clone the repository:
```zsh
git clone https://github.com/yourusername/flexilock.git
cd flexilock
```
Create virtual environment:
```zsh
python -m venv venv
```
Activate environment

Windows
```zsh
venv\Scripts\activate
```
Mac / Linux
```zsh
source venv/bin/activate
```
Install dependencies:
```zsh
pip install -r requirements.txt
```
Run migrations:
```zsh
python manage.py migrate
```
Create admin account:
```zsh
python manage.py createsuperuser
```
Run server:
```zsh
python manage.py runserver
```
Open in browser:

http://127.0.0.1:8000
