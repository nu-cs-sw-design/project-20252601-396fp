# Project: RentLoop

## Contributors
Al Nahiyan and Saeed AlKaabi

## Dependencies
- Language & Version
    - Python 3.11
    - HTML/CSS/JavaScript (for the UI)
- External Libraries
    - fastapi
    - uvicorn
    - sqlalchemy
    - pydantic
    - email-validator

- Other
    - SQLite database (auto-created, no setup required)
    - SHA-256 password hashing (built-in Python hashlib)

## Build Instructions
- Open a terminal
- Clone the project and enter the folder:
    git clone <your-repo-url>
    cd campus-rental
- Install the required Python libraries:
    pip install fastapi uvicorn sqlalchemy pydantic email-validator
- Run the backend server:
    uvicorn main:app --reload
- Open your web browser and go to:
    http://127.0.0.1:8000
- To access the API documentation, go to:
    http://127.0.0.1:8000/docs
- The SQLite database file (campus_rental.db) is created automatically the first time you run the server.

## Milestones:
- Milestone 1: https://docs.google.com/document/d/1NtlV_lC_xWwM-uV6avwhlX2GhohpykeKkHb5RiIDSaU/edit?usp=sharing

- Milestone 3: [https://docs.google.com/document/d/1K3qpVERM1rnA0AtRqXbA7uBTgAuDViXvqYywLr1aizs/edit?usp=sharing
](https://drive.google.com/file/d/1DewAkpTWwZwDcdkV46WPwSOfM9SKUpEc/view?usp=sharing)
