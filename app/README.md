# NOTES

## Setting things up

Create a virtual environment by your preferred means.

Using [venv](https://docs.python.org/3/tutorial/venv.html):

```sh
python -m venv venv
```

Activate the virtual environment:

### On Windows

```sh
./venv/Scripts/activate
```

### On Linux

```sh
source venv/bin/activate
```

Then install the dependencies:

```sh
pip install -r requirements.txt
```

## Creating the database

On first run, or when making changes to database schema, run:

```sh
python util/db.py
```

## Adding the first administrative user

The file `config.py` contains the Config class, which has the field `Admin`, you should update the values accordingly.

Once you've updated the values of the said object, run:

```sh
python util/admin.py
```

## Customizing Meedikal from its config file

The file `config.py` contains the Config class, which has the fields:

- company_name (The name of your company)
- central_data (address, email, phone, google maps embedded link)
- role_colors (the colors used to differentiate users)
- plans (name, price, popular, features and a legend)

You should update said fields according to your company's features.

## Running since

The file `frontend/static/js/index.js` has the field `RUNNING_SINCE`, this indicates since which year appointments may be queried by users. (This is useful in case you have acquired this system but you previously relied on paper documentation, and you want to add said past documentation digitally to Meedikal). In case it's not of your interest to digitize past appointments (or your company is a new one), you should set the value to the present year.

## Generating tailwindcss styles

The production styles are already generated, but if you change something you can re-build them using the following commands:

Move to the frontend/static/css directory, run:

```sh
npm install
```

### export NODE_ENV variable to production

### In windows (powershell)

```powershell
$Env:NODE_ENV="production"
```

### In linux

export NODE_ENV="production"

### Build the styles

```sh
npm run tailwind:build
npm run styles:build
```

## Enviroment variables

The file _.example.env_ should be renamed to _.env_, set the FLASK_ENV variable to either `development`, `testing` or `production`.

## Run it

### Locally

```sh
flask run
```

## Production

### In Windows

```sh
waitress-serve --port=80 wsgi:app | Start-Process "http://127.0.0.1/"
```

### In Linux

```sh
gunicorn --bind 0.0.0.0:80 wsgi:app && xdg-open "http://127.0.0.1/"
```
