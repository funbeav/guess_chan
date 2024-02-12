# Guess Chan
Guess-Chan is a web application built using Django, providing a platform for anime enthusiasts to test their character recognition skills. The main objective of the game is to guess the anime character based on their artwork. The characters are presented in the form of anime-style illustrations (known as "chans"), and players need to assemble the correct character name by selecting letters from a randomized set.

## Features
- **Authentication and Email Confirmation**: Users can create accounts, log in, and receive email confirmations for account verification.
- **Guessing Game**: Players are given a certain number of attempts to guess the anime character represented by a chans. A randomized set of letters is provided for users to construct the correct character name.
- **Attempt History**: The application keeps a log of all guessed attempts, allowing users to review their progress.
- **Language Switching**: Users can switch between languages for guessing characters. The letter sets do not change when switching languages, providing a consistent gaming experience.
- **Character Persistence**: Unsuccessfully guessed characters may reappear in the future with a certain probability. However, if a user checks the correct answer for a particular character, that character will no longer be presented in subsequent attempts.

## Gameplay
1. **Login and Authentication**:
- Users can create accounts and log in.
- Email confirmation is required for account activation.
2. **Guessing Game**:
- Players are presented with a chan (anime-style character).
- A randomized set of letters is provided for constructing the character's name.
- Users have a limited number of attempts to guess the character correctly.
3. **Attempt History**:
- The application keeps a record of all guessed attempts, showing both successful and unsuccessful attempts.
4. **Language Switching**:
- Users can switch between languages for guessing characters.
- Letter sets remain constant across language switches to maintain fairness.
5. **Character Persistence**:
- Unsuccessfully guessed characters may reappear in the future with a certain probability.
- Checking the correct answer for a character ensures it won't be presented in future attempts.

## Getting Started
Clone repository:
```shell
git clone https://github.com/funbeav/guess_chan.git
```

Run docker-compose:
```shell
docker compose build
docker compose up
```
Navigate to http://127.0.0.1:8000/

### Local Debug

For local debug install dependencies:
```shell
cd guess_chan
poetry install
```

Start only `postgres` service from docker-compose.yml and apply migrations:
```shell
poetry run python manage.py migrate
```

Setup the project and run django server locally:
```
python manage.py setup          # adding langs and admin user
python manage.py init_chans     # for populating initial chans
python manage.py runserver
```
