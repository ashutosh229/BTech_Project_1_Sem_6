import json
import os
import re


SUCCESS_PATTERNS = [
    r"\bpetition\s+is\s+allowed\b",
    r"\bappeal\s+is\s+allowed\b",
    r"\bapplication\s+is\s+allowed\b",
    r"\bsuit\s+is\s+decreed\b",
    r"\bdecreed\s+in\s+favour\s+of\b",
    r"\bissue\s+is\s+decided\s+in\s+favour\s+of\b",
    r"\bacquitted\b",
    r"\bconviction\s+is\s+set\s+aside\b",
    r"\bimpugned\s+order\s+is\s+set\s+aside\b",
    r"\brelief\s+is\s+granted\b",
]

FAILURE_PATTERNS = [
    r"\bpetition\s+is\s+dismissed\b",
    r"\bappeal\s+is\s+dismissed\b",
    r"\bapplication\s+is\s+dismissed\b",
    r"\bsuit\s+is\s+dismissed\b",
    r"\brejected\b",
    r"\bconvicted\b",
    r"\bconviction\s+is\s+upheld\b",
    r"\bview\s+taken.*must\s+be\s+upheld\b",
    r"\bnot\s+liable\s+to\s+be\s+interfered\s+with\b",
    r"\bstands\s+dismissed\b",
]

PARTIAL_PATTERNS = [
    r"\bpartly\s+allowed\b",
    r"\bpartially\s+allowed\b",
    r"\ballowed\s+in\s+part\b",
    r"\bdisposed\s+of\b",
    r"\bmodified\s+to\s+the\s+extent\b",
]


def _join_elements(elements, keys):
    chunks = []
    for key in keys:
        if key in elements:
            chunks.append(" ".join(item.get("text", "") for item in elements[key]))
    return " ".join(chunks)


def _normalize(text):
    text = (text or "").lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_case_outcome(elements):
    terminal_text = _join_elements(
        elements,
        ["Conclusion", "Judgment", "Judgement", "Final Order"],
    )
    candidate_text = terminal_text if terminal_text.strip() else _join_elements(
        elements,
        ["Court's Reasoning", "Analysis of the law", "Analysis"],
    )
    text = _normalize(candidate_text)

    if not text:
        return "Unknown"

    partial_hit = any(re.search(p, text) for p in PARTIAL_PATTERNS)
    success_hit = any(re.search(p, text) for p in SUCCESS_PATTERNS)
    failure_hit = any(re.search(p, text) for p in FAILURE_PATTERNS)
    terminal_tail = text[-800:]

    if re.search(r"\b(suit|appeal|petition|revision|complaint|case)\s+is\s+(accordingly\s+)?dismissed\b", terminal_tail):
        return "Dismissed/Weak"
    if re.search(r"\b(suit|appeal|petition|revision|complaint|case)\s+is\s+(hereby\s+)?rejected\b", terminal_tail):
        return "Dismissed/Weak"
    if re.search(r"\b(suit|appeal|petition|revision|complaint)\s+is\s+(hereby\s+)?allowed\b", terminal_tail):
        return "Allowed/Success"

    if partial_hit:
        return "Partial/Mixed"
    if success_hit and not failure_hit:
        return "Allowed/Success"
    if failure_hit and not success_hit:
        return "Dismissed/Weak"
    if success_hit and failure_hit:
        return "Partial/Mixed"
    return "Unknown"

def parse_real_case_json(file_path):
    """Dynamically parses the actual legal JSON format into a flat dictionary."""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)
        
    elements = raw_data.get("elements_by_title", {})
    
    # Base dictionary
    clean_case = {
        "case_id": os.path.splitext(os.path.basename(file_path))[0],
        "case_title": raw_data.get("case_title", "Unknown Case"),
        "url": raw_data.get("url", ""),
        "evidence_list": [], # To be filled later
        "outcome": extract_case_outcome(elements)
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

# --- TEST BLOCK ---
if __name__ == "__main__":
    # Use a dummy example to avoid FileNotFoundError during pipeline runs
    TEST_FILE = 'allahabad_2015_3099880.json'
    if os.path.exists(TEST_FILE):
        my_case = parse_real_case_json(TEST_FILE)
        print(my_case.keys())
    else:
        print(f"⚠️ Test file {TEST_FILE} not found. Skipping local test.")
