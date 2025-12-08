# Architecture Diagram

## Todo App Backend Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│                         User/Client                             │
│                    (Browser/Mobile App)                         │
│                                                                 │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 │ HTTPS Request
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│                      API Gateway (REST API)                     │
│                    Endpoints: /todos, /todos/{id}               │
│                                                                 │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 │ Invoke
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│                    Lambda Function (Python)                     │
│                       TodoHandler                               │
│                  (Runs in VPC - Private Subnet)                 │
│                                                                 │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 │ Read/Write
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│                    DynamoDB Table                               │
│                      TodosTable                                 │
│                   (NoSQL Database)                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│                      S3 Bucket                                  │
│                  (Static Website Hosting)                       │
│                    Test UI (index.html)                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Request Flow

1. **User** sends HTTP request (GET/POST/DELETE) to API Gateway endpoint
2. **API Gateway** validates request and invokes Lambda function
3. **Lambda** processes business logic and interacts with DynamoDB
4. **DynamoDB** stores/retrieves todo items
5. **Lambda** returns response to API Gateway
6. **API Gateway** returns response to user
7. **S3** hosts static HTML page for testing the API

## Components

| Service | Purpose | Configuration |
|---------|---------|---------------|
| **VPC** | Network isolation | 10.0.0.0/16, 2 AZs, public/private subnets |
| **API Gateway** | REST API endpoint | Regional, CORS enabled |
| **Lambda** | Serverless compute | Python 3.12, TodoHandler function |
| **DynamoDB** | NoSQL database | On-demand, partition key: id |
| **S3** | Static hosting | Public bucket, website enabled |
| **IAM** | Security | Lambda execution role with DynamoDB access |
| **CloudWatch** | Monitoring | Automatic Lambda logs |

## API Endpoints

- `GET /todos` - Retrieve all todos
- `POST /todos` - Create new todo
