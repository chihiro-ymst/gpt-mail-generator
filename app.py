from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from openai import OpenAI
from flask_mail import Mail, Message
import os

# .envファイルから環境変数を読み込み
load_dotenv()

# OpenAIクライアントの初期化（sk-proj対応）
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__, template_folder='templates')

# === メール設定（Gmail） ===
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")
app.config['MAIL_DEFAULT_SENDER'] = os.getenv("MAIL_USERNAME")
mail = Mail(app)

# === ルーティング ===

@app.route('/')
def index():
    return render_template('top.html')

@app.route('/index')
def index_redirect():
    return render_template('index.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/coming-soon')
def coming_soon():
    return render_template('coming_soon.html')

from email.header import Header

@app.route('/how-to')
def how_to():
    return render_template('how_to.html')

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "GET":
        return render_template("contact.html")

    try:
        name = request.form.get("name", "名無し")
        email = request.form.get("email", "")
        message = request.form.get("message", "")

        msg = Message(
            subject=f"お問い合わせ from {name}",
            sender=email,
            recipients=["chihiro.ymst.create@gmail.com"],  # ← あなたの受信用メールに変更してね
            body=message,
            charset='utf-8'  # ★ 日本語文字化け対策
        )
        mail.send(msg)
        return "送信が完了しました。ありがとうございます！"

    except Exception as e:
        print(f"❌ メール送信エラー: {e}")
        return "送信に失敗しました。時間をおいて再度お試しください。", 500


@app.route('/complaint')
def complaint():
    return render_template('complaint.html')

@app.route('/generate_complaint', methods=['POST'])
def generate_complaint():
    try:
        data = request.json
        print("🟡 受信データ:", data)

        recipient = data.get("recipient", "")
        sender = data.get("sender", "")
        details = data.get("details", "")
        response_text = data.get("response", "")
        tone = data.get("tone", "")
        tone_instruction = ""

        if tone == "丁寧に謝罪":
            tone_instruction = "非常に丁寧な謝罪のトーンで書いてください。"
        elif tone == "事実を重視":
            tone_instruction = "トラブル回避を意識し、事実を重視した冷静なトーンで書いてください。"
        elif tone == "柔らかめに対応":
            tone_instruction = "相手に配慮した柔らかいトーンで書いてください。"

        user_message = f"""
以下の条件で、クレーム対応のビジネスメールを作成してください。

- 宛名：「{recipient}」
- 差出人（署名）：「{sender}」
- クレームの内容：「{details}」
- 対応内容：「{response_text}」
- {tone_instruction}
"""

        res = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "あなたは丁寧なビジネスメールを生成するアシスタントです。常に、宛名には相手の名前を拝啓　（recipient）を使い、、文末の署名には自分の名前（sender）を入れて敬具をつけてください。"},
                {"role": "user", "content": user_message}
            ]
        )

        reply = res.choices[0].message.content.strip()
        return jsonify({"email": reply})

    except Exception as e:
        print("❌ エラー:", e)
        return jsonify({"error": "生成中にエラーが発生しました"}), 500

@app.route('/business')
def business():
    return render_template('business.html')

@app.route('/generate_business', methods=['POST'])
def generate_business():
    try:
        data = request.json
        print("🟡 ビジネスメール入力データ:", data)

        recipient = data.get("recipient", "").strip()
        sender = data.get("sender", "").strip()
        subject = data.get("subject", "").strip()
        greeting = data.get("greeting", "").strip()
        body = data.get("body", "").strip()
        closing = data.get("closing", "").strip()

        user_message = f"""
以下の要素を使って、自然で丁寧なビジネスメールを作成してください。

・宛名：{recipient}
・件名：{subject}
・挨拶文：{greeting}
・本文：{body}
・結びの言葉：{closing}
・署名：{sender}

丁寧で信頼感のある文章に整え、日本語のビジネスマナーに沿って、自然な流れで構成してください。
"""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "あなたは日本語ビジネスメールを丁寧に書くアシスタントです。"},
                {"role": "user", "content": user_message}
            ]
        )

        reply = response.choices[0].message.content.strip()
        return jsonify({"email": reply})

    except Exception as e:
        print("❌ エラー:", e)
        return jsonify({"error": "生成中にエラーが発生しました"}), 500

@app.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.json
        print("🟡 フォームデータ:", data)

        recipient = data.get('recipient', '').strip()
        sender = data.get('sender', '').strip()
        dates = data.get('dates', '').strip()
        place = data.get('place', '').strip()
        memo = data.get('memo', '').strip()

        user_message = f"""{recipient}
お世話になっております。
{sender}です。
以下日程にて面談候補をお送りします。
{dates}"""
        if place:
            user_message += f"\n場所：{place}"
        if memo:
            user_message += f"\n{memo}"

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "あなたはビジネスメールの作成を手伝うアシスタントです。"},
                {"role": "user", "content": user_message}
            ]
        )

        reply = response.choices[0].message.content.strip()
        return jsonify({"email": reply})

    except Exception as e:
        print("❌ エラー:", e)
        return jsonify({"error": "生成中にエラーが発生しました"}), 500

# === アプリ起動 ===
if __name__ == '__main__':
    app.run(debug=True, port=5000)
