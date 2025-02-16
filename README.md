# Claims Management System
## Overview
Flask-based web application that allows users to manage insurance claims
## Features
- **User Authentication:** Sign up and log in using JWT tokens.
- **Claim Management:** Create, read, update, and delete claims.
- **Report Generation:** Generate CSV reports for claims based on their status.
- **Asynchronous Processing:** Utilize Celery to handle long-running tasks.

## Endpoints and Usage

Download a generated report by providing the task ID Requires authentication.
```bash
curl -X GET "http://localhost:5000/download/<task_id>" -H "Authorization: Bearer <access_token>"
```
Check the status of a report generation task and get the download link for the report Requires authentication.
```bash
curl -X GET "http://localhost:5000/claims/report/<task_id>" -H "Authorization: Bearer <access_token>"
```
Generate a CSV report for claims based on their status Requires authentication.
```bash
curl -X POST http://localhost:5000/claims/report -H "Authorization: Bearer <access_token>" -H "Content-Type: application/json" -d '{"status": "<status>"}'

```
Delete a claim from the database by claim ID. Requires authentication.
```bash
curl -X DELETE http://localhost:5000/claims/<claim_id> \
    -H "Authorization: Bearer <access_token>"
```
Update the status of a claim by claim ID. Requires authentication.
```bash
curl -X PUT http://localhost:5000/claims/<claim_id> \
    -H "Authorization: Bearer <access_token>" \
    -H "Content-Type: application/json" \
    -d '{"status": "<status>"}'
```
Retrieve the details of a claim by claim ID. Requires authentication.
```bash
curl -X GET http://localhost:5000/claims/<claim_id> \
    -H "Authorization: Bearer <access_token>"
```
Retrieve a list of claims with optional filters and pagination. Requires authentication.
```bash
curl -X GET "http://localhost:5000/claims?status=<status>&diagnosis_code=<diagnosis_code>&procedure_code=<procedure_code>&page=<page>&per_page=<per_page>" \
    -H "Authorization: Bearer <access_token>"
```
Add a new claim to the database. Requires authentication.
```bash
curl -X POST http://localhost:5000/claims \
    -H "Authorization: Bearer <access_token>" \
    -H "Content-Type: application/json" \
    -d '{
        "patient_name": "<patient_name>",
        "diagnosis_code": <diagnosis_code>,
        "procedure_code": <procedure_code>,
        "claim_amount": <claim_amount>"
    }'
```
Log in a user and get a JWT token.
```bash
curl -X POST http://localhost:5000/auth/login \
    -H "Content-Type: application/json" \
    -d '{
        "email": "<email>",
        "password": "<password>"
    }'

```
Sign up a new user.
```bash
curl -X POST http://localhost:5000/auth/signup \
    -H "Content-Type: application/json" \
    -d '{
        "name": "<name>",
        "email": "<email>",
        "password": "<password>"
    }'
```
## Installation
1-Clone the repository:
```bash
git clone https://github.com/Aboodalokla300900/clime_test.git
```
2-Navigate to the project directory:
```bash
cd clime_test
```
3-Install the required dependencies:
```bash
pip install -r requirements.txt
```
