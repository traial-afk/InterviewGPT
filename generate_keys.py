import pickle
from pathlib import Path
import streamlit_authenticator as stauth

names = ["snehit", "vaddi", "test"]
usernames = ["snehit", "vaddi", "Test"]
passwords = ["snehit", "snehit", "test"]

# Hash the passwords
hashed_passwords = stauth.Hasher(passwords).hashed_passwords

# Save the hashed passwords to a file
file_path = Path(__file__).parent / "hashed_pw.pkl"
with file_path.open("wb") as file:
    pickle.dump(hashed_passwords, file)

print("Hashed passwords saved successfully!")
