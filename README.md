# wis2-downloader

## Usage

Install dependencies

``
pip install -r requirements.txt
``

Run subscriber

``
flask.exe --app .\app.py run
``

Example API call (HTTP GET) to add subscription

``
curl http://localhost:5000/wis2/subscriptions/add?topic=cache/a/wis2/%2B/%2B/data/core/weather/surface-based-observations/%23
``

Example API call (HTTP GET) to delete subscription

``
curl http://localhost:5000/wis2/subscriptions/delete?topic=cache/a/wis2/%2B/%2B/data/core/weather/surface-based-observations/%23
``

Example API call (HTTP GET) to list subscriptions

``
curl http://localhost:5000/wis2/subscriptions/list
``

## Notes

- Special symbols (e.g. +, #) in topics need to be URL encoded, + = %2B, # = %23.
- Initial subscriptions can be stored in subscriptions.json
- All data downloaded to ./downloads. This will be updated in future to allow configuration. 
- 2 child threads created, one to download the data and another for the subscriber
- The main program/thread is the flask app that manages the subscriptions and downloads