# Step-by-Step Instructions: Building Todo App Backend on AWS

## Table of Contents
1. [Create VPC](#step-1-create-vpc)
2. [Create DynamoDB Table](#step-2-create-dynamodb-table)
3. [Create Lambda Function](#step-3-create-lambda-function)
4. [Create API Gateway](#step-4-create-api-gateway)
5. [Create S3 Bucket for Testing](#step-5-create-s3-bucket-for-testing)
6. [Test End-to-End](#step-6-test-end-to-end)
7. [Cleanup](#step-7-cleanup)

---

## Step 1: Create VPC

**Why?** A VPC provides network isolation and security for your AWS resources. While Lambda can run without VPC, using one demonstrates best practices for production environments.

### 1.1 Create the VPC

1. Navigate to **AWS Console** → Search for **VPC** → Click **VPC**
2. Click **Create VPC** button (orange button, top right)
3. Select **VPC and more** (this creates VPC with subnets automatically)
4. Enter the following:
   - **Name tag auto-generation**: `todo-app`
   - **IPv4 CIDR block**: `10.0.0.0/16`
   - **Number of Availability Zones**: `2`
   - **Number of public subnets**: `2`
   - **Number of private subnets**: `2`
   - **NAT gateways**: `None` (to save costs for this demo)
   - **VPC endpoints**: `None`
5. Click **Create VPC** (screenshot: VPC creation preview page)
6. Wait 2-3 minutes for creation to complete
7. Click **View VPC** when done

**What was created?**
- 1 VPC
- 2 public subnets (in different AZs)
- 2 private subnets (in different AZs)
- 1 Internet Gateway (attached to VPC)
- Route tables for public and private subnets

---

## Step 2: Create DynamoDB Table

**Why?** DynamoDB is a fully managed NoSQL database perfect for storing todo items. It's serverless, scales automatically, and integrates seamlessly with Lambda.

### 2.1 Create Table

1. Navigate to **AWS Console** → Search for **DynamoDB** → Click **DynamoDB**
2. Click **Create table** (orange button)
3. Enter the following:
   - **Table name**: `TodosTable`
   - **Partition key**: `id` (String)
   - Leave **Sort key** empty
4. Under **Table settings**, select **Customize settings**
5. **Table class**: `DynamoDB Standard`
6. **Read/write capacity settings**: Select **On-demand**
   - **Why?** On-demand mode automatically scales and you only pay for what you use
7. Leave other settings as default
8. Click **Create table** (screenshot: DynamoDB table configuration)
9. Wait 30 seconds for table to become **Active**

**What you created:** A NoSQL table that will store todo items with `id` as the primary key.

---

## Step 3: Create Lambda Function

**Why?** Lambda runs your code without managing servers. It will handle all business logic for creating, reading, and deleting todos.

### 3.1 Create IAM Role for Lambda

1. Navigate to **AWS Console** → Search for **IAM** → Click **IAM**
2. Click **Roles** in left sidebar
3. Click **Create role**
4. Select **AWS service** → Select **Lambda** → Click **Next**
5. In the search box, type and select these policies:
   - `AWSLambdaBasicExecutionRole` (for CloudWatch logs)
   - `AmazonDynamoDBFullAccess` (for DynamoDB access)
6. Click **Next**
7. **Role name**: `TodoLambdaRole`
8. Click **Create role** (screenshot: IAM role creation)

### 3.2 Create Lambda Function

1. Navigate to **AWS Console** → Search for **Lambda** → Click **Lambda**
2. Click **Create function** (orange button)
3. Select **Author from scratch**
4. Enter the following:
   - **Function name**: `TodoHandler`
   - **Runtime**: `Python 3.12`
   - **Architecture**: `x86_64`
5. Expand **Change default execution role**
   - Select **Use an existing role**
   - Choose **TodoLambdaRole** from dropdown
6. Click **Create function** (screenshot: Lambda function creation)

### 3.3 Add Function Code

1. You'll be on the function's **Code** tab
2. Delete the existing code in the `lambda_function.py` editor
3. Copy and paste the following code:

```python
import json
import boto3
import uuid
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('TodosTable')

def lambda_handler(event, context):
    http_method = event['httpMethod']
    path = event['path']
    
    try:
        if http_method == 'GET' and path == '/todos':
            return get_todos()
        elif http_method == 'POST' and path == '/todos':
            return create_todo(json.loads(event['body']))
        elif http_method == 'DELETE' and '/todos/' in path:
            todo_id = path.split('/')[-1]
            return delete_todo(todo_id)
        else:
            return response(400, {'error': 'Invalid request'})
    except Exception as e:
        return response(500, {'error': str(e)})

def get_todos():
    result = table.scan()
    return response(200, {'todos': result['Items']})

def create_todo(body):
    todo_id = str(uuid.uuid4())
    item = {
        'id': todo_id,
        'title': body['title'],
        'completed': False,
        'createdAt': datetime.utcnow().isoformat()
    }
    table.put_item(Item=item)
    return response(201, item)

def delete_todo(todo_id):
    table.delete_item(Key={'id': todo_id})
    return response(200, {'message': 'Todo deleted'})

def response(status_code, body):
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(body)
    }
```

4. Click **Deploy** (button above the code editor)
5. Wait for "Successfully deployed" message

**Code explanation:**
- `lambda_handler`: Entry point that routes requests based on HTTP method and path
- `get_todos()`: Retrieves all todos from DynamoDB
- `create_todo()`: Creates a new todo with auto-generated ID
- `delete_todo()`: Deletes a todo by ID
- CORS headers allow browser access

### 3.4 Test Lambda Function

1. Click **Test** tab (next to Code tab)
2. Click **Create new event**
3. **Event name**: `CreateTodoTest`
4. Replace the JSON with:

```json
{
  "httpMethod": "POST",
  "path": "/todos",
  "headers": {
    "Content-Type": "application/json"
  },
  "body": "{\"title\": \"Learn AWS Services\"}"
}
```

5. Click **Save**
6. Click **Test** button (screenshot: Lambda test configuration)
7. Check **Execution results** - you should see:
   - Status: **Succeeded**
   - Response with `statusCode: 201` and the created todo

### 3.5 Verify in DynamoDB

1. Go back to **DynamoDB** → **Tables** → **TodosTable**
2. Click **Explore table items**
3. You should see 1 item with your todo (screenshot: DynamoDB items view)

---

## Step 4: Create API Gateway

**Why?** API Gateway provides a public HTTPS endpoint that clients can call. It routes requests to your Lambda function and handles authentication, throttling, and more.

### 4.1 Create REST API

1. Navigate to **AWS Console** → Search for **API Gateway** → Click **API Gateway**
2. Click **Create API** (orange button)
3. Find **REST API** (not Private or HTTP API) → Click **Build**
4. Select **New API**
5. Enter the following:
   - **API name**: `TodoAPI`
   - **Description**: `REST API for Todo application`
   - **Endpoint Type**: `Regional`
6. Click **Create API** (screenshot: API Gateway creation)

### 4.2 Create Resources and Methods

**Create /todos resource:**

1. Click **Actions** dropdown → Select **Create Resource**
2. Enter:
   - **Resource Name**: `todos`
   - **Resource Path**: `/todos`
   - Check **Enable API Gateway CORS**
3. Click **Create Resource**

**Add GET method to /todos:**

1. With `/todos` selected, click **Actions** → **Create Method**
2. Select **GET** from dropdown → Click the checkmark
3. Configure:
   - **Integration type**: `Lambda Function`
   - **Use Lambda Proxy integration**: Check this box (important!)
   - **Lambda Region**: Select your region (e.g., us-east-1)
   - **Lambda Function**: Type `TodoHandler` and select it
4. Click **Save**
5. Click **OK** on the permission popup (screenshot: GET method setup)

**Add POST method to /todos:**

1. With `/todos` selected, click **Actions** → **Create Method**
2. Select **POST** from dropdown → Click checkmark
3. Configure same as GET:
   - **Integration type**: `Lambda Function`
   - **Use Lambda Proxy integration**: Check this box
   - **Lambda Function**: `TodoHandler`
4. Click **Save** → Click **OK**


### 4.3 Deploy API

1. Click **Actions** → **Deploy API**
2. **Deployment stage**: Select **[New Stage]**
3. **Stage name**: `prod`
4. Click **Deploy**
5. Copy the **Invoke URL** at the top (e.g., `https://abc123.execute-api.us-east-1.amazonaws.com/prod`)
   - **Save this URL** - you'll need it for testing! (screenshot: API deployed with invoke URL)

**What you created:** A public REST API with three endpoints:
- `GET /todos` - List all todos
- `POST /todos` - Create a todo

---

## Step 5: Create S3 Bucket for Testing

**Why?** S3 can host a simple HTML page to test your API from a browser. This demonstrates static website hosting.

### 5.1 Create Bucket

1. Navigate to **AWS Console** → Search for **S3** → Click **S3**
2. Click **Create bucket**
3. Enter:
   - **Bucket name**: `todo-app-test-<your-initials>-<random-number>` (must be globally unique)
     - Example: `todo-app-test-jd-12345`
   - **AWS Region**: Select your region
4. **Uncheck** "Block all public access"
   - Check the acknowledgment box
5. Leave other settings as default
6. Click **Create bucket** (screenshot: S3 bucket creation)

### 5.2 Enable Static Website Hosting

1. Click on your bucket name
2. Go to **Properties** tab
3. Scroll to **Static website hosting** → Click **Edit**
4. Select **Enable**
5. **Index document**: `index.html`
6. Click **Save changes**
7. Scroll back to **Static website hosting** section
8. Copy the **Bucket website endpoint** URL (screenshot: Static website hosting enabled)

### 5.3 Create Test HTML Page

1. Go to **Objects** tab
2. Click **Create folder** → Name it `test` → Click **Create folder**
3. Click **Upload**
4. Click **Add files** → Create a file named `index.html` on your computer with this content:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Todo App Test</title>
    <style>
        body { font-family: Arial; max-width: 600px; margin: 50px auto; padding: 20px; }
        input, button { padding: 10px; margin: 5px; }
        .todo { padding: 10px; border: 1px solid #ddd; margin: 5px 0; }
    </style>
</head>
<body>
    <h1>Todo App Test</h1>
    <div>
        <input type="text" id="todoInput" placeholder="Enter todo title">
        <button onclick="createTodo()">Add Todo</button>
        <button onclick="getTodos()">Refresh</button>
    </div>
    <div id="todos"></div>

    <script>
        const API_URL = 'YOUR_API_GATEWAY_URL_HERE';

        async function getTodos() {
            const response = await fetch(`${API_URL}/todos`);
            const data = await response.json();
            const todosDiv = document.getElementById('todos');
            todosDiv.innerHTML = data.todos.map(todo => `
                <div class="todo">
                    ${todo.title} 
                    <button onclick="deleteTodo('${todo.id}')">Delete</button>
                </div>
            `).join('');
        }

        async function createTodo() {
            const title = document.getElementById('todoInput').value;
            await fetch(`${API_URL}/todos`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({title})
            });
            document.getElementById('todoInput').value = '';
            getTodos();
        }

        async function deleteTodo(id) {
            await fetch(`${API_URL}/todos/${id}`, {method: 'DELETE'});
            getTodos();
        }

        getTodos();
    </script>
</body>
</html>
```

5. **Important**: Replace `YOUR_API_GATEWAY_URL_HERE` with your actual API Gateway invoke URL from Step 4.4
6. Upload the file to S3
7. Click **Upload**

### 5.4 Add Bucket Policy

1. Go to **Permissions** tab
2. Scroll to **Bucket policy** → Click **Edit**
3. Paste this policy (replace `YOUR-BUCKET-NAME` with your actual bucket name):

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::YOUR-BUCKET-NAME/*"
        }
    ]
}
```

4. Click **Save changes** (screenshot: Bucket policy configuration)

---

## Step 6: Test End-to-End

### 6.1 Test with API Gateway Console

1. Go to **API Gateway** → **TodoAPI** → **Resources**
2. Click **POST** method under `/todos`
3. Click **Test** (lightning bolt icon)
4. In **Request Body**, enter:

```json
{
    "title": "Complete AWS Capstone"
}
```

5. Click **Test** button
6. Check response - should show `Status: 201` with the created todo (screenshot: API Gateway test)

### 6.2 Test with Browser (S3 Website)

1. Open the S3 website endpoint URL in your browser
2. You should see the Todo App Test page
3. Enter a todo title and click **Add Todo**
4. Click **Refresh** to see all todos

### 6.3 Test with curl (Optional)

If you have curl installed:

```bash
# Get all todos
curl https://YOUR-API-URL/prod/todos

# Create a todo
curl -X POST https://YOUR-API-URL/prod/todos \
  -H "Content-Type: application/json" \
  -d '{"title": "Test from curl"}'

# Delete a todo (replace ID)
curl -X DELETE https://YOUR-API-URL/prod/todos/YOUR-TODO-ID
```

### 6.4 Verify in CloudWatch Logs

1. Navigate to **CloudWatch** → **Log groups**
2. Find `/aws/lambda/TodoHandler`
3. Click on the latest log stream
4. You'll see logs from your Lambda executions (screenshot: CloudWatch logs)

**What you've proven:** Your entire architecture works! Requests flow from browser → API Gateway → Lambda → DynamoDB and back.

---

## Step 7: Cleanup

**Important:** Delete resources to avoid charges.

### 7.1 Delete API Gateway

1. Go to **API Gateway** → **APIs**
2. Select **TodoAPI**
3. Click **Actions** → **Delete**
4. Type the API name to confirm → Click **Delete**

### 7.2 Delete Lambda Function

1. Go to **Lambda** → **Functions**
2. Select **TodoHandler**
3. Click **Actions** → **Delete**
4. Type "delete" to confirm → Click **Delete**

### 7.3 Delete IAM Role

1. Go to **IAM** → **Roles**
2. Search for **TodoLambdaRole**
3. Select it → Click **Delete**
4. Type the role name → Click **Delete**

### 7.4 Delete DynamoDB Table

1. Go to **DynamoDB** → **Tables**
2. Select **TodosTable**
3. Click **Delete**
4. Type "delete" to confirm → Click **Delete**

### 7.5 Delete S3 Bucket

1. Go to **S3** → **Buckets**
2. Select your bucket
3. Click **Empty** → Type "permanently delete" → Click **Empty**
4. Click **Delete** → Type bucket name → Click **Delete**

### 7.6 Delete VPC

1. Go to **VPC** → **Your VPCs**
2. Select **todo-app-vpc**
3. Click **Actions** → **Delete VPC**
4. Type "delete" to confirm → Click **Delete**
   - This will delete all associated subnets, route tables, and IGW

---

## Troubleshooting

### Lambda returns 500 error
- Check CloudWatch logs for the Lambda function
- Verify IAM role has DynamoDB permissions
- Ensure DynamoDB table name matches in code

### API Gateway returns 403 Forbidden
- Verify Lambda function has resource-based policy allowing API Gateway
- Check if API is deployed to the correct stage

### CORS errors in browser
- Ensure CORS is enabled on all methods
- Verify Lambda returns CORS headers in response
- Redeploy API after CORS changes

### S3 website not accessible
- Check bucket policy allows public read
- Verify static website hosting is enabled
- Ensure index.html is public

---

## Best Practices Demonstrated

1. **Serverless Architecture**: No servers to manage, automatic scaling
2. **Least Privilege**: IAM role has only necessary permissions
3. **CORS Configuration**: Enables secure browser access
4. **Error Handling**: Lambda catches and returns proper error responses
5. **Resource Naming**: Consistent naming convention for easy identification
6. **Logging**: CloudWatch automatically captures Lambda logs
7. **API Versioning**: Using deployment stages (prod)

---

## Next Steps

To enhance this project:
- Add authentication with Amazon Cognito
- Implement input validation
- Add update (PUT) functionality
- Use DynamoDB streams to trigger notifications
- Add CloudFront for global content delivery
- Implement API throttling and usage plans
- Add X-Ray for distributed tracing
- Use AWS WAF for API protection

---

## Summary

You've built a complete serverless application using:
- **VPC** for network isolation
- **DynamoDB** for data storage
- **Lambda** for compute
- **API Gateway** for REST API
- **S3** for static hosting
- **IAM** for security
- **CloudWatch** for monitoring

All services integrate seamlessly to create a production-ready architecture!
