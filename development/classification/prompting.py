from together import Together
import pandas as pd

api_key = "04754ecf704467fd40c34bb371850b0b5100c9bac653b0c277f2281ef2ee0737"

# Load the JSON data into a DataFrame
df = pd.read_json("test_data.json")
client = Together(api_key=api_key)

def promptBasic(input_data, command):
    prompt_message = f"give me triz principle for the TRIZ: {input_data}"
    response = client.chat.completions.create(
        model="deepseek-ai/DeepSeek-V3",
        messages=[{"role": "user", "content": prompt_message}],
    )

    # Return the response content
    return response.choices[0].message.content

# Example usage
#command = "Classify based on TRIZ 40 principles"
#output = promptBasic(df.iloc[0]['claims'], command)
#print(output)