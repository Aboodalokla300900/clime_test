from flask import request, jsonify, Flask, send_file
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from _db_helper import _db_query
from _validator import _validator
import csv
from celery import Celery
import uuid

# Initialize Flask application
app = Flask(__name__)

# Set Flask secret key for session management
app.config['SECRET_KEY'] = "4b5f41a0d9a7c3e813bb642b7c2e1f29a5c92b4a614f17d24b8f32ed"

# Initialize JWT manager for handling authentication tokens
JWTManager(app)

# Initialize Celery for asynchronous task processing
celery = Celery(app.name, broker='pyamqp://guest@localhost//')

# Dictionary to store job status by job ID
jobs = {}

class Report:
    # Endpoint to download report by task ID
    @app.route("/download/<task_id>", methods=['GET'])
    @jwt_required()
    def download_report(task_id):
        csv_file_path = f"{task_id}_claims_report.csv"
        try:
            # Serve the CSV file as an attachment
            return send_file(csv_file_path, as_attachment=True)
        except FileNotFoundError:
            # Return error if file is not found
            return jsonify({"error": True, "message": "File not found or has been removed"}), 404

    # Endpoint to check report status and download link by task ID
    @app.route("/claims/report/<task_id>", methods=['GET'])
    @jwt_required()
    def check_job_id(task_id):
        # Return the status of the job and download link
        if task_id in jobs:
            if str(jobs[task_id])=="completed":
                return jsonify({"status": jobs[task_id], "link": f"http://localhost:5000/download/{task_id}"})
            else:
                return jsonify({"status": jobs[task_id]})
        else:
            return jsonify({"message": "Cannot find job ID"}), 404
    # Celery task to create CSV report
    @celery.task(bind=True)
    def create_csv_report(self, data):
        # Generate a unique job ID
        job_id = str(uuid.uuid4())
        csv_file_path = f'{job_id}_claims_report.csv'
        
        # Write the report data to CSV file
        jobs[job_id] = 'in progress'
        try:
            with open(csv_file_path, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Patient Name', 'Diagnosis Code', 'Procedure Code', 'Status', 'Total Claim Amount'])
                writer.writerows(data)
            # Update job status to completed
            jobs[job_id] = 'completed'
        except Exception as e:
            # Update job status to failed in case of error
            jobs[job_id] = 'failed'
        return job_id

    # Endpoint to generate the report
    @app.route("/claims/report", methods=['POST'])
    @jwt_required()
    def genreate_report():
        status = request.json.get('status')
        # Validate the status input
        if not _validator.check_string_type(status) or _validator.convert_type(status) == "Unknown value":
            return jsonify({"error": True, "message": "status isn't valid type or valid value"}), 500
         
        # Retrieve claim data based on status
        result = _db_query.get_claim_data_report(_validator.convert_type(status))
        # Create the CSV report using Celery
        task_id = Report.create_csv_report(result[1])
        return jsonify({"success": result[0], "task_id": task_id}), 200 if result[0] else 500

class ClaimRoutes:
    # Endpoint to delete a claim by ID
    @app.route("/claims/<int:claim_id>", methods=['DELETE'])
    @jwt_required()
    def delete_claim(claim_id):
        # Validate claim_id input
        if not _validator.check_int_type(claim_id):
            return jsonify({"error": True, "message": "claim_id isn't a valid int type"})
        
        # Delete claim by ID and return result
        result = _db_query.delete_claim_by_id(claim_id)
        return jsonify({"success": result[0], "message": result[1]}), 200 if result[0] else 500

    # Endpoint to update claim status by ID
    @app.route("/claims/<int:claim_id>", methods=['PUT'])
    @jwt_required()
    def update_claim_status(claim_id):
        status = request.json.get("status")
        # Validate claim_id and status input
        if not _validator.check_string_type(status) or not _validator.check_int_type(claim_id):
            return jsonify({"error": True, "message": "claim_id or status are not valid type or valid value"}), 500
        
        # Validate status value
        if _validator.convert_type(status) == "Unknown value":
            return jsonify({"error": True, "message": "status value isn't valid"}), 500
        
        # Update claim status and return result
        result = _db_query.update_claim_status(_validator.convert_type(status), claim_id)
        return jsonify({"success": result[0], "message": result[1]}), 200 if result[0] else 500

    # Endpoint to get a claim by ID
    @app.route("/claims/<int:claim_id>", methods=['GET'])
    @jwt_required()
    def get_claim_by_id(claim_id):
        # Validate claim_id input
        if not _validator.check_int_type(claim_id):
            return jsonify({"error": True, "message": "claim_id isn't a valid int type"})
        
        # Retrieve claim by ID and return result
        result = _db_query.retrieve_claim_by_id(claim_id)
        return jsonify({"success": result[0], "message": result[1]}), 200 if result[0] else 500

    # Endpoint to get a list of claims with optional filters
    @app.route("/claims", methods=['GET'])
    @jwt_required()
    def get_claims():
        # Get optional filter parameters
        status = request.args.get('status')
        diagnosis_code = request.args.get('diagnosis_code')
        procedure_code = request.args.get('procedure_code')
        page = request.args.get('page')
        per_page = request.args.get('per_page')

        # Check if all required parameters are provided
        if not (status and diagnosis_code and procedure_code and page and per_page):
            return jsonify({"error": True, "message": "All parameters must be provided"}), 400
        # Validate the input values
        try:
            page = int(page)
            per_page = int(per_page)
        except ValueError:
            return jsonify({"error": True, "message": "page and per_page must be integers"}), 500

        if not _validator.check_string_type(status):
            return jsonify({"error": True, "message": "status must be a string"}), 400
        if not _validator.check_int_type(diagnosis_code, procedure_code, page, per_page):
            return jsonify({"error": True, "message": "diagnosis_code, procedure_code, page, and per_page must be integers"}), 400
        if _validator.convert_type(status) == "Unknown value":
            return jsonify({"error": True, "message": "status value isn't valid"}), 400
        # Retrieve claim data with the specified filters
        result = _db_query.get_claim_data(per_page, page, diagnosis_code, procedure_code, _validator.convert_type(status))
        return jsonify({"success": result[0], "message": result[1]}), 200 if result[0] else 500

    # Endpoint to add a new claim
    @app.route("/claims", methods=['POST'])
    @jwt_required()
    def add_claim():
        # Get input values
        patient_name = request.json.get('patient_name')
        diagnosis_code = request.json.get('diagnosis_code')
        procedure_code = request.json.get('procedure_code')
        claim_amount = request.json.get('claim_amount')
        if not (patient_name and diagnosis_code and procedure_code and claim_amount):
            return jsonify({"error": True, "message": "All data must be provided"}), 400
        # Validate the input values
        if _validator.check_null_values(patient_name, diagnosis_code, procedure_code, claim_amount):
            return jsonify({"error": "Missing values"}), 400
        if not _validator.check_int_type(diagnosis_code, procedure_code, claim_amount):
            return jsonify({"error": "diagnosis_code and procedure_code must be integers, claim_amount must be a number"}), 400
        
        # Add new claim and return result
        result = _db_query.add_claim(patient_name, diagnosis_code, procedure_code, claim_amount)
        return jsonify({"success": result[0], "message": result[1]}), 200 if result[0] else 500

class AuthRoutes:
    # Endpoint for user login
    @app.route("/auth/login", methods=['POST'])
    def login():
        # Get login credentials
        email = request.json.get('email')
        password = request.json.get('password')
        
        # Validate the input values
        if not _validator.check_null_values(email, password):
            result = _db_query.login(email, password)
            if not result:
                return jsonify(message="Invalid credentials"), 401
            else:
                # Create access token if credentials are valid
                return jsonify({"access_token": create_access_token(identity=email)}), 200 # return auth token by email identity.
        else:
            return jsonify({"error": "Missing values"}), 400
    # Endpoint for user signup
    @app.route("/auth/signup", methods=['POST'])
    def signup():
        name = request.json.get('name')
        email = request.json.get('email')
        password = request.json.get('password')
        # Validate the input values
        if not _validator.check_null_values(name, email, password): # check if theres any none values .
            if "@" not in email or "." not in email:
                return jsonify({"success": False, "error": "Invalid email address"}), 400
            else:
                result = _db_query.add_user(name, email, password)
                return jsonify({"success": result[0], "message": result[1]}), 200
        else:
            return jsonify({"error": True, "message": "Missing field"}), 400

# Main function to run the Flask application
def __main__():
    app.run(debug=True,port=5000)

if __name__ == "__main__":
    __main__()
