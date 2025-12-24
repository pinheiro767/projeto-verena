import os
import requests
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import datetime

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
    
    # URL do modelo FLASH 2.0
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"
    
    headers = {"Content-Type": "application/json"}
    
    ano_atual = datetime.datetime.now().year
    
    # --- AQUI ESTÁ A MUDANÇA PARA ELA SER FOCADA ---
    prompt_sistema = f"""
    Você é a VERENA.
    
    SUA MISSÃO: Responder perguntas de cuidadores de idosos com EXTREMA OBJETIVIDADE.
    
    REGRAS DE OURO (Siga estritamente):
    1. ZERO ENROLAÇÃO: Não comece com "Olá, que bom ter você...", "Entendo sua situação...". Vá direto para a resposta técnica.
    2. FOCO TOTAL: Responda APENAS o que foi perguntado. Se perguntou sobre "dor", fale SÓ de dor. Não fale de alimentação ou banho se não foi pedido.
    3. LEI E CIÊNCIA: Cite o Artigo do Estatuto do Idoso ou DOI científico ({ano_atual-5}-{ano_atual}) que justifique sua resposta. Seja breve na citação.
    4. FORMATO: Use parágrafos curtos.
    5. O paciente é SEMPRE IDOSO.
    
    PERGUNTA: '{msg}'
    """
    
    payload = {
        "contents": [{
            "parts": [{
                "text": prompt_sistema
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
                texto_ia = "Erro ao processar resposta."
                
            return jsonify({"resposta": texto_ia.replace('\n', '<br>')})
        else:
            return jsonify({"resposta": f"Erro Google: {response.text}"})
            
    except Exception as e:
        return jsonify({"resposta": f"Erro interno: {str(e)}"})

if __name__ == '__main__':
    app.run(debug=True)