"""
NyayaRAG Implementation with Groq + LangChain
Implements Retrieval-Augmented Generation for Judgment Prediction
Follows NyayaRAG paper architecture for Indian legal system

Features:
- Retrieve similar cases using embeddings
- Augment with statutes and precedents
- Generate predictions + explanations with Groq LLM
"""

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
import os
import json
import numpy as np
from typing import Dict, List, Tuple, Optional
from pathlib import Path
from dotenv import load_dotenv

# ============================================================================
# 1. LOAD CONFIGURATION & API
# ============================================================================

# Load environment variables
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

if not groq_api_key:
    raise ValueError("❌ GROQ_API_KEY not found in .env file")

print("✓ Groq API key loaded")

# Initialize Groq LLM
llm = ChatGroq(
    groq_api_key=groq_api_key,
    model_name="llama-3.3-70b-versatile",  # High-quality reasoning
    temperature=0.2,  # Low temp for deterministic legal reasoning
    max_tokens=1000
)

print("✓ Groq LLM initialized (llama-3.3-70b-versatile)")


# ============================================================================
# 2. RAG CONTEXT BUILDER
# ============================================================================

class RAGContextBuilder:
    """Build contextual inputs for judgment prediction from RAG components."""
    
    def __init__(self, embeddings_path: str, analysis_path: str):
        """
        Args:
            embeddings_path: Path to shareable_legal_vectors.json
            analysis_path: Path to case analysis JSON with metadata
        """
        self.embeddings_path = embeddings_path
        self.analysis_path = analysis_path
        self.embeddings_list = []
        self.case_index = {}
        
        self._load_embeddings()
        self._load_case_analysis()
        
    def _load_embeddings(self):
        """Load shareable legal embeddings."""
        try:
            with open(self.embeddings_path, 'r', encoding='utf-8') as f:
                self.embeddings_list = json.load(f)
            
            # Build case ID index
            for i, item in enumerate(self.embeddings_list):
                if isinstance(item, dict):
                    if 'metadata' in item and 'case_id' in item['metadata']:
                        case_id = item['metadata']['case_id']
                        self.case_index[case_id] = i
            
            print(f"✓ Loaded {len(self.embeddings_list)} case embeddings")
            
        except Exception as e:
            print(f"⚠ Failed to load embeddings: {e}")
    
    def _load_case_analysis(self):
        """Load sample case analysis for context."""
        try:
            with open(self.analysis_path, 'r', encoding='utf-8') as f:
                self.case_analysis = json.load(f)
            print(f"✓ Loaded case analysis")
        except Exception as e:
            print(f"⚠ Failed to load case analysis: {e}")
            self.case_analysis = {}
    
    def retrieve_similar_cases(self, query_embedding: np.ndarray, k: int = 5) -> List[Dict]:
        """
        Retrieve top-k similar cases using cosine similarity.
        
        Args:
            query_embedding: Case embedding vector
            k: Number of similar cases to retrieve
            
        Returns:
            List of (case_id, similarity_score) tuples
        """
        if len(self.embeddings_list) == 0:
            return []
        
        # Extract all embeddings
        embedding_vectors = []
        case_ids = []
        
        for item in self.embeddings_list:
            if isinstance(item, dict):
                if 'metadata' in item and 'case_id' in item['metadata']:
                    case_id = item['metadata']['case_id']
                elif 'case_id' in item:
                    case_id = item['case_id']
                else:
                    continue
                
                # Extract embedding
                if 'embedding' in item:
                    vec = item['embedding']
                elif 'vector' in item:
                    vec = item['vector']
                else:
                    continue
                
                case_ids.append(case_id)
                embedding_vectors.append(vec)
        
        if not embedding_vectors:
            return []
        
        # Cosine similarity
        index_array = np.array(embedding_vectors, dtype=np.float32)
        query_norm = query_embedding / (np.linalg.norm(query_embedding) + 1e-8)
        index_norm = index_array / (np.linalg.norm(index_array, axis=1, keepdims=True) + 1e-8)
        
        similarities = np.dot(index_norm, query_norm)
        top_k_indices = np.argsort(similarities)[::-1][:k]
        
        results = []
        for idx in top_k_indices:
            case_id = case_ids[idx]
            score = float(similarities[idx])
            results.append({"case_id": case_id, "similarity": score})
        
        return results
    
    def build_rag_context(self, 
                         case_facts: str,
                         similar_cases: List[Dict],
                         statutes: Optional[List[str]] = None,
                         pipeline_type: str = "CaseText + Statutes + Precedents") -> str:
        """
        Build RAG context string for LLM input.
        
        Args:
            case_facts: Summarized facts of the case
            similar_cases: Retrieved similar precedents
            statutes: List of relevant statutes
            pipeline_type: Which RAG pipeline to use
            
        Returns:
            Formatted RAG context string
        """
        context = f"## Case Facts\n{case_facts}\n\n"
        
        # Add statutes if available
        if statutes and len(statutes) > 0:
            context += "## Relevant Statutes & Laws\n"
            for statute in statutes[:3]:  # Top 3 statutes
                context += f"- {statute}\n"
            context += "\n"
        
        # Add similar cases (precedents)
        if similar_cases:
            context += "## Similar Precedent Cases (Retrieved via RAG)\n"
            for i, case in enumerate(similar_cases[:5], 1):
                context += f"{i}. {case['case_id']} (Similarity: {case['similarity']:.4f})\n"
            context += "\n"
        
        return context


