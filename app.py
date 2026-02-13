import os
from decimal import Decimal, InvalidOperation
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
import stripe

load_dotenv()

app = Flask(__name__)

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

def _parse_amount_to_cents(amount_raw: str) -> int:
    amount = Decimal(amount_raw).quantize(Decimal("0.01"))
    return int(amount * 100)

@app.get("/")
def index():
    return render_template(
        "index.html",
        publishable_key=os.getenv("STRIPE_PUBLISHABLE_KEY"),
    )

@app.post("/create-payment-intent")
def create_payment_intent():
    data = request.get_json() or {}
    amount_raw = data.get("amount")
    payment_method_id = data.get("payment_method_id")
    email = data.get("email")

    amount_cents = _parse_amount_to_cents(amount_raw)

    try:
        intent = stripe.PaymentIntent.create(
            amount=amount_cents,
            currency="usd",
            payment_method=payment_method_id,
            confirm=True,
            receipt_email=email or None,
            payment_method_types=["card"],
            error_on_requires_action=True,
        )
        return jsonify({"status": "true", "pi_id": intent.id})

    except stripe.error.CardError as e:
        err = e.error
        return jsonify({
            "status": "declined",
            "code": err.code,
            "decline_code": err.decline_code,
            "message": err.message
        }), 402

if __name__ == "__main__":
    app.run()