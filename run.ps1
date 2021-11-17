$ErrorActionPreference= 'silentlycontinue'

$Env:NODE_ENV="production" 
$run = $Env:MEEDIKAL_HAS_RUN_YET

Set-Location app

if ((-not $run) -or ($run -eq 0)) {
    python -m venv venv # create virtual environment #

    ./venv/Scripts/activate # activate virtual environment #
    pip install -r requirements.txt # install requirements #

    Move-Item .example.env .env # replace dotenv file #
    Move-Item config.example.py config.py # replace config file #
    ./util/db.py && ./util/admin.py # create db and admin #
    
    Set-Location frontend/static/css
    npm install # install dependencies #
    npm run build # build and minify tailwindcss file #
    Set-Location ../../../
    $Env:MEEDIKAL_HAS_RUN_YET = 1
}
else {
    ./venv/Scripts/activate
}

waitress-serve --port=80 wsgi:app | Start-Process "http://127.0.0.1/"