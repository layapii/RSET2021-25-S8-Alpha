import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from sklearn.preprocessing import StandardScaler
import pdfplumber
from docx import Document

# Directory containing dataset files
data_dir = r"C:\Users\basil\.cache\kagglehub\datasets\rbdbhardwaj123\rentalagreementsdocs\versions\1"


def list_files():
    """List all files in the dataset directory."""
    print("Files in dataset:")
    for dirname, _, filenames in os.walk(data_dir):
        for filename in filenames:
            print(os.path.join(dirname, filename))

def extract_text_from_docx(file_path):
    """Extract text from a DOCX file."""
    doc = Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])

def extract_text_from_pdf(file_path):
    """Extract text from a PDF file."""
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

def load_rental_agreements():
    """Load and extract text from rental agreements."""
    agreements = {}
    for file in os.listdir(data_dir):
        file_path = os.path.join(data_dir, file)
        if file.endswith(".docx"):
            agreements[file] = extract_text_from_docx(file_path)
        elif file.endswith(".pdf"):
            agreements[file] = extract_text_from_pdf(file_path)
    return agreements

def plot_data_distribution(df, nGraphShown=10, nGraphPerRow=3):
    """Plot distribution graphs of dataset columns."""
    nunique = df.nunique()
    df = df[[col for col in df if 1 < nunique[col] < 50]]
    nRow, nCol = df.shape
    columnNames = list(df)
    nGraphRow = int((nCol + nGraphPerRow - 1) / nGraphPerRow)
    plt.figure(figsize=(6 * nGraphPerRow, 8 * nGraphRow))
    
    for i in range(min(nCol, nGraphShown)):
        plt.subplot(nGraphRow, nGraphPerRow, i + 1)
        columnDf = df.iloc[:, i]
        if not np.issubdtype(type(columnDf.iloc[0]), np.number):
            columnDf.value_counts().plot.bar()
        else:
            columnDf.hist()
        plt.ylabel("Counts")
        plt.xticks(rotation=90)
        plt.title(f"{columnNames[i]}")
    plt.tight_layout()
    plt.show()

def plot_correlation_matrix(df, graphWidth=10):
    """Plot correlation matrix."""
    df = df.dropna(axis=1, how='all')
    df = df[[col for col in df if df[col].nunique() > 1]]
    if df.shape[1] < 2:
        print("Not enough numerical data for correlation analysis.")
        return
    corr = df.corr()
    plt.figure(figsize=(graphWidth, graphWidth))
    plt.matshow(corr, fignum=1)
    plt.xticks(range(len(corr.columns)), corr.columns, rotation=90)
    plt.yticks(range(len(corr.columns)), corr.columns)
    plt.colorbar()
    plt.title("Correlation Matrix", fontsize=15)
    plt.show()

def main():
    list_files()
    agreements = load_rental_agreements()
    print("\nSample Agreement Text:\n", list(agreements.values())[0][:1000])
    
    # Dummy DataFrame for Visualization Example
    data = {
        "Rent Amount": np.random.randint(10000, 50000, 100),
        "Lease Duration (Months)": np.random.randint(6, 36, 100),
        "Security Deposit": np.random.randint(5000, 30000, 100)
    }
    df = pd.DataFrame(data)
    plot_data_distribution(df)
    plot_correlation_matrix(df)

if __name__ == "__main__":
    main()