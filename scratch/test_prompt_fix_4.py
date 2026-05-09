from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import os
from dotenv import load_dotenv
import sys
import re

# Set encoding to utf-8
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

load_dotenv()

llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)

prompt_template = ChatPromptTemplate.from_messages([
            ("system", """You are a strictly factual, highly precise mutual fund assistant.
Your goal is to answer the user's question using ONLY the provided context.

RULES:
1. Use ONLY the provided context to answer. Do not use outside knowledge.
2. If the context does not contain the answer, say "I do not have the information to answer that question."
3. Your response MUST NOT exceed 3 sentences.
4. You MUST NOT provide any investment advice, predictions, or recommendations. Keep it strictly factual.
"""),
            ("user", """Context:
{context}

User Question: {question}""")
        ])

context = """Scheme: HDFC Mid Cap Fund Direct Growth
Section: Core Details

- Fund Name: HDFC Mid Cap Fund Direct Growth
- Fund House: HDFC Mutual Fund
- Category: Equity - Mid Cap
- Benchmark: NIFTY Midcap 150 Total Return Index
- AUM (Assets Under Management): ₹85357.9246 Crores
- Latest NAV: ₹217.72 (As of 30-Apr-2026)"""

query = "What is the NAV of HDFC Mid-Cap Opportunities Fund?"

# Simple normalization: Replace the mention of 'HDFC Mid-Cap Opportunities Fund' with 'the fund'
# In the real code, we can use regex or just replace the detected shorthand
normalized_query = "What is the NAV of the fund?"

chain = prompt_template | llm | StrOutputParser()
response = chain.invoke({
    "context": context,
    "question": normalized_query
})

print(f"Original Query: {query}")
print(f"Normalized Query: {normalized_query}")
print(f"Response:\n{response}")
