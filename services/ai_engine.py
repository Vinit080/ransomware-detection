from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from core.config import settings
from models.telemetry import TelemetryPayload

class AIEngine:
    def __init__(self):
        self.llm = ChatOpenAI(
            api_key=settings.OPENAI_API_KEY, 
            model="gpt-4o", 
            temperature=0.2
        )
        self.embeddings = OpenAIEmbeddings(api_key=settings.OPENAI_API_KEY)
        
        # Initialize Vector Store (ChromaDB)
        self.vector_store = Chroma(
            collection_name="threat_intelligence",
            embedding_function=self.embeddings,
            persist_directory=settings.CHROMA_DB_DIR
        )
        
        # Seed the DB if it's empty (just for the demo)
        self._seed_threat_intel()

    def _seed_threat_intel(self):
        """Seeds the vector DB with some basic threat intel for RAG."""
        try:
            if len(self.vector_store.get()['ids']) == 0:
                docs = [
                    Document(page_content="Ransomware typically deletes Volume Shadow Copies using 'vssadmin.exe Delete Shadows /All /Quiet' to prevent recovery.", metadata={"source": "threat_intel_db", "family": "general"}),
                    Document(page_content="High entropy files (entropy > 7.5) with changed extensions (e.g., .enc, .locked) usually indicate active file encryption by ransomware.", metadata={"source": "threat_intel_db", "family": "general"}),
                    Document(page_content="Connections to non-standard high ports or port 4444 often indicate Command and Control (C2) frameworks like Metasploit or Cobalt Strike.", metadata={"source": "threat_intel_db", "family": "general"})
                ]
                self.vector_store.add_documents(docs)
        except Exception as e:
            print(f"Failed to seed vector DB: {e}")

    def analyze_telemetry(self, telemetry: TelemetryPayload, yara_results: list) -> dict:
        """Uses RAG and Semantic Analysis to analyze the telemetry."""
        
        # 1. Retrieve relevant threat intel context based on the processes and network
        query_texts = [p.command_line for p in telemetry.processes]
        query_texts.extend([str(n.destination_port) for n in telemetry.networks])
        
        retrieved_docs = []
        for q in query_texts:
            docs = self.vector_store.similarity_search(q, k=1)
            retrieved_docs.extend(docs)
            
        context = "\n".join([d.page_content for d in set(retrieved_docs)])
        
        # 2. Semantic Analysis using LLM
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert SOC Analyst and Reverse Engineer. Analyze the provided sandbox telemetry and YARA rule hits. Determine if this is malicious. Provide a classification, MITRE ATT&CK mapping, and a plain-English explanation."),
            ("user", "Threat Intel Context:\n{context}\n\nTelemetry JSON:\n{telemetry_json}\n\nYARA Hits:\n{yara_hits}\n\nPlease output the analysis in a structured format: Classification, MITRE Mapping, Explanation.")
        ])
        
        chain = prompt | self.llm
        
        response = chain.invoke({
            "context": context if context else "No specific threat intel context found.",
            "telemetry_json": telemetry.model_dump_json(indent=2),
            "yara_hits": str(yara_hits)
        })
        
        return {
            "analysis": response.content,
            "retrieved_context": context
        }

ai_engine = AIEngine()
