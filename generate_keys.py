import pickle
from pathlib import Path
import streamlit_authenticator as stauth

names = ["snehit", "vaddi", "test"]
usernames = ["snehit", "vaddi", "test"]
passwords = ["snehit", "snehit", "test"]

# Use generate_hashed_passwords() instead of generate()
hashed_passwords = stauth.Hasher(passwords).generate_hashed_passwords()

file_path = Path(__file__).parent / "hashed_pw.pkl"
with file_path.open("wb") as file:
    pickle.dump(hashed_passwords, file)

print("File 'hashed_pw.pkl' generated successfully!")
