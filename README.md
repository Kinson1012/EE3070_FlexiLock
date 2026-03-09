CityU FlexiLock – Smart Locker Management System

CityU FlexiLock is a smart locker management platform designed to improve the flexibility and convenience of locker usage at City University of Hong Kong. The system replaces traditional physical locks with a digital reservation and access system, allowing students to reserve lockers online and unlock them using QR codes.

This project demonstrates how web technologies and IoT devices (such as ESP32) can be integrated to build a modern smart locker system.

Project Overview

Currently, most lockers at CityU require students to apply annually and use traditional physical locks. These lockers are often old and lack flexibility. Students may forget passwords or lose keys, and short-term locker usage is difficult.

CityU FlexiLock aims to solve these problems by providing:

Online locker reservation

Flexible short-term or long-term booking

QR code based locker access

Real-time locker status monitoring

Administrative control for maintenance and management

Key Features
User Functions

User registration and login system

Locker reservation system

Flexible booking durations

Reservation countdown timer

QR code generation for locker access

Reservation history tracking

Campus locker map view

Reservation timeline calendar

Automatic reservation expiry

Admin Functions

Locker maintenance control

Disable or reopen lockers

View locker activity logs

Monitor locker status across campus

Smart Locker Simulation

The system simulates the full lifecycle of a smart locker:

Reserve locker → countdown begins → reservation active
→ QR unlock access → reservation expires → locker released
System Architecture

The system consists of two main components:

Web Platform

Django backend

SQLite database

HTML / CSS / JavaScript frontend

IoT Locker Controller (Future Integration)

ESP32 microcontroller

Electronic lock mechanism

QR code validation via web API

Example workflow:

User reserves locker
↓
System generates reservation token
↓
User scans QR code
↓
ESP32 verifies reservation via API
↓
Locker unlocks
Technologies Used

Backend:

Django

Python

SQLite

Frontend:

HTML5

CSS3

JavaScript

FullCalendar (reservation timeline)

Other:

QR Code generation

Git / GitHub version control

Project Structure

Example structure:

EE3070_FlexiLock
│
├── locker/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── templates/
│   │   └── locker/
│   │       ├── index.html
│   │       ├── dashboard.html
│   │       ├── reserve_form.html
│   │       ├── campus_map.html
│   │       ├── reservation_timeline.html
│   │       └── admin_lockers.html
│
├── logs/
│   └── reservation.log
│
├── manage.py
└── README.md
Installation

Clone the repository:

git clone https://github.com/yourusername/flexilock.git
cd flexilock

Create virtual environment:

python -m venv venv

Activate environment:

Windows

venv\Scripts\activate

Mac/Linux

source venv/bin/activate

Install dependencies:

pip install -r requirements.txt

Run migrations:

python manage.py migrate

Create admin account:

python manage.py createsuperuser

Run server:

python manage.py runserver

Open:

http://127.0.0.1:8000