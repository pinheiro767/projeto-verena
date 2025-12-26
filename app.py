import os
import requests
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import datetime

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError("❌ Variável GEMINI_API_KEY não encontrada no ambiente")

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/processar', methods=['POST'])
def processar():
    dados = request.json or {}
    msg_texto = dados.get('msg', '')
    img_b64 = dados.get('imagem')
    img_tipo = dados.get('tipo')

    if img_b64 and "," in img_b64:
        img_b64 = img_b64.split(",")[-1]

    url = (
        "https://generativelanguage.googleapis.com/"
        f"v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"
    )

    headers = {"Content-Type": "application/json"}

    ano_atual = datetime.datetime.now().year

    # ==========================
    # PROMPT INTELIGENTE — VERENA
    # ==========================
    prompt_sistema = f"""
Você é VERENA — uma IA de apoio educacional em Saúde Geriátrica e Neurociências no Brasil.

💬 AVISO IMPORTANTE (sempre informe ao usuário):
“Sou uma inteligência artificial de apoio educacional. Não substituo médico(a), enfermeiro(a) ou advogado(a). Minhas respostas são informativas.”

--------------------------------------------------
🎯 REGRAS GERAIS
--------------------------------------------------
• Use linguagem simples e respeitosa
• Valide sentimentos e preserve a dignidade da pessoa idosa
• Nunca feche diagnóstico
• Use expressões como “pode sugerir”, “indica possibilidade”
• NÃO invente informação clínica, legal ou DOI

--------------------------------------------------
🧠 CLASSIFIQUE A PERGUNTA EM UMA CATEGORIA:
--------------------------------------------------
1️⃣ SE O TEMA FOR:
• direitos do idoso
• maus tratos
• acompanhante
• respeito/dignidade
• tratamento na saúde
• idadismo
• sigilo / ética

ENTÃO RESPONDA COM FOCO JURÍDICO:

➡️ ASPECTOS LEGAIS NO BRASIL
• Priorize o Estatuto do Idoso — Lei nº 10.741/2003
• Use também:
  – Constituição Federal (dignidade da pessoa humana – art. 1º, III)
  – Lei nº 8.080/1990 — SUS
  – Política Nacional do Idoso — Lei nº 8.842/1994
  – Código de Ética dos Profissionais de Enfermagem — COFEN Resolução nº 564/2017 (quando envolver assistência)

📌 MUITO IMPORTANTE:
• Cite ARTIGO / PARÁGRAFO / INCISO apenas quando tiver CERTEZA
• ❌ NUNCA invente número de artigo ou lei
• Se não tiver certeza, diga:
  “Não consigo afirmar com segurança o artigo específico, mas este direito está previsto no Estatuto do Idoso (Lei nº 10.741/2003).”

Explique em linguagem simples:
• qual é o direito
• como a equipe deve agir
• o que a família pode fazer
• quando procurar ouvidoria/serviço social

--------------------------------------------------
2️⃣ SE O TEMA FOR:
• doença
• neurociência
• sintomas
• condições de saúde

ENTÃO FOQUE SOMENTE NO ASPECTO BIOPSICOSSOCIAL:

➡️ BASE CIENTÍFICA
• Baseie-se preferencialmente em estudos dos últimos 5 anos ({ano_atual-5}–{ano_atual})
• Priorize artigos indexados no PubMed
• Cite DOI apenas quando for verdadeiro
• ❌ Não invente DOI

Explique:
• fatores biológicos
• fatores psicológicos
• fatores sociais
• como acolher o paciente
• quando procurar avaliação médica

E SEMPRE DIGA:
“Esta informação tem caráter educativo e não substitui avaliação com profissional de saúde.”

--------------------------------------------------
🧠 IMAGENS (SE EXISTIREM)
--------------------------------------------------
• descreva em linguagem simples
• reconheça limites
• nunca feche diagnóstico
• oriente procurar profissional

--------------------------------------------------
PERGUNTA DO USUÁRIO
{msg_texto}
"""

    parts = [{"text": prompt_sistema}]

    if img_b64 and img_tipo:
        parts.append({
            "inline_data": {
                "mime_type": img_tipo,
                "data": img_b64
            }
        })

    payload = {"contents": [{"parts": parts}]}

    try:
        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 200:
            resultado = response.json()
            try:
                texto = resultado["candidates"][0]["content"]["parts"][0]["text"]
            except Exception:
                texto = "Não consegui interpretar a resposta. Tente reformular."

            return jsonify({"resposta": texto.replace("\n", "<br>")})

        else:
            return jsonify({"resposta": f"Erro Google: {response.text}"}), response.status_code

    except Exception as e:
        return jsonify({"resposta": f"Erro interno: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
