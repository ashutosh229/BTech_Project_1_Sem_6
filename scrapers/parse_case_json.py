import json

def parse_real_case_json(file_path):
    """Dynamically parses the actual legal JSON format into a flat dictionary."""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)
        
    elements = raw_data.get("elements_by_title", {})
    
    # Base dictionary
    clean_case = {
        "case_id": raw_data.get("case_title", "Unknown Case"),
        "url": raw_data.get("url", ""),
        "evidence_list": [], # To be filled later
        "outcome": "unknown" # To be filled later
    }

    # Dynamically extract whatever sections exist in this specific case
    for section_title, section_list in elements.items():
        # Create a clean dictionary key (e.g., "Court's Reasoning" -> "courts_reasoning")
        clean_key = section_title.lower().replace(" ", "_").replace("'", "")
        
        # Join all the text in this section
        section_text = " ".join([item.get("text", "") for item in section_list]).strip()
        
        # Add to our clean case object
        clean_case[clean_key] = section_text
        # --- FALLBACK LOGIC FOR RAG ---
    # We MUST have a 'primary_facts' string for our embeddings later.
    if "fact" in clean_case and clean_case["fact"].strip():
        clean_case["primary_facts"] = clean_case["fact"]
    elif "analysis_of_the_law" in clean_case and clean_case["analysis_of_the_law"].strip():
        clean_case["primary_facts"] = clean_case["analysis_of_the_law"]
    else:
        # If all else fails, grab the first 1000 characters of whatever text exists
        all_text = " ".join([v for k, v in clean_case.items() if isinstance(v, str)])
        clean_case["primary_facts"] = all_text[:1000]
    return clean_case

# Example usage:
my_case = parse_real_case_json('allahabad_2015_3099880.json')
print(my_case.keys())
my_case = parse_real_case_json('allahabad_2015_27309404.json')
print(my_case.keys())
