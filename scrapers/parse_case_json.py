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
        
    return clean_case

# Example usage:
my_case = parse_real_case_json('./India_Kanoon_scraping/docs/allahabad_2015_27309404.json')