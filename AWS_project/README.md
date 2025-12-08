# AWS Capstone Project: Todo App Backend

## Overview

This project demonstrates a serverless Todo application backend built entirely using AWS services through the AWS Console. It showcases how multiple AWS services integrate to create a scalable, production-ready API.

## Architecture

The application uses:
- **API Gateway**: REST API endpoint for client requests
- **Lambda**: Serverless compute for business logic
- **DynamoDB**: NoSQL database for storing todos
- **S3**: Static website hosting for a simple test UI
- **VPC**: Network isolation (Lambda in VPC for security best practices)

## What You'll Learn

- Creating a VPC with public and private subnets
- Setting up DynamoDB tables
- Writing Lambda functions in Python
- Configuring API Gateway REST APIs
- Integrating services together
- Testing end-to-end workflows

## Project Structure

```
capstone-project/
 ├── README.md
 ├── architecture/
 │    └── diagram.mmd
 ├── docs/
 │    └── step-by-step-instructions.md
 ├── lambda/
 │    └── index.py
 └── sample-data/
      └── test-event.json
```

## Getting Started

Follow the detailed instructions in `docs/step-by-step-instructions.md` to build this project from scratch using only the AWS Console.

## Estimated Time

2-3 hours for complete setup

## Cost Estimate

This project uses AWS Free Tier eligible services. Expected cost: $0-5/month if staying within free tier limits.

## Cleanup

Remember to delete all resources after testing to avoid charges:
1. Delete API Gateway
2. Delete Lambda function
3. Delete DynamoDB table
4. Empty and delete S3 bucket
5. Delete VPC (will delete associated subnets, route tables, IGW)
