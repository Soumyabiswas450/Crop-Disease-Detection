
DISEASE_KNOWLEDGE = {

    "blight": {
        "type": "Blight",
        "scientific_name": "Not specified",
        "cause": "The model identifies blight, but does not specify whether it is bacterial or fungal.",
        "symptoms": [
            "Leaf yellowing or drying may occur.",
            "Water-soaked or discoloured lesions may appear.",
            "Symptoms depend on the specific type of blight."
        ],
        "management": [
            "Get the specific blight type confirmed by an agricultural expert.",
            "Use healthy planting material.",
            "Remove infected plant debris where appropriate.",
            "Avoid applying pesticides before confirming the disease."
        ],
        "note": "The model's Blight class needs a more specific disease definition."
    },

    "brown spot": {
        "type": "Fungal Disease",
        "scientific_name": "Bipolaris oryzae",
        "cause": "A fungal disease affecting rice leaves, seedlings and sometimes grains.",
        "symptoms": [
            "Circular or oval brown spots on leaves.",
            "Spots may have a grey or light-brown centre.",
            "Reddish-brown margins around lesions.",
            "Severe infections can cause lesions to merge."
        ],
        "management": [
            "Use healthy, disease-free seeds.",
            "Remove infected crop debris.",
            "Practise crop rotation where suitable.",
            "Maintain balanced soil fertility.",
            "Use locally recommended tolerant varieties."
        ],
        "note": "Inspect affected leaves and monitor the spread of lesions."
    },

    "false smut": {
        "type": "Fungal Disease",
        "scientific_name": "Ustilaginoidea virens",
        "cause": "A fungal disease that infects individual grains in rice panicles.",
        "symptoms": [
            "Yellow or greenish spore balls appear on individual grains.",
            "Infected grains develop a velvety appearance.",
            "Spore balls gradually become larger.",
            "Only some grains in a panicle may be affected."
        ],
        "management": [
            "Monitor panicles around flowering and grain development.",
            "Remove and safely dispose of infected panicles where practical.",
            "Maintain balanced nutrient management.",
            "Follow local agricultural advisories for disease management."
        ],
        "note": "Pay particular attention to infected grains during panicle development."
    },

    "leaf smut": {
        "type": "Fungal Disease",
        "scientific_name": "Entyloma oryzae",
        "cause": "A fungal disease affecting rice leaves.",
        "symptoms": [
            "Small, slightly raised black spots on leaves.",
            "Spots may develop into pustules.",
            "Infection commonly occurs later in the growing season."
        ],
        "management": [
            "Monitor leaves for increasing numbers of spots.",
            "Maintain field sanitation.",
            "Avoid unnecessary fungicide application.",
            "Consult an agricultural expert if symptoms become widespread."
        ],
        "note": "Leaf smut is generally considered a minor disease, but local severity should be assessed."
    },

    "rice blast": {
        "type": "Fungal Disease",
        "scientific_name": "Pyricularia oryzae",
        "cause": "A fungal disease that can affect leaves, nodes and rice panicles.",
        "symptoms": [
            "Spindle-shaped lesions on leaves.",
            "Grey centres with brown borders.",
            "Blackening of infected stem nodes.",
            "Panicle neck infection can cause panicles to fall over."
        ],
        "management": [
            "Use healthy, disease-free seeds.",
            "Grow locally recommended resistant varieties.",
            "Avoid excessive nitrogen application.",
            "Maintain suitable plant spacing.",
            "Remove infected crop debris and weed hosts."
        ],
        "note": "Monitor leaf lesions and inspect the neck of the panicle for infection."
    },

    "stem rot": {
        "type": "Fungal Disease",
        "scientific_name": "Sclerotium oryzae",
        "cause": "A fungal disease affecting rice leaf sheaths and stems.",
        "symptoms": [
            "Small black or dark lesions near the waterline.",
            "Rotting of leaf sheaths and internal stems.",
            "Dark fungal structures may develop inside infected stems.",
            "Severe infection can cause plants to lodge or collapse."
        ],
        "management": [
            "Remove infected crop residues after harvest.",
            "Maintain balanced fertilizer application.",
            "Use suitable resistant or non-lodging varieties.",
            "Follow locally recommended water management practices.",
            "Avoid transferring irrigation water from infected fields to healthy fields."
        ],
        "note": "Inspect the lower stem and leaf sheath for dark lesions."
    },

    "tungro": {
        "type": "Viral Disease",
        "scientific_name": "Rice tungro viruses",
        "cause": "A viral disease transmitted by green leafhoppers.",
        "symptoms": [
            "Stunted plant growth.",
            "Reduced tillering.",
            "Yellow or orange-yellow leaves.",
            "Delayed flowering.",
            "Smaller panicles and poorly filled grains."
        ],
        "management": [
            "Monitor green leafhopper populations.",
            "Use locally recommended tungro-resistant varieties.",
            "Remove volunteer rice plants and weed hosts where appropriate.",
            "Follow integrated vector-management recommendations.",
            "Consult local agricultural experts when infection is suspected."
        ],
        "note": "Tungro is viral, so fungicides are not a treatment for the virus."
    },

    "healthy": {
        "type": "Healthy Classification",
        "scientific_name": "Not applicable",
        "cause": "The model classified the detected region as healthy.",
        "symptoms": [
            "No target disease symptoms were identified in this detected region."
        ],
        "management": [
            "Continue regular crop monitoring.",
            "Maintain balanced nutrition and irrigation.",
            "Use healthy seeds and proper field sanitation."
        ],
        "note": "A healthy classification does not guarantee that the entire plant or field is disease-free."
    }
}


def get_disease_details(disease_counts):

    disease_details = []

    for disease_name, count in disease_counts.items():

        key = disease_name.strip().lower()

        # Ignore background detections
        if key == "background" or count <= 0:
            continue

        information = DISEASE_KNOWLEDGE.get(key)

        if information:

            disease_details.append({
                "name": disease_name,
                "count": int(count),
                **information
            })

    return disease_details
