import requests

def google_transliterate(name, lang="ml"):
    url = f"https://www.google.com/inputtools/request?text={name}&itc={lang}-t-i0-und&num=1"
    response = requests.get(url)
    if response.status_code == 200:
        try:
            data = response.json()
            return data[1][0][1][0]  # Extract transliterated result
        except Exception:
            return name  # Return original if there's an error
    return name

# Example names
names = ["Basil", "Elodo", "Michael", "Thomas","Tripti"]
transliterated_names = {name: google_transliterate(name) for name in names}

print(transliterated_names)
