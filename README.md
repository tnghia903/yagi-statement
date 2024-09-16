For downloading statements, please refer to this [Google Drive](https://drive.google.com/drive/folders/1WKKjborv5gXq2REakUzd1Aqud4a3qr8P?usp=sharing)

Then, put downloaded folder in ```root-dir```

### How to run?
```docker-compose up```

Then you can access these resources:
- api: ```127.0.0.1:8080```
  - ```/api/transactions```
    - Test: ```curl --location '127.0.0.1:8080/api/transactions?page=1&limit=2'```
  - ```/api/transactions/search```
    - Test: ```curl --location '127.0.0.1:8080/api/transactions/search?transaction_details=ho%20thi&page=2&limit=1'```
- redis: ```127.0.0.1:6379``` - DB: 0 - Key: ```transactions```