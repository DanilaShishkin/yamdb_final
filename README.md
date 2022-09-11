# ABOUT THE PROJECT:

The YaMDb project collects user reviews of works. The works are divided into categories: "Books", "Films", "Music". The list of categories can be expanded by the administrator (for example, you can add the category "Fine Art" or "Jewelry").
The works themselves are not stored in YaMDb, you can't watch a movie or listen to music here.
Grateful or outraged users leave text reviews for the works and give the work a rating in the range from one to ten. The user can leave only one review for one work.

## How to launch a project:

Clone the repository and go to it on the command line:

```
git clone #######
```

Go to dir infra/:

```
cd infra
```

Create .env file:

```
nano .env
```
Template
```
DB_ENGINE=django.db.backends.postgresql # indicate that we are working with postgresql
DB_NAME=postgres # database name
POSTGRES_USER=postgres # login to connect to the database
POSTGRES_PASSWORD=Proverka7 # password to connect to the database (set your own)
DB_HOST=db # name of the service (container)
DB_PORT=5432 # port for connecting to the database
```

Create and start project:

```
docker-compose up
```

In another console, execute migrations, create superuser and copy static files:

```
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py collectstatic --no-input 
```

Or you can load dump database:

```
docker-compose exec web python manage.py loaddata fixtures.json 
```

## authorization

###Registering a new user

Send a POST request to /api/v1/auth/signup/ specifying username and email in the request.

```
{
  "email": "string",
  "username": "string"
}
```
**Attention!!! It is forbidden to use the name 'me' as a username.**

A confirmation code will be sent in response to the email.

###Getting a JWT token

Send a POST request to /api/v1/auth/token/ specifying the username and confirmation code received by email in the request

```
{
  "username": "string",
  "confirmation_code": "string"
}
```
A token will be sent in response to the email.

```
{
  "token": "string"
}
```


# Example of using the API:

##Getting a list of all works

Send a GET request to /api/v1/titles/.
In response, you will receive a json with a list of all the works:

```
[
  {
    "count": 0,
    "next": "string",
    "previous": "string",
    "results": [
      {
        "id": 0,
        "name": "string",
        "year": 0,
        "rating": 0,
        "description": "string",
        "genre": [
          {
            "name": "string",
            "slug": "string"
          }
        ],
        "category": {
          "name": "string",
          "slug": "string"
        }
      }
    ]
  }
]
```

##Adding a work

Send a POST request to /api/v1/titles/ with a json string:

```
{
  "name": "string",
  "year": 0,
  "description": "string",
  "genre": [
    "string"
  ],
  "category": "string"
}
```
Author Danil Shishkin
MIT License
