import re
from langchain_core.prompts import ChatPromptTemplate

class Guardrails:
    def __init__(self):
        # Basic Indian PAN Regex: 5 Letters, 4 Digits, 1 Letter
        self.pan_pattern = re.compile(r'[A-Za-z]{5}\d{4}[A-Za-z]{1}')
        # Basic Indian Aadhaar Regex: 12 digits (with optional spaces/dashes)
        self.aadhaar_pattern = re.compile(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}\b')
        
        # Advisory triggers (Fast keyword check)
        self.advisory_keywords = [
            "should i buy", "should i sell", "recommend", 
            "is it good to", "is it bad to", "better fund", 
            "which one is better", "invest my money", "give me advice"
        ]

        # LLM Intent Classification Prompt
        self.intent_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a security guardrail classifier for a Mutual Fund FAQ assistant.
Your task is to classify the user's intent into exactly one of these categories:
- FACTUAL: Asking for objective data like NAV, AUM, Expense Ratio, Exit Load, or Fund Manager names.
- ADVISORY: Asking for investment advice, recommendations, opinions on whether a fund is "good" or "bad", or help with a purchase decision.
- PII: Providing personal info like PAN, Aadhaar, or Bank details.

Output ONLY the category name.

Examples:
"What is the NAV of HDFC Mid Cap?" -> FACTUAL
"Should I invest in HDFC Large Cap?" -> ADVISORY
"Is 1.5% expense ratio good?" -> ADVISORY
"Compare which fund is better for retirement" -> ADVISORY
"My PAN is ABCDE1234F" -> PII
"""),
            ("user", "{query}")
        ])

        # LLM Refusal Generation Prompt
        self.refusal_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a polite, strictly factual mutual fund assistant.
The user has just asked a question that violates our safety or factual guidelines (e.g., asking for investment advice, providing PII, or asking about non-HDFC funds).

Your task: Generate a polite, 1-sentence refusal message.
- If it was PII: Explain you cannot process personal information for security reasons.
- If it was ADVISORY: Explain you only provide objective factual data and cannot give advice or recommendations.
- If it was UNKNOWN: Explain you only have data for 5 specific HDFC mutual funds.

Be professional and concise. DO NOT provide any external links or citations.
"""),
            ("user", "User Query: {query}\nReason for Refusal: {reason}")
        ])

    def check_pii(self, text: str) -> bool:
        """Returns True if PII (PAN/Aadhaar) is detected."""
        if self.pan_pattern.search(text) or self.aadhaar_pattern.search(text):
            return True
        return False

    def check_advisory_fast(self, text: str) -> bool:
        """Fast keyword check for advisory intent."""
        text_lower = text.lower()
        for keyword in self.advisory_keywords:
            if keyword in text_lower:
                return True
        return False

    def generate_refusal_llm(self, query: str, llm, reason: str) -> str:
        """Uses Groq to generate a polite, context-aware refusal."""
        if not llm:
            return f"Refused: {reason}. I can only provide objective factual data."
            
        try:
            chain = self.refusal_prompt | llm
            return chain.invoke({"query": query, "reason": reason}).content.strip()
        except Exception as e:
            return f"Refused: {reason}. I can only provide objective factual data."

    def evaluate_query_llm(self, query: str, llm) -> str:
        """
        Subphase 3.1: Intent Detection Layer (LLM Check)
        Uses Groq to classify nuanced intent and generate a polite refusal.
        """
        # 1. First run fast deterministic checks
        if self.check_pii(query):
            return self.generate_refusal_llm(query, llm, "PII detected")
            
        if self.check_advisory_fast(query):
            return self.generate_refusal_llm(query, llm, "Investment advice seeking")

        # 2. If it passes fast checks, use LLM for nuanced intent detection
        if llm:
            try:
                # Use a separate chain for classification to be precise
                category = (self.intent_prompt | llm).invoke({"query": query}).content.strip().upper()
                
                if "ADVISORY" in category:
                    return self.generate_refusal_llm(query, llm, "Investment advice seeking")
                if "PII" in category:
                    return self.generate_refusal_llm(query, llm, "Personal information detected")
            except Exception as e:
                print(f"Guardrail LLM check failed: {e}")
                pass
            
        return None

