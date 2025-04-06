import os
import sys
import subprocess
import torch
from flask import Flask, request, jsonify, send_from_directory, render_template

app = Flask(__name__, static_folder="static", template_folder="templates")

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "ProteinMPNN/output/seqs"
PROTEINMPNN_PATH = "ProteinMPNN/protein_mpnn_run.py"  # Adjust path as needed

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/')
def home():
    """ Serve the index.html page """
    return render_template("index.html")

@app.route('/upload', methods=['POST'])
def upload_file():
    """ Handle PDB file upload and run ProteinMPNN """
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    pdb_file = request.files['file']
    
    if pdb_file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    file_path = os.path.join(UPLOAD_FOLDER, pdb_file.filename)
    pdb_file.save(file_path)

    # Define command to run ProteinMPNN
#     command = [
#         "python", PROTEINMPNN_PATH,
# #        "--pdb_path", file_path,
#         "--pdb_path", "ProteinMPNN/chain_C_only.pdb",
#         "--out_folder", OUTPUT_FOLDER,
#         "--fixed_positions_jsonl", "ProteinMPNN/fixed_positions.jsonl",
#         "--chain_id_jsonl", "ProteinMPNN/chain_ids.jsonl",
#         "--sampling_temp", "0.2"
#     ]
    

    # Run ProteinMPNN
    #try:
    print("hi")
    print(file_path)
    #subprocess.run(command, check=True, text=True, capture_output=True)
    PYTHON_PATH = sys.executable  # Uses the same Python as your terminal
    PROTEINMPNN_PATH = "ProteinMPNN/protein_mpnn_run.py"

    subprocess.run([PYTHON_PATH, PROTEINMPNN_PATH], check=True)

    #subprocess.run(["python", PROTEINMPNN_PATH], check=True)
    print("hello")
    #except subprocess.CalledProcessError as e:

    #    return jsonify({"error": f"ProteinMPNN failed: {e.stderr}"}), 500

    # Extract the generated FASTA sequence
    fasta_file = os.path.join(OUTPUT_FOLDER, "chain_C_only.fa")  # Adjust filename as per ProteinMPNN output
    if not os.path.exists(fasta_file):
        return jsonify({"error": "FASTA file not generated"}), 500

    with open(fasta_file, "r") as f:
        fasta_content = f.read()

    return jsonify({"sequence": fasta_content})

if __name__ == '__main__':
    app.run(debug=True)



from flask import Flask, render_template, request, jsonify
import numpy as np
from Bio import PDB

app = Flask(__name__)

def extract_plddt(pdb_file):
    """Extracts per-residue pLDDT scores."""
    parser = PDB.PDBParser(QUIET=True)
    structure = parser.get_structure("protein", pdb_file)
    plddt_scores = [atom.get_bfactor() for model in structure for chain in model for residue in chain for atom in residue if atom.get_name() == "CA"]
    return np.array(plddt_scores)

@app.route("/evaluate", methods=["POST"])
def evaluate():
    print("Received request")
    print("Request headers:", request.headers)
    print("Request content type:", request.content_type)
    print("Request files:", request.files)
    print("Request JSON:", request.json)

    if "pdb_file" not in request.files:
        print("❌ No file uploaded!")
        return jsonify({"error": "No file uploaded"}), 400

    pdb_file = request.files["pdb_file"]
    if pdb_file.filename == "":
        print("❌ No file selected!")
        return jsonify({"error": "No selected file"}), 400

    print("✅ File received:", pdb_file.filename)

    # Save file temporarily
    temp_path = f"/tmp/{pdb_file.filename}"
    pdb_file.save(temp_path)
    print("📁 File saved at:", temp_path)

    try:
        plddt_scores = extract_plddt(temp_path)
        avg_plddt = np.mean(plddt_scores)
    except Exception as e:
        print("❌ Error in processing:", str(e))
        return jsonify({"error": f"PDB parsing failed: {str(e)}"}), 500
    finally:
        os.remove(temp_path)  # Clean up file

    accuracy = np.random.uniform(70, 95)
    confidence_level = "High" if avg_plddt > 80 else "Medium" if avg_plddt > 60 else "Low"

    return jsonify({
        "average_plddt": round(avg_plddt, 2),
       # "accuracy": round(accuracy, 2),
        "confidence": confidence_level
    })
