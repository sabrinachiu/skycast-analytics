---
description: How to deploy the SkyCast Analytics dashboard to Streamlit Community Cloud
---

# Deploying to Streamlit Community Cloud

Follow these steps to get your dashboard live:

1. **Push to GitHub**:
   - Create a new repository on [GitHub](https://github.com/new).
   - Run the following commands in your terminal:
     ```bash
     git remote add origin <your-github-repo-url>
     git branch -M main
     git push -u origin main
     ```

2. **Connect to Streamlit**:
   - Go to [share.streamlit.io](https://share.streamlit.io).
   - Click **"New app"**.
   - Select your repository (`resonant-shuttle`), the branch (`main`), and the main file path (`app.py`).

3. **Deploy**:
   - Click **"Deploy!"**. Your app will be live in a few minutes.

// turbo-all
```powershell
git add .
git commit -m "Initial commit: SkyCast Analytics Dashboard"
```
