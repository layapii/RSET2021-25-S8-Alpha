import os
import torch
from transformers import BartTokenizer, BartForConditionalGeneration, Trainer, TrainingArguments
from datasets import Dataset
from torch.optim import AdamW
import evaluate
from bert_score import score

# Check if GPU is available
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Training on: {device}")

# Initialize tokenizer and model for BART
model_name = "facebook/bart-large"
tokenizer = BartTokenizer.from_pretrained(model_name)
model = BartForConditionalGeneration.from_pretrained(model_name)
model.to(device)  # Move model to GPU

# Function to load data from text files
def load_data(judgement_folder, summary_folder, max_files=6000):
    data = []
    
    # List files in judgement and summary folders
    judgement_files = sorted(os.listdir(judgement_folder))[:max_files]
    summary_files = sorted(os.listdir(summary_folder))[:max_files]

    # Loop through first max_files files
    for j_file, s_file in zip(judgement_files, summary_files):
        with open(os.path.join(judgement_folder, j_file), 'r') as j_f:
            judgement_text = j_f.read()
        with open(os.path.join(summary_folder, s_file), 'r') as s_f:
            summary_text = s_f.read()

        # Append data to list
        data.append({"judgement": judgement_text, "summary": summary_text})
    
    return data

# Load training and test data
test_data = load_data(r"C:\Users\basil\Downloads\Telegram Desktop\archive (1)\dataset\IN-Abs\test-data\judgement", 
                      r"C:\Users\basil\Downloads\Telegram Desktop\archive (1)\dataset\IN-Abs\test-data\summary", 
                      max_files=100)

train_data = load_data("C:\\Users\\basil\\Downloads\\Telegram Desktop\\archive (1)\\dataset\\IN-Abs\\train-data\\judgement", 
                       "C:\\Users\\basil\\Downloads\\Telegram Desktop\\archive (1)\\dataset\\IN-Abs\\train-data\\summary")

# Convert to Hugging Face Dataset
train_dataset = Dataset.from_list(train_data)
test_dataset = Dataset.from_list(test_data)

# Tokenization function
def preprocess_function(examples):
    model_inputs = tokenizer(examples["judgement"], max_length=1024, truncation=True, padding="max_length")
    with tokenizer.as_target_tokenizer():
        labels = tokenizer(examples["summary"], max_length=256, truncation=True, padding="max_length")
    
    model_inputs["labels"] = labels["input_ids"]
    return model_inputs

# Tokenize datasets
tokenized_train_dataset = train_dataset.map(preprocess_function, batched=True)
tokenized_test_dataset = test_dataset.map(preprocess_function, batched=True)

# Define Training Arguments
training_args = TrainingArguments(
    output_dir='./results',
    evaluation_strategy="epoch",   # Evaluate every epoch
    learning_rate=2e-5,
    per_device_train_batch_size=1,  # Adjust batch size based on your GPU memory
    per_device_eval_batch_size=1,   # Adjust batch size based on your GPU memory
    num_train_epochs=3,
    weight_decay=0.01,
    logging_dir='./logs',
    save_total_limit=None,
    save_steps=0,
    report_to="none",  # Disable reports to WandB, etc.
    fp16=False,  # Enable mixed precision for faster training on GPU
)

# Initialize optimizer manually
optimizer = AdamW(model.parameters(), lr=2e-5)

# Initialize Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_train_dataset,
    eval_dataset=tokenized_test_dataset,
    optimizers=(optimizer, None),  # Set the optimizer
)

# Start Training
trainer.train()

# Save the fine-tuned model
model.save_pretrained('./fine_tuned_bart_model')
tokenizer.save_pretrained('./fine_tuned_bart_model')

print("Training complete and model saved.")

# Sample evaluation (you can add your evaluation logic here)
predictions = ["This is a sample predicted summary."]
references = ["This is the reference summary."]

# Compute BERTScore
P, R, F1 = score(predictions, references, lang='en')
print(f"BERTScore: Precision={P.mean().item()}, Recall={R.mean().item()}, F1={F1.mean().item()}")
