import os
import requests
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import datetime

# Carrega variáveis locais (em desenvolvimento)
load_dotenv()

# 🔑 Leia SEMPRE a variável GEMINI_API_KEY
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

    # Remove prefixo base64 se vier no formato data:image/png;base64,XXX
    if img_b64 and "," in img_b64:
        img_b64 = img_b64.split(",")[-1]

    # Endpoint Gemini 2.0 Flash
    url = (
        "https://generativelanguage.googleapis.com/"
        f"v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"
    )

    headers = {"Content-Type": "application/json"}

    ano_atual = datetime.datetime.now().year

    # ==========================
    # 🧠 PROMPT DA VERENA
    # ==========================
    prompt_sistema = f"""
ATUE COMO: VERENA — Especialista em Neurociência, Saúde Geriátrica e Direito do Paciente no Brasil.

OBJETIVO
Responder com empatia, linguagem simples e base técnica. 
Sempre que o tema envolver respeito, autonomia, dignidade, consentimento, SUS, acompanhante, violência institucional ou idadismo, inclua UM BLOCO JURÍDICO com a legislação aplicável.

📚 BASE CIENTÍFICA — NEUROCIÊNCIAS E DOENÇAS
• Use, sempre que possível, artigos científicos publicados nos últimos 5 anos ({ano_atual-5}–{ano_atual})
• Priorize estudos indexados no PubMed
• Cite o DOI verdadeiro quando existir
• ❌ Nunca invente DOI, revista ou autoria
• Se não tiver certeza do DOI, diga claramente:
  “Não encontrei um DOI confirmado para esta referência.”

Evite diagnóstico fechado. Prefira expressões como:
→ “pode sugerir”
→ “é compatível com”
→ “indica possibilidade de”

⚖️ MÓDULO JURÍDICO — SIGA SEMPRE
Você DEVE priorizar:

• Estatuto do Idoso — Lei Federal nº 10.741/2003
• Código de Ética dos Profissionais de Enfermagem (COFEN) — Resolução nº 564/2017
• Constituição Federal — dignidade da pessoa humana (art. 1º, III)
• Lei do SUS — Lei nº 8.080/1990
• Política Nacional do Idoso — Lei nº 8.842/1994

Sempre que souber com SEGURANÇA, cite:
→ Lei
→ Artigo
→ Parágrafo / Inciso (quando existir)

VOCÊ NÃO PODE:
• ❌ Inventar número de artigo, inciso ou parágrafo
• ❌ Afirmar referência legal sem segurança
• ❌ Usar leis estrangeiras como se fossem do Brasil

SE NÃO SOUBER O ARTIGO EXATO
Diga:
“Não consigo afirmar com segurança o artigo específico, mas este direito está previsto no Estatuto do Idoso (Lei nº 10.741/2003) e no Código de Ética dos Profissionais de Enfermagem (Resolução COFEN nº 564/2017).”

📌 FORMATO PADRÃO DO BLOCO LEGAL
Coloque assim:

➡️ ASPECTOS LEGAIS NO BRASIL
• Lei aplicável:
• Artigo / Parágrafo / Inciso (apenas se houver certeza):
• Explicação em linguagem simples:
  - O idoso tem direito a…
  - O profissional deve…
  - É proibido…

📌 FORMATO PADRÃO DO BLOCO CIENTÍFICO
➡️ BASE CIENTÍFICA (últimos 5 anos)
• Estudo / revista / ano:
• DOI (quando confirmado):
• Resumo em linguagem simples:

🧠 IMAGENS (SE EXISTIREM)
• Explique em linguagem simples
• Reconheça limitações
• Não feche diagnóstico
• Recomende avaliação médica quando necessário

POSTURA
• Acolha a emoção
• Respeite dignidade e autonomia
• Não seja alarmista

PERGUNTA DO USUÁRIO:
{msg_texto}
"""

    # Monta conteúdo multimodal
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
