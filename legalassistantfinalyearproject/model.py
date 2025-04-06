import os
import json
import time
import random
from faker import Faker
from num2words import num2words

# Initialize Faker for random data generation
fake = Faker()

def generate_lease_sample():
    """Generates a lease agreement text and structured JSON output."""
    
    # Lease Agreement Details
    effective_date = fake.date_this_decade().strftime("%B %d, %Y")
    lessor_name = fake.name()
    lessee_name = fake.name()
    property_address = fake.address().replace("\n", ", ")
    lease_term = f"{random.randint(6, 36)} months"
    monthly_rent = f"${random.randint(800, 5000)}"
    
    # Generate Lease Agreement Text
    lease_text = (
        f"This lease agreement is made on {effective_date}, between {lessor_name} (Lessor) "
        f"and {lessee_name} (Lessee) for the property at {property_address}. "
        f"The lease term is {lease_term}, with a monthly rent of {monthly_rent}."
    )
    
    # JSON Output
    lease_json = {
        "effective_date": effective_date,
        "lessor": lessor_name,
        "lessee": lessee_name,
        "property_address": property_address,
        "lease_term": lease_term,
        "monthly_rent": monthly_rent
    }
    
    return {"text": lease_text, "json_output": lease_json}

# Generate dataset
num_samples = 50
dataset = [generate_lease_sample() for _ in range(num_samples)]

# Save dataset
with open("lease_dataset.json", "w") as f:
    json.dump(dataset, f, indent=4)

print("✅ Lease dataset saved as lease_dataset.json")
