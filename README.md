# wis2-downloader

## Usage

Install dependencies

``
pip install -r requirements.txt
``

Run subscriber

``
flask.exe --Front end .\Front end.py run
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
- The main program/thread is the flask Front end that manages the subscriptions and downloads


## Workflow

```mermaid
sequenceDiagram
    
    Participant User
    box WIS2 Downloader
    Participant Front end
    Participant Back end
    end
    Participant Storage
    box WIS2 Global Services
    Participant Global catalogue
    Participant Global broker
    Participant Global cache
    end
    Back end ->> Global broker: Connect
        
    User->>Front end: Search for data (via UI)
 
    Front end->>Global catalogue: Send search request (HTTP(S) GET)
    Global catalogue->>Front end: Return search result
    Front end ->> User: Render results to user
    User ->> Front end: Click subscribe button
    Front end ->> Back end: Add subscription (HTTP(S) GET)
    Back end ->> Front end: Return list of active subscriptions
    Back end ->> Global broker: Subscribe (MQTT(S))
    Global broker ->> Back end: Acknowledge
    Global broker ->> Back end: WIS2 notification(s) (MQTT(S))
    Back end ->> Global cache: Request data (HTTP(S) GET)
    Global cache ->> Back end: Send data
    Back end ->> Storage: Save to storage (FS, S3, etc)
    User ->> Front end: Click unsubscribe button
    Front end ->> Back end: Delete subscription (HTTP(S) GET)
    Back end ->> Global broker: Unubscribe (MQTT(S))
    Global broker ->> Back end: Acknowledge
    Back end ->> Front end: Return list of active subscriptions
```