# ============================================================================
# 3. JUDGMENT PREDICTION ENGINE
# ============================================================================

class NyayaRAGPredictor:
    """
    Judgment Prediction with RAG using Groq LLM.
    Combines case facts + statutes + precedents for decision-making.
    """
    
    def __init__(self, llm: ChatGroq, rag_builder: RAGContextBuilder):
        """
        Args:
            llm: Groq LLM instance
            rag_builder: RAG context builder
        """
        self.llm = llm
        self.rag_builder = rag_builder
        self.parser = StrOutputParser()
        
        # Define system prompt for legal judgment
        self.system_prompt = """You are an expert legal AI system called NYAYARAG, specialized in Indian legal judgment prediction.

Your task:
1. Analyze the case facts provided
2. Consider relevant statutes and laws
3. Review similar precedent cases
4. Predict the likely judgment (ALLOWED or DISMISSED)
5. Provide detailed legal reasoning

Output format (MANDATORY):
##PREDICTION: [ALLOWED or DISMISSED]
##CONFIDENCE: [0.0 to 1.0]
##EXPLANATION: [Detailed legal reasoning citing facts, laws, and precedents]

Key Guidelines:
- ALLOWED: Appeal allowed, plaintiff wins, petition accepted
- DISMISSED: Appeal dismissed, plaintiff loses
- Base prediction on case similarity and precedent outcomes
- Cite specific statutes and precedent cases
- Be precise and legally coherent
- Keep explanation under 500 words"""
    
    def predict(self, 
                case_facts: str,
                similar_cases: List[Dict],
                statutes: Optional[List[str]] = None,
                case_id: Optional[str] = None) -> Dict:
        """
        Generate judgment prediction with explanation using RAG.
        
        Args:
            case_facts: Summarized case facts
            similar_cases: Retrieved similar precedent cases
            statutes: Relevant statutes (optional)
            case_id: Case identifier for logging
            
        Returns:
            Dict with prediction, confidence, and explanation
        """
        
        print(f"\n{'='*70}")
        print(f"🔮 NYAAYARAG JUDGMENT PREDICTION")
        print(f"{'='*70}")
        print(f"Case ID: {case_id or 'Unknown'}")
        print(f"Retrieved {len(similar_cases)} similar cases")
        print(f"Statutes provided: {len(statutes) if statutes else 0}")
        
        try:
            # Build RAG context
            rag_context = self.rag_builder.build_rag_context(
                case_facts=case_facts,
                similar_cases=similar_cases,
                statutes=statutes
            )
            
            # Create message for LLM
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=f"""Based on the following legal context, predict the judgment:

{rag_context}

Provide your prediction with detailed reasoning.""")
            ]
            
            # Call Groq LLM
            print("\n🤖 Calling Groq LLM (llama-3.3-70b-versatile)...")
            response = self.llm.invoke(messages)
            output = self.parser.invoke(response)
            
            # Parse response
            result = self._parse_prediction(output, case_id)
            
            print(f"\n✅ Prediction Complete")
            print(f"   Verdict: {result['prediction']}")
            print(f"   Confidence: {result['confidence']:.2%}")
            
            return result
            
        except Exception as e:
            print(f"❌ Error during prediction: {e}")
            return {
                "case_id": case_id,
                "prediction": "ERROR",
                "confidence": 0.0,
                "explanation": f"Error: {str(e)}",
                "status": "failed"
            }
    
    def _parse_prediction(self, output: str, case_id: Optional[str] = None) -> Dict:
        """Parse LLM output into structured prediction."""
        
        result = {
            "case_id": case_id,
            "prediction": "UNKNOWN",
            "confidence": 0.5,
            "explanation": output,
            "status": "success"
        }
        
        try:
            # Extract prediction
            if "##PREDICTION: ALLOWED" in output.upper():
                result["prediction"] = "ALLOWED"
            elif "##PREDICTION: DISMISSED" in output.upper():
                result["prediction"] = "DISMISSED"
            
            # Extract confidence
            lines = output.split('\n')
            for line in lines:
                if "##CONFIDENCE:" in line:
                    conf_str = line.replace("##CONFIDENCE:", "").strip()
                    try:
                        result["confidence"] = float(conf_str)
                    except:
                        pass
            
            # Extract explanation
            if "##EXPLANATION:" in output:
                parts = output.split("##EXPLANATION:")
                if len(parts) > 1:
                    result["explanation"] = parts[1].strip()
            
        except Exception as e:
            print(f"⚠ Parsing error: {e}")
        
        return result


