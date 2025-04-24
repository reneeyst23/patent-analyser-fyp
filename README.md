# patent-analyser-fyp

To get started with the collaboration, please read the following steps:
1. Open your terminal and install pipx if you do not have it

    ✅ Method 1: (Recommended) Install via pipx
        If you have pipx: 

        pipx install uv

        Don't have pipx? Install it first:

        python -m pip install --user pipx
        python -m pipx ensurepath

        Then restart your terminal and run:

        pipx install uv

    ✅ Method 2: Install via pipx (macOS)

        python3 -m pip install --user pipx
        python3 -m pipx ensurepath

        Then restart your terminal and run:

        pipx --version

2. Install uv using pipx

    pipx install uv

3. Connect to the collaboration:

    source setup.sh

or 

(Windows)
1. Install all requirements

    pip install -r requirements.txt

2. Building frontend

cd frontend
npm i
npm run dev

To run the app:

streamlit run app.py

