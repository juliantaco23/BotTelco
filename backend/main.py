from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import openai
from dotenv import load_dotenv
import os

# Cargar las variables de entorno
load_dotenv()

# Configurar la API de OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

app = FastAPI()

# Definir el modelo de la solicitud
class QueryRequest(BaseModel):
    user_id: str
    query: str
    context: dict = None

# Manejador del contexto
user_contexts = {}

def update_context(user_id, new_context):
    if user_id not in user_contexts:
        user_contexts[user_id] = {}
    user_contexts[user_id].update(new_context)

@app.post("/chat/")
async def chat(request: QueryRequest):
    user_id = request.user_id
    query = request.query
    context = user_contexts.get(user_id, {})

    # Generar respuesta con GPT-3.5-turbo
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": query}
            ]
        )
        answer = response.choices[0].message['content'].strip()

        # Actualizar el contexto del usuario
        update_context(user_id, {'last_query': query, 'last_answer': answer})
        
        return {"answer": answer, "context": user_contexts[user_id]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
