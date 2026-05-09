import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
from pathlib import Path
import chromadb
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))
from src.phase3_guardrails.guardrails import Guardrails

# Known fund names for strict pre-filtering
KNOWN_FUNDS = [
    "HDFC Large Cap Fund Direct Growth",
    "HDFC Mid Cap Fund Direct Growth",
    "HDFC ELSS Tax Saver Fund Direct Plan Growth",
    "HDFC Focused Fund Direct Growth",
    "HDFC Flexi Cap Direct Plan Growth"
]

class RAGPipeline:
    def __init__(self):
        db_dir = project_root / "data" / "chroma_db"
        
        # Initialize Guardrails
        self.guardrails = Guardrails()
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=str(db_dir))
        self.collection = self.client.get_collection(name="mutual_fund_facts")
        
        # Initialize LLM (Ensure GROQ_API_KEY is in environment variables)
        self.has_api_key = bool(os.getenv("GROQ_API_KEY"))
        if self.has_api_key:
            self.llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)
        else:
            print("Warning: GROQ_API_KEY not found. Running in mock LLM mode for testing.")
            
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", """You are a strictly factual, highly precise mutual fund assistant.
Your goal is to answer the user's question using ONLY the provided context.

The user is inquiring about the fund: {target_scheme}
Note: The user might use different names or shorthands (e.g., "Mid-Cap Opportunities" instead of "Mid Cap Fund"), but they always refer to this specific fund.

RULES:
1. Use ONLY the provided context to answer. Do not use outside knowledge.
2. If the context does not contain the answer, say "I do not have the information to answer that question."
3. Your response MUST NOT exceed 3 sentences.
4. You MUST NOT provide any investment advice, predictions, or recommendations. Keep it strictly factual.
5. Answer the question about {target_scheme} using the context provided.
"""),
            ("user", """Context:
{context}

User Question: {question}""")
        ])

    def extract_intent(self, query: str) -> str:
        """
        Subphase 2.1: Query Processing (Intent Extraction)
        Uses simple heuristic matching to guarantee the target fund is identified.
        """
        # Normalize query: lower case and replace hyphens with spaces
        query_normalized = query.lower().replace("-", " ")
        
        # Mapping common shorthand to exact scheme names
        shorthands = {
            "mid cap": "HDFC Mid Cap Fund Direct Growth",
            "midcap": "HDFC Mid Cap Fund Direct Growth",
            "opportunities": "HDFC Mid Cap Fund Direct Growth",
            "large cap": "HDFC Large Cap Fund Direct Growth",
            "elss": "HDFC ELSS Tax Saver Fund Direct Plan Growth",
            "tax saver": "HDFC ELSS Tax Saver Fund Direct Plan Growth",
            "focused": "HDFC Focused Fund Direct Growth",
            "flexi": "HDFC Flexi Cap Direct Plan Growth",
            "flexi cap": "HDFC Flexi Cap Direct Plan Growth"
        }
        
        for shorthand, exact_name in shorthands.items():
            if shorthand in query_normalized:
                return exact_name
                
        # Also check exact names (normalized)
        for exact_name in KNOWN_FUNDS:
            if exact_name.lower().replace("-", " ") in query_normalized:
                return exact_name
                
        return None

    def retrieve_context(self, scheme_name: str, query: str) -> dict:
        """
        Subphase 2.2: Retrieval Mechanism (Metadata Pre-Filtering)
        Hard filters by scheme_name, ensuring zero cross-contamination.
        """
        # We fetch top 4 chunks since there are now 4 chunks per scheme (Core, Fees, Returns, and Holdings)
        results = self.collection.query(
            query_texts=[query],
            n_results=4,
            where={"scheme_name": scheme_name}
        )
        
        if not results['documents'] or not results['documents'][0]:
            return None
            
        # Combine the chunks
        context_text = "\n\n".join(results['documents'][0])
        # Get metadata from the first chunk for citation
        metadata = results['metadatas'][0][0] 
        
        return {
            "text": context_text,
            "source_url": metadata["source_url"],
            "last_updated": metadata["last_updated_date"]
        }

    def generate_response(self, query: str) -> str:
        """Main RAG execution flow."""
        # 0. Phase 3 Guardrails (PII & Advisory Checks)
        # Use LLM for nuanced intent check if API key is available
        guardrail_rejection = self.guardrails.evaluate_query_llm(
            query, 
            self.llm if self.has_api_key else None
        )
        if guardrail_rejection:
            return guardrail_rejection # Returns immediately WITHOUT citation
            
        # 1. Intent Extraction
        # Check for 'list funds' intent first
        list_intent_keywords = ["list", "which funds", "available funds", "what funds", "show all"]
        query_lower = query.lower()
        if any(keyword in query_lower for keyword in list_intent_keywords):
            funds_list = "\n".join([f"- {fund}" for fund in KNOWN_FUNDS])
            return f"I have detailed factual information for the following 5 HDFC mutual funds:\n\n{funds_list}\n\nPlease specify which one you'd like to know more about (e.g., 'What is the NAV of HDFC Mid Cap?')."

        target_scheme = self.extract_intent(query)
        if not target_scheme:
            return "Refused: Please specify which exact HDFC mutual fund you are asking about." # No citation
            
        # 2. Retrieval
        context_data = self.retrieve_context(target_scheme, query)
        if not context_data:
            return f"I couldn't find data for {target_scheme} in my factual database." # No citation
            
        # 3. LLM Generation
        if self.has_api_key:
            import re
            # Normalize query: Replace specific fund mentions with 'the fund' to help the LLM 
            # bridge naming gaps between the query and the context.
            normalized_query = re.sub(r'HDFC [^?.]+(Fund|Plan|Growth|Opportunities)', 'the fund', query, flags=re.IGNORECASE)
            
            chain = self.prompt_template | self.llm | StrOutputParser()
            llm_response = chain.invoke({
                "context": context_data["text"],
                "question": normalized_query,
                "target_scheme": target_scheme
            })
        else:
            # Mock response for local execution without API keys
            llm_response = f"[MOCKED LLM RESPONSE based on context from {target_scheme}]: The requested data is available in the provided context."
            
        # 4. Refusal Handling & Citation Appending
        # If the LLM explicitly states it doesn't know, DO NOT append citations.
        if "I do not have the information" in llm_response:
            return llm_response
            
        # Otherwise, append the citation securely
        final_response = f"{llm_response}\n\n"
        final_response += f"Source: [{target_scheme}]({context_data['source_url']})\n"
        final_response += f"*Last updated from sources: {context_data['last_updated']}*"
        
        return final_response

if __name__ == "__main__":
    pipeline = RAGPipeline()
    
    print("Testing RAG Pipeline & Phase 3 Guardrails...\n")
    test_queries = [
        # Normal query (Should return URL)
        "What is the expense ratio for the HDFC Mid Cap fund?",
        
        # PII Check (Should block and NOT return URL)
        "My PAN is ABCDE1234F. What is the lock-in period for ELSS?",
        
        # Advisory Check (Should block and NOT return URL)
        "Which one is better to invest in, Flexi cap or Mid cap?",

        # Nuanced Advisory Check (Catchable by LLM Guardrail)
        "Is it a good idea for me to put my life savings into the HDFC Focused fund?",
        
        # Ambiguous / Not found Check (Should block and NOT return URL)
        "What is the NAV of an unknown fund?"
    ]
    
    for q in test_queries:
        print(f"Q: {q}")
        print(f"A:\n{pipeline.generate_response(q)}\n")
        print("-" * 50 + "\n")
