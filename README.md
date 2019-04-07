# SmartAdvising API

The REST API backend which provides typical CRUD functionality for our data models, as well as built-in queuing (enqueue/dequeue) functionality for students in an online waiting room.

## Stack
* Language: Python 3
* Web Framework: Falcon 
* Database: MySQL 5.6 running on AWS RDS within a t2.micro instance
* Data Layer: SQLAlchemy, SQLService, pymysql
* API: AWS API Gateway as a reverse proxy for AWS Lambda

## Endpoints:

```
/
    /advisors: GET
    /colleges: GET
        /{college_id}: GET
            /majors: GET
                /{major_id}: GET
    /faqs: GET
    /queuers: POST, DELETE
    /queues: GET
    /students: GET, POST, DELETE
        /{student_id}: GET, DELETE, PATCH
```
