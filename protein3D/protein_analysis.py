import os
import sys
import subprocess
import numpy as np
import torch
from flask import Flask, request, jsonify, send_from_directory, render_template
from Bio import PDB

app = Flask(__name__, static_folder="static", template_folder="templates")

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "ProteinMPNN/output/seqs"
PROTEINMPNN_PATH = "ProteinMPNN/protein_mpnn_run.py"  # Adjust path as needed

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def extract_plddt(pdb_file):
    """Extracts per-residue pLDDT scores."""
    parser = PDB.PDBParser(QUIET=True)
    structure = parser.get_structure("protein", pdb_file)
    plddt_scores = [atom.get_bfactor() for model in structure for chain in model for residue in chain for atom in residue if atom.get_name() == "CA"]
    return np.array(plddt_scores)

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

    # Run ProteinMPNN
    PYTHON_PATH = sys.executable  # Uses the same Python as your terminal
    subprocess.run([PYTHON_PATH, PROTEINMPNN_PATH], check=True)
    
    # Extract the generated FASTA sequence
    fasta_file = os.path.join(OUTPUT_FOLDER, "chain_C_only.fa")  
    if not os.path.exists(fasta_file):
        return jsonify({"error": "FASTA file not generated"}), 500

    with open(fasta_file, "r") as f:
        fasta_content = f.read()

    return jsonify({"sequence": fasta_content})

@app.route("/evaluate", methods=["POST"])
def evaluate():
    """API to return protein statistics."""
    data = request.json
    predicted_pdb = data.get("predicted_pdb")

    if not predicted_pdb or not os.path.exists(predicted_pdb):
        return jsonify({"error": "Invalid or missing PDB file"}), 400

    # Extract pLDDT scores
    plddt_scores = extract_plddt(predicted_pdb)
    avg_plddt = np.mean(plddt_scores)

    # Determine confidence level
    confidence_level = "High" if avg_plddt > 80 else "Medium" if avg_plddt > 60 else "Low"

    return jsonify({
        "average_plddt": round(avg_plddt, 2),
        "confidence": confidence_level
    })

if __name__ == '__main__':
    app.run(debug=True)
