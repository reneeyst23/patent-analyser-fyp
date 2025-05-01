# patent-analyser-fyp

To get started with the collaboration, please read the following steps:

Install the required dependencies:
    `pip install -r requirements.txt`

Create .streamlit folder in the root of the repository and add a `secrets.toml` file:
    `mkdir .streamlit`
    `touch .streamlit/secrets.toml`
    `touch .streamlit/config.toml`

Fill in the `secrets.toml` file with the following information:
    `environment = "development"`

Fill in the `config.toml` file with the following information:
    `[server]`
    `runOnSave = true`

File is default gitignored for security concerns, do not push them to git.

## Run QdrantClient

`docker run -p 6333:6333 -v qdrant_data:/qdrant/storage qdrant/qdrant`

## To run the app frontend

`streamlit run app.py`