# ============================================================================
# 4. MAIN PIPELINE
# ============================================================================

def run_nyaag_pipeline(case_facts: str,
                       case_id: str = "test_case",
                       statutes: Optional[List[str]] = None):
    """
    Run complete NyayaRAG pipeline: RAG retrieval + LLM prediction.
    
    Args:
        case_facts: Case summary/facts
        case_id: Case identifier
        statutes: Optional list of statutes
    """
    
    print("\n" + "="*70)
    print("📋 NYAAYARAG: JUDGMENT PREDICTION WITH RAG")
    print("="*70)
    
    # Initialize RAG builder
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    EMBEDDINGS_PATH = os.path.join(BASE_DIR, "..", "..", "outputs", "shareable_legal_vectors.json")
    ANALYSIS_PATH = os.path.join(BASE_DIR, "..", "..", "outputs", "system_final_allahabad_2015_3099880.json")
    
    print(f"\n📂 Loading RAG resources...")
    rag_builder = RAGContextBuilder(EMBEDDINGS_PATH, ANALYSIS_PATH)
    
    # Create random query embedding for demonstration
    query_embedding = np.random.randn(768).astype(np.float32)
    
    # Retrieve similar cases
    print(f"\n📚 Retrieving similar precedent cases...")
    similar_cases = rag_builder.retrieve_similar_cases(query_embedding, k=5)
    
    # Initialize predictor
    predictor = NyayaRAGPredictor(llm, rag_builder)
    
    # Default statutes if not provided
    if not statutes:
        statutes = [
            "Indian Penal Code, 1860",
            "Indian Evidence Act, 1872",
            "Constitution of India, Article 226"
        ]
    
    # Make prediction
    result = predictor.predict(
        case_facts=case_facts,
        similar_cases=similar_cases,
        statutes=statutes,
        case_id=case_id
    )
    
    # Display results
    print(f"\n{'='*70}")
    print(f"📊 FINAL JUDGMENT PREDICTION")
    print(f"{'='*70}")
    print(f"Case: {result['case_id']}")
    print(f"\n🎯 Verdict: {result['prediction']}")
    print(f"📈 Confidence: {result['confidence']:.2%}")
    print(f"\n📝 Reasoning:\n{result['explanation'][:500]}...")
    print(f"\n{'='*70}\n")
    
    return result


# ============================================================================
# 5. EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    
    # Example case facts
    example_case_facts = """
    Case: Smt. Pushpa Sareen vs State Of U.P. (2015)
    
    Facts:
    - The appellant challenges the decision of the lower court regarding property ownership
    - Case involves dispute over interpretation of a deed executed in 1905
    - Parties belong to a Hindu family governed by Marumakkathayam law
    - Evidence includes original property deeds and transaction documents
    - Cross-examination revealed conflicting accounts of the transaction
    
    Legal Issues:
    1. Whether the transaction (Exhibit B-9) is void in law
    2. Whether the deed release was properly executed
    3. Applicability of Hindu succession law
    
    Arguments:
    - Appellant contends the transaction violates property transfer laws
    - Respondent argues the transaction is valid under applicable law
    - Previous courts ruled in favor of respondent
    """
    
    # Run the pipeline
    result = run_nyaag_pipeline(
        case_facts=example_case_facts,
        case_id="pushpa_sareen_vs_up_2015",
        statutes=[
            "Hindu Succession Act, 1956",
            "Indian Evidence Act, 1872", 
            "Transfer of Property Act, 1882"
        ]
    )
