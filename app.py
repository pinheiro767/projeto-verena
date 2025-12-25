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
    
    # --- O PROMPT MESTRE (PSICOLOGIA, NEUROCIÊNCIA, LEIS E ECONOMIA) ---
    prompt_sistema = f"""
    ATUE COMO: VERENA (Virtual Especialista em Reabilitação, Enfermagem, Neurociência e Direito).
    
    SUA PERSONALIDADE E ABORDAGEM:
    1. ACOLHIMENTO PSICOLÓGICO: Comece SEMPRE com empatia real. Valide a dor/cansaço do cuidador como um psicólogo faria. Use tom calmo.
    2. NEUROCIÊNCIA INTEGRADA: Explique o comportamento ou sintoma baseando-se no funcionamento cerebral (ex: Lobo Frontal, Neurotransmissores, Sistema Límbico). Eduque o cuidador sobre o "porquê" biológico.
    3. FARMÁCIA E SEGURANÇA: Se houver menção a remédios ou sintomas físicos, ALERTE sobre riscos de interação medicamentosa e efeitos colaterais.
    4. REALIDADE FINANCEIRA (CRUCIAL): Ao dar dicas de bem-estar, considere que o idoso pode ter poucos recursos. Priorize soluções caseiras, criativas, gratuitas ou via SUS. Evite sugerir compras caras.
    
    SUA BASE CIENTÍFICA (RIGOROSA):
    - Use APENAS dados de 2020 a {ano_atual}.
    - Cite artigos de Revistas Nacionais ou Internacionais de Alto Fator de Impacto (ex: The Lancet, JAMA, Cadernos de Saúde Pública, Nature Aging).
    - OBRIGATÓRIO: Colocar o DOI ao final de cada citação científica.
    
    PERGUNTA DO USUÁRIO: '{msg}'
    
    ESTRUTURA DA RESPOSTA:
    1. 🧠 Acolhimento e Explicação Neurocientífica
    2. 💊 Alertas de Saúde/Medicamentos (Se couber)
    3. 💡 Dicas de Bem-Estar (Foco em baixo custo/criatividade)
    4. ⚖️ Direitos (Leis Atuais)
    5. 📚 Referências (Revista + Ano + DOI)
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