from flask import Flask, request, abort
import os
import openai
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

# 環境変数から読み込み（RenderのEnvironment Variablesで設定）
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # ← OpenAIのキーもRenderに登録してね！

# 初期化
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)
openai.api_key = OPENAI_API_KEY

# Flaskアプリ作成
app = Flask(__name__)

# Webhookのエンドポイント
@app.route("/callback", methods=['POST'])
def callback():
    # 署名の取得と検証
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

# LINEのメッセージ受信時の処理
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text

    # OpenAI ChatGPT APIへリクエスト
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # 必要に応じて gpt-4 に変更も可（課金必要）
            messages=[
                {"role": "system", "content": "あなたは親切な英会話教師です。"},
                {"role": "user", "content": user_message}
            ]
        )
        reply = response.choices[0].message['content'].strip()
    except Exception as e:
        reply = "ごめん、ちょっとエラーが出たみたい💦"

    # LINEに返信
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply)
    )

# Renderでの起動ポイント
if __name__ == "__main__":
    app.run()

