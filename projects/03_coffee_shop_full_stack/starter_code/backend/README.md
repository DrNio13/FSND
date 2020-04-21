# Coffee Shop Backend

## Getting Started

### Installing Dependencies

#### Python 3.7

Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

#### Virtual Enviornment

We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organaized. Instructions for setting up a virual enviornment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

#### PIP Dependencies

Once you have your virtual environment setup and running, install dependencies by naviging to the `/backend` directory and running:

```bash
pip install -r requirements.txt
```

This will install all of the required packages we selected within the `requirements.txt` file.

##### Key Dependencies

- [Flask](http://flask.pocoo.org/)  is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [SQLAlchemy](https://www.sqlalchemy.org/) and [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/en/2.x/) are libraries to handle the lightweight sqlite database. Since we want you to focus on auth, we handle the heavy lift for you in `./src/database/models.py`. We recommend skimming this code first so you know how to interface with the Drink model.

- [jose](https://python-jose.readthedocs.io/en/latest/) JavaScript Object Signing and Encryption for JWTs. Useful for encoding, decoding, and verifying JWTS.

## Running the server

From within the `./src` directory first ensure you are working using your created virtual environment.

Each time you open a new terminal session, run:

```bash
export FLASK_APP=api.py;
```

To run the server, execute:

```bash
flask run --reload
```

The `--reload` flag will detect file changes and restart the server automatically.

## Tasks

### Setup Auth0

1. Create a new Auth0 Account
2. Select a unique tenant domain
3. Create a new, single page web application
4. Create a new API
    - in API Settings:
        - Enable RBAC
        - Enable Add Permissions in the Access Token
5. Create new API permissions:
    - `get:drinks-detail`
    - `post:drinks`
    - `patch:drinks`
    - `delete:drinks`
6. Create new roles for:
    - Barista
        - can `get:drinks-detail`
    - Manager
        - can perform all actions

        https://drnio13.eu.auth0.com/authorize?audience=drink&response_type=token&client_id=YG3fEQiptY6uEYx2h0vSCTKhrxk5IuPi&redirect_uri=https://127.0.0.1:5000/login-results


7. Test your endpoints with [Postman](https://getpostman.com). 
    - Register 2 users - assign the Barista role to one and Manager role to the other.
    - Sign into each account and make note of the JWT.
        1user 
        eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IlJqazVOVVpDTVVJNVJVWkNORFJETWpORlFURkRRa0UxUkRJNE1VVXpPRVV5TXpKRk1qSTNSZyJ9.eyJpc3MiOiJodHRwczovL2RybmlvMTMuZXUuYXV0aDAuY29tLyIsInN1YiI6ImF1dGgwfDVlOWYwM2NkNjQ3YmViMGM3YmIxM2M4MSIsImF1ZCI6ImRyaW5rIiwiaWF0IjoxNTg3NDk3ODIzLCJleHAiOjE1ODc1MDUwMjMsImF6cCI6IllHM2ZFUWlwdFk2dUVZeDJoMHZTQ1RLaHJ4azVJdVBpIiwic2NvcGUiOiIiLCJwZXJtaXNzaW9ucyI6WyJkZWxldGU6ZHJpbmtzIiwiZ2V0OmRyaW5rLWRldGFpbHMiLCJwYXRjaDpkcmlua3MiLCJwb3N0OmRyaW5rcyJdfQ.PShpeHepShXN5n0YHI8aqzVDxAeCjmjJc1o_SptTKttQ78TiZbXyjTYx1PRjrxv3dex6i7HxmzFf2XpAQfEREA56pvwqQ_m33wtqX5n_1--KS7VUmojeUjcEhyd_EcRzCMyOBhWAUmbr2Dw2kxkAmmMCltCHNcqsXpNdOUyXBWs9U5hotQBx2m4iQdopIDRKi1Qx9nKiDWMeVm9op_iMNqtiUVo8d7k6pLbKFf9Jc-9sAhm5F5Rj0rr0JArixt9nvVO4tXC5tP77V7rUOoUwkuJvVm5munBVtZDHo8AHpkpXZKmNqPrmyoxxAZvBeWn-xElwSSmTYLE_2MtlMdk_Zw

        2user eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IlJqazVOVVpDTVVJNVJVWkNORFJETWpORlFURkRRa0UxUkRJNE1VVXpPRVV5TXpKRk1qSTNSZyJ9.eyJpc3MiOiJodHRwczovL2RybmlvMTMuZXUuYXV0aDAuY29tLyIsInN1YiI6ImF1dGgwfDVlOWYwNDI2NjQ3YmViMGM3YmIxM2NmZiIsImF1ZCI6ImRyaW5rIiwiaWF0IjoxNTg3NDkwOTMyLCJleHAiOjE1ODc0OTgxMzIsImF6cCI6IllHM2ZFUWlwdFk2dUVZeDJoMHZTQ1RLaHJ4azVJdVBpIiwic2NvcGUiOiIiLCJwZXJtaXNzaW9ucyI6WyJnZXQ6ZHJpbmstZGV0YWlscyJdfQ.VubaCohGrghSjCdwgLexr-yzBPoWDksqHMgK_a2RFM7cGCEkyXiEa7XuSAQteFe3kjbQJsOWfrfBj-3XTGd5jIq8b2QZTeKV46agOMr5hA9gfycDX6HtfGnFtaScaWnOyykfZdw5BIe1UrJErZiRl1RU8YcGzRqBz_RdTf2UJcU44TBvF4s5Uuu578pyri-OiiwPeiXeHZ4MOq1Gusq85Vp1jqRgj07dpxfw2y--dfnHL4uIS7t-dLyKg4acnPBCleJsoOf0Do_KcKfI-HMtCNteOTQ2CK-vhjxxaqnGEzrDNrDKb4EGRQEwgWQnRcHZXfD5G7mFih4tbH4lj8fAqA 

    - Import the postman collection `./starter_code/backend/udacity-fsnd-udaspicelatte.postman_collection.json`
    - Right-clicking the collection folder for barista and manager, navigate to the authorization tab, and including the JWT in the token field (you should have noted these JWTs).
    - Run the collection and correct any errors.
    - Export the collection overwriting the one we've included so that we have your proper JWTs during review!

### Implement The Server

There are `@TODO` comments throughout the `./backend/src`. We recommend tackling the files in order and from top to bottom:

1. `./src/auth/auth.py`
2. `./src/api.py`
