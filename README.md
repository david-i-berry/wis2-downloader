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


## Workflow

```mermaid
sequenceDiagram
    
    Participant User
    Participant App
    Participant WIS2 Downloader
    Participant Global catalogue
    Participant Global broker
    Participant Global cache
    Participant Storage
    
    WIS2 Downloader ->> Global broker: Connect
        
    User->>+App: Search for data (via UI)
 
    App->>+Global catalogue: Send search request (HTTP(S) GET)
    Global catalogue->>-App: Return search result
    App ->> -User: Render results to user
    User ->> App: Click subscribe button
    App ->> WIS2 Downloader: Add subscription (HTTP(S) GET)
    WIS2 Downloader ->> App: Return list of active subscriptions
    WIS2 Downloader ->> +Global broker: Subscribe (MQTT(S))
    Global broker ->> WIS2 Downloader: Acknowledge
    Global broker ->> WIS2 Downloader: WIS2 notification(s) (MQTT(S))
    WIS2 Downloader ->> +Global cache: Request data (HTTP(S) GET)
    Global cache ->> -WIS2 Downloader: Send data
    WIS2 Downloader ->> Storage: Save to storage (FS, S3, etc)
    User ->> App: Click unsubscribe button
    App ->> WIS2 Downloader: Delete subscription (HTTP(S) GET)
    WIS2 Downloader ->> Global broker: Unubscribe (MQTT(S))
    Global broker ->> -WIS2 Downloader: Acknowledge
    WIS2 Downloader ->> App: Return list of active subscriptions
```