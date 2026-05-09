# Project Issues & Resolutions

This document tracks identified issues in the Groww MF RAG Assistant and their respective resolutions.

## 1. LLM Name Pedantry (Resolved)
- **Issue**: The RAG Assistant (Llama 3.1) refused to answer questions when the fund name in the query (e.g., "HDFC Mid-Cap Opportunities Fund") slightly differed from the canonical name in the database (e.g., "HDFC Mid Cap Fund Direct Growth"), even when explicitly told they are the same.
- **Resolution**: Implemented **Query Normalization** in `pipeline.py`. The system now uses regex to replace specific fund name mentions in the user's query with "the fund" or the canonical name before sending it to the LLM. This removes the naming conflict and allows the LLM to focus on the factual context.
- **Status**: Fixed.

## 2. Missing Fund Manager Data (Resolved)
- **Issue**: Queries about "Fund Manager" were returning "I do not have the information," even though the data was available in the raw Groww JSON files.
- **Root Cause**: The `cleaner.py` script in the ingestion pipeline was not extracting the `fund_manager` field from the raw data.
- **Resolution**: Updated `src/phase1_ingestion/subphase1_2_cleaning/cleaner.py` to include the `Fund Manager` field in the cleaned "Core Details" section. Reprocessed the entire ingestion pipeline (cleaning, chunking, and embedding).
- **Status**: Fixed.

## 3. Port Mismatch in Test Script (Resolved)
- **Issue**: The `test_api.py` script was trying to connect to port `8001`, but the FastAPI server was running on port `8000`.
- **Resolution**: Updated `test_api.py` to use port `8000`.
- **Status**: Fixed.

## 4. Missing Return Statistics (Resolved)
- **Issue**: Queries about fund performance (e.g., "return of last 5 years") were returning "I do not have the information."
- **Root Cause**: The `cleaner.py` script was not extracting return statistics (1Y, 3Y, 5Y) from the raw JSON data.
- **Resolution**: Updated `src/phase1_ingestion/subphase1_2_cleaning/cleaner.py` to extract the `stats` field (specifically the `FUND_RETURN` type) and include it in a new "Return Statistics" section. Reprocessed the ingestion pipeline.
- **Status**: Fixed.

## 5. Internal Server Error (500) during Retrieval (Resolved)
- **Issue**: The UI was returning "An internal server error occurred" for certain queries like "minimum investment required".
- **Root Cause**: The FastAPI server was running an outdated instance of the `RAGPipeline` that did not account for the database schema updates (missing return stats chunks in the retrieval count).
- **Resolution**: Updated `retrieve_context` in `pipeline.py` to increase `n_results` from 2 to 3, ensuring all 3 factual sections (Core, Fees, and Returns) are considered. Restarted the backend server to apply all code and logic updates.
- **Status**: Fixed.

## 6. Missing Portfolio Holdings (Resolved)
- **Issue**: Queries about fund holdings (e.g., "in which companies does the fund have holdings") were returning "I do not have the information."
- **Root Cause**: The `cleaner.py` script was not extracting the `holdings` array from the raw JSON data.
- **Resolution**: Updated `src/phase1_ingestion/subphase1_2_cleaning/cleaner.py` to extract the top 10 company names and their corpus percentage. Increased `n_results` to 4 in `pipeline.py` to include the new "Top Holdings" section. Reprocessed the ingestion pipeline and restarted the server.
- **Status**: Fixed.
