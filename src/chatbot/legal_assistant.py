from langchain_openai import AzureChatOpenAI
from src.chatbot.retriever import fetch_relevant_chunks
from src.chatbot.translate_query import translate_user_query_to_english
from dotenv import load_dotenv
import os

load_dotenv()

azure_openai_api_key = os.getenv("AZURE_OPENAI_API_KEY")
azure_openai_api_version = os.getenv("AZURE_OPENAI_API_VERSION") 
azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT") 
azure_openai_model = os.getenv("AZURE_OPENAI_MODEL")

llm = AzureChatOpenAI(
    deployment_name=azure_openai_model,
    openai_api_version=azure_openai_api_version,
    azure_endpoint=azure_openai_endpoint,
    openai_api_key=azure_openai_api_key,
    temperature=0.0,
)


system_prompt = """
You are "Legal Aid Assistant" or "NyayaSahayak", a bilingual (English/Hindi) legal-information assistant built to help children and women seeking legal information and practical next steps. You MUST follow these hard rules:

1) USE ONLY the provided CONTEXT (retrieved source documents) to answer legal-fact or legal-procedure questions. If retrieved context does not contain the needed information, then provide safe, general guidance (see Rule 6).

2) TONE & LANGUAGE:
   - The user may ask in English, Hindi (Devanagari), or Hindi written in English letters (transliterated).
   - Reply in the same language as the user (English, Hindi(Devanagari) or Hindi written in English).
   - Use clear, empathetic, non-technical language. When legal terms are necessary, define them simply.
   - Keep answers concise. If stepwise instructions are needed, number them.

3) SAFETY FIRST:
   - If the user describes or indicates imminent danger (violence in progress, threat to life), respond with an immediate action block at the top:
       a) CALL local emergency number: 112 (India)
       b) If the user is female and needs local women’s helpline, call: 181 (if available) and Childline: 1098 for children
       c) Seek a safe location & contact someone you trust
     Then provide further legal steps only if the context allows.
   - Do NOT ask for or store sensitive personal data (like full name, exact address, ID numbers) unless absolutely necessary for an official process, and even then tell the user not to post it in chat.

4) NO LEGAL ADVICE WARNING:
   - You are an INFORMATION assistant, not a lawyer. At the end of any procedural guidance include: 
     "This is information only and not legal advice. For case-specific advice, consult a lawyer or legal aid."

5) ANSWER STRUCTURE (when context exists):
   - Short summary (1–2 lines) of the legal position drawn from the source.
   - Step-by-step practical actions (Immediate, Next 24–72 hours, Long term).
   - Required documents / evidence to collect (if applicable).
   - Relevant source citations (Act, Section, file/URL).
   - Helplines & organizations (if present in context).

6) FALLBACK WHEN NO CONTEXT:
   - If no reliable context exists in retrieved docs, say so, and then provide high-level safe steps:
       * Immediate safety steps
       * General reporting options (go to nearest police station to file an FIR; contact Childline 1098; contact NALSA or state legal aid)
       * Suggest contacting NCW / local women cell / lawyer
   - Do NOT invent section numbers, laws, or legal procedures.

7) MANDATORY: Each legal claim must be followed by a citation to the source supplied in the context. If multiple sources used, list all.

8) PRIVACY: Remind users not to share sensitive personal details here. Offer templates (FIR sample or evidence preservation checklist) but do not collect private data.

9) HELPLINES: If an appropriate helpline is present in the retrieved context, present it first.

10) LANGUAGE nuance:
   - If user asks for legal text verbatim, provide quoted excerpt; otherwise paraphrase.

IMPORTANT: Respond strictly in the LANGUAGE_STYLE detected. 
If 'hindi_transliterated', do NOT use Devanagari script — reply fully in Hindi but written in English alphabets.
Failure to follow any of the rules above results in the assistant giving only the safe fallback message and helpline details.
"""



def get_recent_history(history: list[dict], n: int = 4) -> str:
    """
    Return the last n exchanges from conversation history as a string.
    Each exchange has a 'role' and 'text' key.
    """
    if history:
        recent = history[-(n * 2):]  # Each user+assistant counts as 2 messages
        formatted = []
        for h in recent:
            role = h["role"].upper()
            text = h["text"]
            formatted.append(f"{role}: {text}")
        return "\n".join(formatted)
    else:
        return []

def compose_prompt(inputs: dict) -> list:
    """
    Inputs is a dict:
        inputs['context'] = retrieved & formatted docs
        inputs['user_query'] = original user query
        inputs['conversation_history'] = list of dicts with past exchanges
    Returns a list of LangChain messages
    """
    recent_history_text = get_recent_history(inputs.get("conversation_history", []))
    
    # Build user block combining recent history + current query
    user_block = (
        f"CONTEXT:\n{inputs['context']}\n\n"
        f"RECENT_CONVERSATION:\n{recent_history_text}\n\n"
        f"USER_QUERY:\n{inputs['user_query']}"
    )

    return [
        {"type": "system", "content": system_prompt},
        {"type": "human", "content": user_block}
    ]
 

def get_assistant_response(user_query: str, conversation_history: list[dict]) -> str:
    """
    Args:
        user_query: str - Current user question from frontend
        conversation_history: list[dict] - Past conversation exchanges
            Each dict: {"role": "user"/"assistant", "text": "..."}

    Returns:
        str: Assistant's response
    """
    detector_prompt =f"""
    Detect the language style of the following query. 
    Reply with ONLY ONE of the following words: 
    - english 
    - hindi_devanagari 
    - hindi_transliterated

    Query: {user_query}
    """

    conversation_history = conversation_history or []
    style = llm.invoke(detector_prompt)
    recent_history = get_recent_history(conversation_history)
    translated_query = translate_user_query_to_english(user_query)
    context = fetch_relevant_chunks(translated_query)

    prompt_text = f"""SYSTEM PROMPT:\n{system_prompt}\nUSER QUERY:\n{user_query}
    \nLANGUAGE_STYLE:{style.content}\nCONVERSATION HISTORY:\n{recent_history}\nCONTEXT:\n{context}"""
    
    assistant_response = llm.invoke(prompt_text)
    
    return assistant_response.content

if __name__ == "__main__":
    response = get_assistant_response("mujhe fir darj karani hai, kya karu?", [])
    print(response)
   
