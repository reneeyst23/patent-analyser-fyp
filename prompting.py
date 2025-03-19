import os
from together import Together
import pandas as pd

api_key = "04754ecf704467fd40c34bb371850b0b5100c9bac653b0c277f2281ef2ee0737"

# Load the JSON data into a DataFrame
df = pd.read_json("test_data.json")
client = Together(api_key=api_key)

def promptBasic(input_data, command):
    prompt_message = f"tidy up writing of the following file: {input_data}"
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

Example= """
Principle 1:Segmentation
    definition:  Segmentation entails dividing a system or object into independent parts and combine them in a more suitable way
    keyword:Divide [divide, apart, partition, disunit, disamble, classify, separate]

Principe 2: Taking Out
    definition: For improving the end of life, eliminate the components (i.e., hazardous materials) that reduce the reuse, the recyclability or the disposal of the product by removing them from the product with less energy.
    keyword: remove [expel, oust, eject, evacuate, dislodge, snatch]

Principle 3: Local Quality
    definition: reducing mental inertia when considering space and materials too homogeneous and continuous. 
                 We can say that, from the Ecodesign point of view, this principle tends to optimize the processes and, therefore, to reduce the energy and mass impacts.
                With the same principle we tend to conceive multi-function objects for exploiting synergies among functions
    keyword: optimize, material, [add, increment, pile, reduce, incremental, improve, adapt, modify, eliminate]

Principle 5: Merging
    definition:  offering the synergies of several machines that share the same energy and control sources.
    keyword: merge [synergy, combine, union, together, combine, harmony]

Principle 6:Universality
    definition: Make a part or object perform multiple functions; eliminate the need for other parts.
    keyword: universal[multifunction, diverse, multipurpose, all-around, versatile, adaptable, accomodate]

Principle 13: the other way around (context of results needed)
    definition:  simply reversing the normal procedure or process. According to it, invert the action(s) used to solve the problem
    , invert the action(s) used to solve the problem (e.g., instead of cooling an object, heat it); make the movable parts of the entity fixed, and the fixed parts movable; turn the entity ‘upside down’;
    nest objects inside others; and exploit other dimensions.
    keyword: reversal[inverse, contrary, improve,reverse, optimize]

Principle 15: Dynamics
    definition: key principle to make the system work only when needed (Operative Time) and always in an optimal way.
                the characteristics ofan object, external environment, or process to change to be optimal or to find an optimal operating condition. 
    keyword: optimize, system [efficient, adapt, adjust, modify, acclimatize, conform, comply, distribute]

Principle 22: Blessing in Disguise
    definition: Use harmful factors (particularly, harmful effects of the environment or surroundings) to achieve a positive effect.
    keyword: repurpose [purify, recycle, disinfect, reuse, eliminate, recycle]

Principle 24: Intermedeary
    definition:

Principle 25: self service

Principle 31: Porous Material
        definition: increase the performances by reducing the mass, the goal is acting on the topology or on the distribution of the masses within the volume of the object, arranging the
                    mass only where it is needed and eliminating the portions which have no functional characteristics.
        keyword: lighten [repurpose, eliminate, distribute, reduce, weight, eliminate]

Principle 35: Parameter Change
        definition: entails changing an object’s physical state to a gas, liquid, or solid; changing pressure or other physical parameters; changing the concentration or consistency;
        changing the degree of flexibility; or changing the temperature. 
        keyword: changing [transform, alter, convert, modify, evolve]


Principle 36: Phase Transition
        definition: Use phenomena occurring during phase transitions (e.g. volume changes, loss or absorption of heat, etc.).
        keyword: transition[volume, absorption]
"""
command = "reformat and complete these statements"
output = promptBasic(Example, command)
print(output)
