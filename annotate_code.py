from openai import OpenAI
# Set your OpenAI API key
import os
client = OpenAI(api_key='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')

def annotate_patent_claims(claims_text):
    prompt = (
        "You are an expert patent analyst with deep knowledge of the 40 TRIZ principles. "
        "For the following patent claims, classify each claim based on the applicable TRIZ principles. "
        "Identify which TRIZ principle(s) are most relevant for each claim and provide a brief explanation for your classification.\n\n"
        f"{claims_text}\n\n"
        "Annotation:"
    )

    response = client.chat.completions.create(
        model="gpt-4",  # or "gpt-4-turbo" if available to you
        messages=[
            {"role": "system", "content": "You are a TRIZ expert specializing in eco-innovation and patent analysis."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content


if __name__ == "__main__":
    sample_claims = """
Claims 
1. A fire extinguishing liquid foam concentrate to be mixed with a proportioned quantity of water, and then mixed with air within an aerating/aspirating foam forming nozzle to generate finished fire extinguishing foam material, said fire extinguishing liquid foam concentrate comprising: a dispersing agent in the form of a quantity of water, for dispersing metal ions dissolved in said quantity of water; a fire inhibiting agent in the form of at least one alkali metal salt of a nonpolymeric saturated carboxylic acid, for providing metal ions dispersed in the water when the at least one alkali metal salt is dissolved in said quantity of water; a foaming agent including hydrolyzed protein isolate (HPI) material dissolved in said quantity of water; and a dispersing agent in the form of an organic compound containing three carboxylic acid groups, or salt/ester derivatives thereof, for dispersing the metal ions in said quantity of water, and lowering the surface tension of the liquid solution formed by said fire inhibiting agent, said foaming agent and said dispersing agent dissolved in said quantity of water, to enable the forming of a fire extinguishing foam material when said liquid solution is mixed with air within an aerating/aspirating foam forming nozzle.
2. The fire extinguishing liquid foam concentrate according to claim 1, wherein the alkali metal salt is a sodium or potassium salt.
3. The fire extinguishing liquid foam concentrate according to claim 1, wherein the alkali metal salt is tripotassium citrate.
4. The fire extinguishing liquid foam concentrate according to claim 1, wherein said coalescing agent is triethyl citrate, an ester of citric acid.
5. A method of fighting a wildfire comprising the steps of applying the fire extinguishing foam material produced in claim 1 to the surfaces to be proactively protected from a wildfire.
6. A method of fighting a fire comprising the steps of applying the fire extinguishing foam material produced in claim 1 to surfaces ignited or consumed by fire to be extinguished by said fire extinguishing foam material.
7. An aqueous-based fire extinguishing liquid concentrate for mixing with a prespecified quantity of water to produce a fire extinguishing liquid solution that produces good immediate extinguishing effects when applied to extinguish a burning or smoldering fire, and very good long-term fire inhibiting effects when being proactively applied to protect combustible surfaces against the threat of fire, said aqueous-based fire extinguishing liquid concentrate comprises: a dispersing agent realized in the form of a quantity of water, for dispersing metal ions dissolved in water; a fire inhibiting agent in the form of at least one alkali metal salt of a nonpolymeric saturated carboxylic acid, for providing metal ions dispersed in the water when the at least one alkali metal salt is dissolved in said quantity of water; and a dispersing agent in the form of an organic compound containing three carboxylic acid groups or salt/ester derivatives thereof, such as triethyl citrate, an ester of citric acid, for dispersing the metal ions in said quantity of water, and lowering the surface tension of the liquid solution formed by said fire inhibiting agent, and said dispersing agent dissolved in said quantity of water, and forming a fire extinguishing liquid solution that produces good immediate extinguishing effects when applied to extinguish a burning or smoldering fire, and very good long-term fire inhibiting effects when being proactively applied to protect combustible surfaces against the threat of fire.
8. The aqueous-based fire extinguishing liquid concentrate of claim 7, wherein said alkali metal salts of nonpolymeric saturated carboxylic acids for inclusion in the composition comprises: alkali metal salts of oxalic acid; alkali metal salts of gluconic acid; alkali metal salts of citric acid; and also alkali metal salts of tartaric acid.
9. The aqueous-based fire extinguishing liquid concentrate of claim 7, wherein said alkali metal salts of nonpolymeric saturated carboxylic acids comprise potassium carboxylates.
10. The aqueous-based fire extinguishing liquid concentrate of claim 7, wherein said alkali metal salts of nonpolymeric saturated carboxylic acids comprise tripotassium citrate monohydrate (TPC).
11. The aqueous-based fire extinguishing liquid concentrate according to claim 7, wherein the alkali metal salt is a sodium or potassium salt.
12. The aqueous-based fire extinguishing liquid concentrate according to claim 7, wherein the alkali metal salt is tripotassium citrate.
13. The aqueous-based fire extinguishing liquid concentrate according to claim 7, wherein said coalescing agent is triethyl citrate, an ester of citric acid.
14. A method of fighting a fire comprising the steps of applying fire extinguishing foam material produced in claim 7 to the surfaces to be proactively protected from a wildfire.
15. A method of fighting a fire comprising the steps of applying fire extinguishing foam material produced in claim 7 to surfaces ignited or consumed by fire to be extinguished by said fire extinguishing foam material.
    """
    
    annotations = annotate_patent_claims(sample_claims)
    print("Annotations:")
    print(annotations)
