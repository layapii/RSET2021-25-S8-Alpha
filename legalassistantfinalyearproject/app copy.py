import io
from flask import Flask, render_template, render_template_string, request, send_file
import requests
import gen2
import spacy
from fpdf import FPDF
from flask import Flask, request, session, redirect, url_for, render_template, jsonify
from firebase_admin import auth, initialize_app, credentials

# Initialize Firebase Admin SDK
cred = credentials.Certificate('templates/firebaseconfig.json')
initialize_app(cred)

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure key

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.json.get('email')
        
        # Verify user exists in Firebase
        try:
            user = auth.get_user_by_email(email)
            session['username'] = email
            return jsonify({'message': 'Login successful'})
        except Exception as e:
            print("Error logging in:", e)
            return jsonify({'message': 'Login failed'}), 401
    else:
        # Render login page if not logged in
        if not session.get('username'):
            return render_template('authentication.html')
        return redirect(url_for('home'))

# Logout Route
@app.route('/logout')
def logout():
    session.clear()
    return render_template('authenti.html')  # Redirect to login page
@app.route('/signup', methods=['POST'])
def signup():
    if request.method == 'POST':
        data = request.json
        email = data.get('email')
        password = data.get('password')
        username = data.get('username')
        address = data.get('address')
        pincode = data.get('pincode')
        
        try:
            # Create user in Firebase
            user = auth.create_user(
                email=email,
                password=password,
                display_name=username
            )
            # You can store additional user data (address, pincode) in a database here if needed
            
            return jsonify({'message': 'User created successfully'}), 200
        except Exception as e:
            print("Error creating user:", e)
            return jsonify({'message': 'Failed to create user'}), 400
@app.route('/ask_ollama', methods=['POST'])
def ask_ollama():
    try:
        data = request.get_json()
        if not data or 'prompt' not in data:
            app.logger.error("No prompt provided in request")
            return jsonify({"error": "No prompt provided"}), 400

        user_query = data['prompt']
        app.logger.info(f"Received prompt: {user_query}")

        # Prepare the prompt
        legal_prompt = f"""You are an AI Legal Assistant. Please provide professional legal information and guidance for the following query. 
        Remember to include a disclaimer that this is general information and not legal advice.
        
        User Query: {user_query}

        Please provide a detailed and helpful response."""

        # Make request to Ollama
        ollama_url = "http://localhost:11434/api/generate"
        ollama_payload = {
            "model": "llama3.1",  # Updated to use llama3.1
            "prompt": legal_prompt
        }

        app.logger.info(f"Sending request to Ollama at {ollama_url}")
        app.logger.debug(f"Payload: {ollama_payload}")
        
        response = requests.post(
            ollama_url,
            json=ollama_payload,
            timeout=60,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 404:
            app.logger.error("Ollama API endpoint not found. Make sure Ollama is running and the URL is correct.")
            return jsonify({"error": "Ollama API endpoint not found"}), 500
            
        response.raise_for_status()
        
        response_data = response.json()
        app.logger.debug(f"Ollama response: {response_data}")
        
        if 'response' not in response_data:
            app.logger.error("No response field in Ollama response")
            return jsonify({"error": "Invalid response from Ollama"}), 500

        app.logger.info("Successfully got response from Ollama")
        return jsonify({"response": response_data['response']})

    except requests.exceptions.ConnectionError:
        app.logger.error("Could not connect to Ollama service")
        return jsonify({"error": "Could not connect to Ollama service. Make sure Ollama is running."}), 500
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Request to Ollama failed: {str(e)}")
        return jsonify({"error": f"Request to Ollama failed: {str(e)}"}), 500
    except Exception as e:
        app.logger.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

@app.route('/check_ollama', methods=['GET'])
def check_ollama():
    try:
        response = requests.get('http://localhost:11434/api/tags')
        if response.status_code == 200:
            return jsonify({"status": "Ollama is running"})
        else:
            return jsonify({"status": "Ollama is not responding correctly"}), 500
    except requests.exceptions.RequestException:
        return jsonify({"status": "Cannot connect to Ollama"}), 500

# Home Route
@app.route('/index')
def home():
    if 'username' not in session:
        return redirect(url_for('authenti.html'))
    return render_template('main.htmnl')  # Replace with your homepage template
@app.route('/')
def index7():
    return render_template('authenti.html')
html_template = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>PDF Generator</title>
</head>
<body>
    <h2>Enter content for PDF</h2>
    <form action="/generate_pdf" method="post">
        <label for="title">Title:</label><br>
        <input type="text" id="title" name="title"><br><br>
        
        <label for="content">Content:</label><br>
        <textarea id="content" name="content" rows="4" cols="50"></textarea><br><br>
        
        <input type="submit" value="Generate PDF">
    </form>
</body>
</html>
"""
@app.route('/main.html')
def main():
    return render_template('main.html')

@app.route('/c')
def index():
    return render_template_string(html_template)


@app.route('/generate_pdf', methods=['POST'])
def generate_pdf1(title,content):
    # Get user input from form
    title = request.form.get("title", "PDF Generation Example")
    content = request.form.get("content", "This is a sample content for PDF.")
    pdf_buffer=gen2.generate_pdf(title,content)

    # Send the PDF as a response
    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name="generated_pdf_example.pdf",
        mimetype="application/pdf"
    )

@app.route('/case', methods=['POST', 'GET'])
def case_input():
    if request.method == 'POST':
        case_scenario = request.form.get('case_scenario')
        # Extract the information from the input case scenario
        lease_info = extract_lease_info(case_scenario)
        print(lease_info)
        pdf_output = generate_pdf(lease_info)
        # Send the generated PDF as a downloadable file
        return send_file(pdf_output, download_name='lease_agreement.pdf', as_attachment=True)

    return render_template('caseinput.html')

# Route for case input page
#@app.route('/case', methods=['GET', 'POST'])
#def case_input():
 #   if request.method == 'POST':
  #      case_text = request.form['case_scenario']
   ##     # Process the case text here
     #   return f"Case scenario received: {case_text}"
    #return render_template('caseinput.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)
