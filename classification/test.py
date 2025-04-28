from LLM import Openai
from trizClassification import classify_patent, retrieveContext

abstract =r"""
'A process can be used for preparing nanoparticles containing at least one bio-resorbable polyester. 
The nanoparticles are in the form of a powder with a Z-Average particle size D, in the range of 3 to 450 nm, and with a polydispersity index PDI 
in the range of 0.01 to 0.5. The process involves emulsion-solvent extraction or emulsion-solvent evaporation, and application of ultrasonic sound.
""" 
claims=r"""Claims 1 . A process for preparing nanoparticles by emulsion-solvent extraction or emulsion-solvent evaporation and application of ultrasonic sound, 
the process comprising: a) providing in a first container, an organic phase (OP), comprising a first solvent or solvent mixture S1, comprising one or more organic solvent(s), 
nd 0.1 to 55 by weight of the at least one bio-resorbable polyester,  b) providing, in a second container, an aqueous phase (AP), comprising a second solvent or solvent mixture S2, 
comprising water, and an emulsion stabilizing agent, c) providing a stream of the organic phase (OP) and a stream of the aqueous phase (AP), and joining the stream of the organic phase (OP) 
and the stream of the aqueous phase (AP), into a joint stream, d) passing the joint stream through an ultrasonic sound flow-through cell under sonication with a power input of 20 to 50 W per cm.sup.3 of the joint stream, 
to result in an emulsion appearing at an outlet of the ultrasonic sound flow-through cell, e) removing the first solvent or solvent mixture S1 and the second solvent or solvent mixture S2 by evaporation, or mixing the emulsion
with an excess amount of an aqueous extraction phase (EP) to form a combined phase, resulting in removal of the first solvent or solvent mixture S1 from the emulsion; to form nanoparticles, and f) obtaining the nanoparticles comprising the at 
least one bio-resorbable polyester by concentration and drying the nanoparticles, to obtain a polymer powder with a Z-Average particle size D.sub.z in the range of 1 to 450 nm and with a polydispersity index PDI in the range of 0.01 to 0.5. 2 .
The process according to claim 1, wherein the organic phase (OP) comprises the first solvent or solvent mixture S1, which is not or only partially miscible with the second solvent or solvent mixture S2 of the aqueous phase (AP).
3 . The process according to claim 1, wherein in d), the emulsion is an oil-in-water (O\/W) emulsion. 4 . The process according to claim 1, wherein in d), the emulsion is a water-in-oil (W.sub.1\/O) emulsion, which is, before e),
mixed and emulsified with an additional water phase (W.sub.2), to give a water-in-oil-in-water emulsion (W.sub.1\/O\/W.sub.2). 5 . The process according to claim 1, wherein the first solvent or solvent mixture S1 comprises dichloromethane, ethyl acetate, chloroform, benzyl alcohol, diethyl carbonate, dimethyl sulfoxide, methanol, propylene carbonate, isopropyl acetate, methyl acetate, methyl ethyl ketone, butyl lactate, isovaleric acid, or any mixture thereof. 6 . The process according to claim 1, wherein the second solvent or solvent mixture S2 comprises 60% or more and up to 100% by weight of water. 7 . The process according to claim 1, wherein the second solvent or solvent mixture S2 is not or only partially miscible with the first solvent or solvent mixture S1, so that the aqueous phase (AP) and the organic phase (OP) form separate phases after mixing. 8 . The process according to claim 1, wherein the aqueous phase (AP) comprises 0.1 to 10% by weight of the emulsion stabilizing agent. 9 . The process according to claim 1, wherein the aqueous extraction phase (EP) comprises 80% by weight or more of water. 10 . The process according to claim 1, wherein the at least one bio-resorbable polyester is selected from the group consisting of a polyorthoester, a polylactide, a polydioxanone, a polycaprolactone, a polytrimethyl carbonate, a polyglycolide, a poly(lactide-co-glycolide), a poly(lactide-co-caprolactone), a poly(lactide-co-trimethyl carbonate), a poly(lactide-co-polyethylene-glycol), and any blend thereof. 11 . The process according to claim 1, wherein the organic phase (OP) or the aqueous phase (AP) or both comprises) an active pharmaceutical ingredient. 12 . The process according to claim 1, wherein in c), the stream of the organic phase (OP) is provided at a flow rate of 0.5 to 50 ml\/min, and the stream of the aqueous phase (AP) is provided at a flow rate of 1.5 to 150 ml\/min, with the proviso that the flow rate of the aqueous phase (AP) is higher than the flow rate of the organic phase (OP), resulting in an oil-in-water emulsion (O\/W) in d). 13 . The process according to claim 1, wherein in c), the stream of the organic phase (OP) is provided at a flow rate of 1.5 to 150 ml\/min, and the stream of the aqueous phase (AP) is provided at a flow rate of 0.5 to 50 ml\/min, with the proviso that the flow rate of the organic phase (OP) is higher than the flow rate of the aqueous phase (AP), resulting in a water-in-oil emulsion (W.sub.1\/O) in d). 14 . The process according to claim 1, wherein a residence time of the joint stream ultrasonic sound flow-through cell is from 0.5 to 80 seconds. 15 . The process according to claim 1, wherein a flow rate of the joint stream h ultrasonic sound flow-through cell is from 2 to 200 ml\/min. 16 . The process according to claim 4, wherein the water-in-oil (W.sub.1\/O) emulsion is mixed and emulsified with the additional water phase (W.sub.2) by a static mixer or a further sonication flow-through cell. 17 . The process according to claim 8, wherein the emulsion stabilizing agent is polyvinyl alcohol or polysorbate.

"""
openai = Openai("OPENAI_KEY")

# Store all results by step_name
all_results = {}

# Run the classification twice
for i in range(2):
    result_steps = classify_patent(openai, abstract, claims)
    for step_name, output in result_steps.items():
        if step_name not in all_results:
            all_results[step_name] = []
        all_results[step_name].append(output)

# Build final markdown output
markdown_output = ""
for step_name, outputs in all_results.items():
    markdown_output += f"### {step_name.upper()}\n\n"
    for idx, output in enumerate(outputs, 1):
        markdown_output += f"**Iteration {idx}:**\n\n"
        markdown_output += f"```\n{output}\n```\n\n"

print(markdown_output)