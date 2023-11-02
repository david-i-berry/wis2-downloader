# wis2-downloader

## Usage

Run subscriber
``
flask.exe --app .\app.py run
``

Example API call (HTTP GET) to add subscribtion

``
curl http://localhost:5000/wis2/subscriptions/add?topic=cache/a/wis2/%2B/%2B/data/core/weather/surface-based-observations/%23
``

Example API call (HTTP GET) to delete subscribtion

``
curl http://localhost:5000/wis2/subscriptions/delete?topic=cache/a/wis2/%2B/%2B/data/core/weather/surface-based-observations/%23
``

Example API call (HTTP GET) to list subscribtion

``
curl http://localhost:5000/wis2/subscriptions/list
``