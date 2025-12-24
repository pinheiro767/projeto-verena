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
    
    # URL do modelo FLASH 2.0 (Rápido e Inteligente)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"
    
    headers = {"Content-Type": "application/json"}
    
    # --- O NOVO CÉREBRO DA VERENA ---
    ano_atual = datetime.datetime.now().year
    
    prompt_sistema = f"""
    Você é a VERENA, uma Assistente Especializada em Gerontologia, Enfermagem e Direito do Idoso.
    
    SUAS REGRAS INEGOCIÁVEIS:
    1. O PACIENTE É SEMPRE UM IDOSO. Nunca assuma que é bebê, criança ou jovem. Se o usuário digitar errado (ex: "isos"), entenda como IDOSO.
    2. LEGISLAÇÃO: Ao orientar, baseie-se estritamente no Estatuto do Idoso (Lei 10.741/2003) e na Constituição. Cite o artigo da lei se for pertinente para defender o direito do idoso.
    3. CIÊNCIA: Se a pergunta for de saúde/técnica, use base científica dos últimos 5 anos ({ano_atual-5} a {ano_atual}). Se possível, cite o DOI ou a fonte (ex: "Segundo estudos recentes de 2023...").
    4. TOM DE VOZ: Profissional, acolhedor, mas técnico e pautado na lei.
    5. Se o usuário relatar DOR ou EMERGÊNCIA, oriente buscar médico imediatamente, mas explique o que pode ser com base na geriatria.
    
    Pergunta do usuário: '{msg}'
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
                texto_ia = "A Verena está consultando a base de dados, mas teve um erro. Tente novamente."
                
            return jsonify({"resposta": texto_ia.replace('\n', '<br>')})
        else:
            return jsonify({"resposta": f"Erro de conexão com o Google: {response.text}"})
            
    except Exception as e:
        return jsonify({"resposta": f"Erro interno: {str(e)}"})

if __name__ == '__main__':
    app.run(debug=True)