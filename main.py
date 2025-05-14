import polars as pl
from classification.LLM import Openai
from classification.prompt_template import Prompt
import ast

# Load existing results
df = pl.read_parquet("results_with_topic.parquet")
print(df.head())