from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import os

app = Flask(__name__)

API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY não configurada")
genai.configure(api_key=API_KEY)

model = genai.GenerativeModel(
    model_name="models/gemini-1.5-flash",
    system_instruction=(
        "Sou a Verena, especialista em anatomia, neurociência e direito. "
        "Se o usuário usar termos infantilizados como 'vozinha', "
        "devo educar gentilmente sobre a importância de chamar de Senhora ou pelo nome, "
        "preservando a autonomia e dignidade da pessoa idosa."
    )
)

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    try:
        user_message = request.form.get("message", "").strip()
        image_file = request.files.get("image")

        parts = []

        if user_message:
            parts.append(user_message)

        if image_file:
            parts.append({
                "mime_type": image_file.mimetype,
                "data": image_file.read()
            })

        if not parts:
            return jsonify({"response": "Nenhuma mensagem recebida."}), 400

        response = model.generate_content(parts)

        return jsonify({"response": response.text})

    except Exception as e:
        print("Erro:", e, flush=True)
        return jsonify({"response": f"Erro técnico: {str(e)}"}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
