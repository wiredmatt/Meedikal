export NODE_ENV="production" 

cd app

if [[ !$MEEDIKAL_HAS_RUN_YET ]] || [[$MEEDIKAL_HAS_RUN_YET -eq 0]]
then
    python -m venv venv # create virtual environment

    . venv/bin/activate # activate virtual environment 
    pip install -r requirements.txt # install requirements 

    mv .example.env .env # replace dotenv file 
    mv config.example.py config.py # replace config file 
    python util/db.py && python util/admin.py # create db and admin
    
    cd frontend/static/css
    npm install # install dependencies 
    npm run build # build and minify tailwindcss file 
    cd ../../../
    export MEEDIKAL_HAS_RUN_YET = 1
else
    . venv/bin/activate
fi

gunicorn --bind 0.0.0.0:80 wsgi:app && xdg-open "http://127.0.0.1/"