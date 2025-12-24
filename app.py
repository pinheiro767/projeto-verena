import os
import requests
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("MINHA_KEY")

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/processar', methods=['POST'])
def processar():
    dados = request.json
    msg = dados.get('msg')
    
    # --- MUDANÇA AQUI: Usando o modelo QUE EXISTE NA SUA LISTA ---
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"
    
    headers = {"Content-Type": "application/json"}
    
    payload = {
        "contents": [{
            "parts": [{
                "text": f"""
                Aja como a VERENA: IA de apoio a cuidadores.
                Seja curta, empática e dê uma dica prática.
                O usuário disse: '{msg}'
                """
            }]
        }]
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            resultado = response.json()
            try:
                texto_ia = resultado['candidates'][0]['content']['parts'][0]['text']
            except:
                texto_ia = "A Verena entendeu, mas não conseguiu gerar texto. Tente reformular."
                
            return jsonify({"resposta": texto_ia.replace('\n', '<br>')})
        else:
            return jsonify({"resposta": f"Erro do Google: {response.text}"})
            
    except Exception as e:
        return jsonify({"resposta": f"Erro interno: {str(e)}"})

if __name__ == '__main__':
    app.run(debug=True)