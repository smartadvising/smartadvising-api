# SmartAdvising API

The REST API backend which provides typical CRUD functionality for our data models, as well as built-in queuing (enqueue/dequeue) functionality for students in an online waiting room.

### Web Language and Framework
The API is written in Python 3.7 within the [Falcon](https://falconframework.org/), the bare-metal web API framework for Python 3. As an alternative to Flask, Falcon has a reduced feature set specifically targeted towards building fast, REST APIs where all client data is JSON and where throughput is prioritized.

![](http://pycnic.nullism.com/images/pycnic-bench.png)

#### Database
Our database is provided as a service by [AWS RDS](https://aws.amazon.com/rds/), in which there's a t2.micro instance running MySQL 5.6 (which is within free tier usage restrictions).


### Data Model
##### SQLAlchemy
a Python SQL toolkit and Object Relational Mapper (ORM) "[which] provides the data mapper pattern, where classes can be mapped to the database in open ended, multiple ways - allowing the object model and database schema to develop in a cleanly decoupled way from the beginning"
##### SQLService
an interface layer to SQLAlchemy's session manager and ORM layer which provides a single point to:
    1.  manage your database connection and sessions, and
    2. create, reflect, or drop your database/SQLAlchemy Model objects
##### PyMySQL
a pure MySQL client in Python with connection pooling, which is optimal in AWS Lambda because of ["lifecycle" and in-memory caching](https://medium.com/@tjholowaychuk/aws-lambda-lifecycle-and-in-memory-caching-c9cd0844e072) of data

#### Hosting
The core services, primarily the API, are provided by [AWS Lambda](https://aws.amazon.com/lambda/), a ["serverless"](https://aws.amazon.com/serverless/) architectural pattern which "allows you to build and run applications and services without thinking about servers", removing manual infrastructure management tasks such as server or cluster provisioning (or when scaling: capacity provisioning), patching, or OS maintenance".

#### API Endpoints:

The API endpoints are provided as a service by [AWS API Gateway](https://aws.amazon.com/api-gateway/), acting a reverse proxy for incoming API requests, making possible building an API with the setup of a single API method. "The Lambda proxy integration allows the client to call a single Lambda function in the backend. The function accesses many resources or features of other AWS services, including calling other Lambda functions."

See below for the registered resources and their associated methods.

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
