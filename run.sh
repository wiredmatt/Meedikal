export NODE_ENV="production" 
run = MEEDIKAL_HAS_RUN_YET

cd app

if [!$run || $run -eq 0] {
    python -m venv venv # create virtual environment

    . venv/bin/activate # activate virtual environment 
    pip install -r requirements.txt # install requirements 

    mv .example.env .env # replace dotenv file 
    mv config.example.py config.py # replace config file 
    python util/createDb.py && python util/createAdmin.py # create db and admin
    
    cd frontend/static/css
    npm install # install dependencies 
    npm run build # build and minify tailwindcss file 
    cd ../../../
    export MEEDIKAL_HAS_RUN_YET = 1
}
else {
    . venv/bin/activate
}

gunicorn --bind 0.0.0.0:80 wsgi:app && xdg-open "http://127.0.0.1/"