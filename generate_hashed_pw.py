import pickle
from pathlib import Path
import streamlit_authenticator as stauth

# Usernames and passwords
names = ["snehit", "vaddi"]
usernames = ["snehit", "vaddi"]
passwords = ["123456789", "123456789"]  # Replace with actual passwords

# Hash passwords
hashed_passwords = stauth.Hasher(passwords).generate()

# Save hashed passwords to a file
file_path = Path(__file__).parent / "hashed_pw.pkl"
with file_path.open("wb") as file:
    pickle.dump(hashed_passwords, file)
