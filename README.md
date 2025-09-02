# ConstituteAI GPT: Simplified Access to Legal Information

## Overview
ConstituteAI GPT is an AI-powered chatbot designed to provide accurate, simplified, and context-specific legal information from the Indian Constitution, related amendments, and case law. It serves a wide range of users including citizens, legal professionals, and law enforcement officers, offering intuitive and real-time access to legal knowledge.

## Features
- **Constitutional Data Retrieval**: Efficient querying of articles, amendments, and case laws with simplified explanations of complex legal texts.
- **Custom Responses**: Personalized responses using advanced AI models like Google Generative AI (Gemini), with context-aware explanations tailored to user needs.
- **Advanced Search Engine**: Uses HuggingFace models for embedding legal texts into vectors and FAISS for fast, scalable vector storage and retrieval.
- **Natural Language Processing**: Understands user intent and context for better query handling and simplifies legal concepts for non-legal audiences.
- **Multifaceted Use Cases**:
  - Assists **citizens** in understanding their rights.
  - Supports **law enforcement** with quick legal references.
  - Enables in-depth **research for legal professionals**.

## Tech Stack
| Technology           | Purpose                                         |
|---------------------|-------------------------------------------------|
| LangChain            | Manages prompt handling and interaction flows  |
| Google Generative AI  | Generates context-aware and simplified responses |
| HuggingFace          | Embeds constitutional text into vectors        |
| FAISS                | Enables efficient vector storage and retrieval |
| pypdf                | Extracts content from legal PDF documents      |
| re                   | Performs text pattern matching during preprocessing |
| FastAPI              | Serves machine learning models through APIs    |
| MongoDB              | Stores user interactions and feedback data     |

## Repository Structure
- **ml-model branch**: Contains the machine learning model code.

## Installation

### Prerequisites
- Python 3.8+
- FAISS-cpu(Vector Database)
- Virtual environment tool (optional but recommended)

### Backend Setup (ml-model branch)
1. Clone the repository:  
   `git clone https://github.com/wahid18-maqs/ConstitutionGPT.git`
2. Switch to the ml-model branch:  
   `git checkout ml-model`
3. Create and activate a virtual environment:  
   `python -m venv venv`  
   `source venv/bin/activate` *(On Windows: `venv\Scripts\activate`)*
4. Install dependencies:  
   `pip install -r requirements.txt`
5. Run the FastAPI server:  
   `uvicorn main:app --reload`

## How It Works
- Spearheaded development of a **97% accurate chatbot** for Indian Constitution consultations.
- Built a **Retrieval-Augmented Generation (RAG) pipeline** to optimize model performance by storing vectorized data in FAISS using the all-MiniLM-L6-v2 embedding model via Hugging Face Inference API.
- Leveraged **Gemini 1.5 Flash LLM** for fast, context-aware conversational chatbot responses.
- Utilized **FastAPI and React.js** for interaction and query submission, with **Docker** ensuring deployment scalability.
- **Data Collection**: Extracts legal text from PDFs and organizes it into structured formats.
- **Embedding and Storage**: Converts text into vector embeddings using HuggingFace models and stores embeddings in FAISS for fast querying.
- **User Interaction**: Handles user queries via frontend app and queries the FastAPI backend for relevant legal information.
- **Response Generation**: Retrieves relevant legal articles and explanations, simplifying responses using Google Generative AI.

## API Endpoints
- **POST /ask**: Accepts user queries and returns legal insights.

## Usage Scenarios
- **Citizens**: Ask about rights and legal remedies.
- **Lawyers**: Query specific constitutional clauses and case laws.
- **Law Enforcement**: Obtain quick legal references for enforcement purposes.

---
