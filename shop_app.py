"""Streamlit clothes-shop simulation backed by the project's Rojak reviews."""

from __future__ import annotations

import csv
from datetime import date, datetime, timedelta
from io import BytesIO
from pathlib import Path
import re
import html

import streamlit as st

from nlp_engine import ReviewAssistant, load_reviews


ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "dataset.csv"
FEEDBACK = ROOT / "shop_feedback.csv"

# The source reviews have no product identifier. These are fictional storefront
# records for a class demonstration, not facts inferred from the reviews.
PRODUCTS = [
    {"id": "BM-101", "name": "Baju Melayu Classic", "colour": "Midnight Navy", "price": 89.00, "icon": "👔", "tag": "Best seller", "description": "A traditional look for celebrations and family gatherings."},
    {"id": "BM-102", "name": "Baju Melayu Modern", "colour": "Sage Green", "price": 99.00, "icon": "🧥", "tag": "New arrival", "description": "A clean, contemporary cut for everyday occasions."},
    {"id": "BM-103", "name": "Baju Kurta Essential", "colour": "Warm Sand", "price": 79.00, "icon": "👕", "tag": "Everyday wear", "description": "An easygoing style for casual outings."},
]
ORDERS = [
    {"id": "RJ-261120-1042", "tracking": "MYX782641905", "product": "Baju Melayu Classic", "variant": "Midnight Navy · M", "quantity": 1, "total": 89.00, "date": "20 Nov 2026", "status": "In transit", "eta": "25 Nov 2026", "events": ["Order placed", "Packed by demo shop", "Handed to demo courier", "In transit"]},
    {"id": "RJ-241102-2078", "tracking": "MYX913578204", "product": "Baju Kurta Essential", "variant": "Warm Sand · L", "quantity": 1, "total": 79.00, "date": "02 Nov 2026", "status": "Delivered", "eta": "Delivered 06 Nov 2026", "events": ["Order placed", "Packed by demo shop", "Handed to demo courier", "Delivered"]},
]
SUGGESTIONS = [
    "Saiz baju ni accurate ke?",
    "Kain dia panas tak?",
    "Jahitan okay tak?",
    "Where is my order?",
]
FAQ = {
    "returns": "For this demo shop, request a return within 7 days of delivery if the item is unused and still has its tags. This is a simulated policy, not a real seller policy.",
    "shipping": "This demo shop offers standard delivery. For an order already placed, I can show its simulated tracking status if you provide its order or parcel code.",
    "sizes": "The demo catalogue lists sizes S, M, L and XL. I don't have a verified size chart, but I can share what customers said about fit in the review collection.",
}

st.set_page_config(page_title="Rojak Wardrobe · Shop & Chat", page_icon="🛍️", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@600;700&display=swap');
html, body, [class*="css"], .stApp {font-family:'DM Sans',sans-serif;color:#26392f}
.stApp {background:#f7f5ef}
header[data-testid="stHeader"] {background:transparent}
.block-container {max-width:1320px;padding-top:1.3rem;padding-bottom:4rem}
h1,h2,h3 {font-family:'Playfair Display',serif;color:#173a2d}
.brand {font-family:'Playfair Display',serif;font-size:1.85rem;font-weight:700;color:#173a2d;letter-spacing:-.04em}
.eyebrow {font-size:.78rem;text-transform:uppercase;letter-spacing:.18em;color:#8d6b45;font-weight:700}
.hero {background:linear-gradient(115deg,#143c2d,#295d44);border-radius:24px;padding:3rem 3.2rem;color:#fff;margin:1.5rem 0 2rem;min-height:260px}
.hero h1 {color:#fff;font-size:3rem;margin:.45rem 0}.hero p{font-size:1.08rem;max-width:560px;color:#e6eee6}
.card {background:#fff;border:1px solid #e7e4db;border-radius:18px;padding:1.4rem;box-shadow:0 7px 24px rgba(23,58,45,.045);min-height:150px}
.product-art {height:175px;background:linear-gradient(135deg,#e7e7dc,#d4decf);border-radius:14px;display:flex;align-items:center;justify-content:center;font-size:5rem;margin-bottom:1rem}
.product-name {font-family:'Playfair Display',serif;font-size:1.28rem;font-weight:700}.muted {color:#6b746b;font-size:.92rem}
.price {font-size:1.15rem;font-weight:700;color:#173a2d}.pill {display:inline-block;padding:.26rem .7rem;border-radius:20px;background:#e5efe7;color:#236043;font-size:.78rem;font-weight:700}
.order-code {font-family:monospace;background:#eff3ed;border-radius:8px;padding:.22rem .45rem;color:#1f5640}
.chat-header {background:#173a2d;color:white;border-radius:18px;padding:1.15rem 1.4rem;margin-bottom:.75rem}
.chat-header strong {font-size:1.15rem}.chat-header small {display:block;color:#c8ddd1;margin-top:.2rem}
.profile-box {background:#fff;border:1px solid #e7e4db;border-radius:18px;padding:1.25rem;margin-bottom:1rem}
.profile-avatar {font-size:2.2rem}.note {background:#fff6e9;border-left:4px solid #d6a661;padding:.75rem 1rem;border-radius:8px;color:#71532f}
.section-gap {height:1.2rem}
.message-row {display:flex;gap:.65rem;align-items:flex-end;margin:.9rem 0}
.message-row.customer {justify-content:flex-end}
.message-avatar {width:36px;height:36px;min-width:36px;border-radius:50%;background:#e4eee7;display:flex;align-items:center;justify-content:center}
.message-bubble {max-width:76%;padding:.85rem 1rem;border-radius:17px;background:#fff;border:1px solid #e4e6dc;box-shadow:0 2px 8px rgba(23,58,45,.035);line-height:1.5;white-space:normal}
.customer .message-bubble {background:#d9f1df;border-color:#c8e8d0;border-bottom-right-radius:4px}
.assistant .message-bubble {border-bottom-left-radius:4px}
.chat-shell {background:#fbfcf9;border:1px solid #e3e7df;border-radius:18px;padding:.6rem 1rem}
.chat-compose-label {color:#758178;font-size:.82rem;margin-top:.7rem}
div.stButton>button[kind="primary"] {background:#1b6045;border-color:#1b6045;border-radius:10px}
div.stButton>button {border-radius:10px;min-height:2.55rem}
div[data-testid="stVerticalBlock"] > div {margin-bottom:.15rem}
</style>""", unsafe_allow_html=True)


@st.cache_resource(show_spinner=False)
def get_assistant():
    return ReviewAssistant(load_reviews(DATA))


def init_state():
    st.session_state.setdefault("page", "Shop")
    st.session_state.setdefault("chat_open", False)
    st.session_state.setdefault("chat_return_page", "Shop")
    st.session_state.setdefault("chat_draft", "")
    st.session_state.setdefault("last_chat_at", None)
    st.session_state.setdefault("messages", [])
    st.session_state.setdefault("customer_name", "Aina Rahman")


def open_chat(order_id=None, product_name=None):
    if not st.session_state.chat_open:
        st.session_state.chat_return_page = st.session_state.page
    st.session_state.chat_open = True
    st.session_state.page = "Shop"
    now = datetime.now()
    last = st.session_state.last_chat_at
    if not st.session_state.messages or last is None or now - last > timedelta(minutes=30):
        st.session_state.messages.append({"role": "assistant", "content": "Hi Aina! 👋 Welcome to Rojak Wardrobe. What can I help you with today? You can ask in English, BM or Rojak.", "quick_replies": True})
    if order_id:
        st.session_state.chat_draft = f"Order ID: {order_id} — "
        st.session_state.messages.append({"role": "assistant", "content": f"Do you want to ask about **{product_name or 'this order'}**? I've put order code **{order_id}** in your message box. Add your question and press Send."})
    st.session_state.last_chat_at = now
    st.rerun()


def find_order(text):
    upper = text.upper()
    return next((order for order in ORDERS if order["id"] in upper or order["tracking"] in upper), None)


def answer_question(question, assistant):
    # A linked order is context. It should not change the topic of a product question.
    user_wording = re.sub(r"\s*\(Order ID: [^)]+\)\s*$", "", question, flags=re.I)
    has_prefilled_code = bool(re.match(r"^Order ID:\s*[A-Z0-9-]+\s*[—-]", user_wording, flags=re.I))
    user_wording = re.sub(r"^Order ID:\s*[A-Z0-9-]+\s*[—-]\s*", "", user_wording, flags=re.I)
    q = user_wording.lower()
    order = find_order(question)
    asks_order = bool(re.search(r"order|parcel|tracking|track|pesanan|belianku|barang.*(mana|sampai)|where.*package|status", q)) or bool(find_order(user_wording)) or (has_prefilled_code and not q)
    if order and asks_order:
        return (f"I found your demo order **{order['id']}** for **{order['product']} ({order['variant']})**. "
                f"Status: **{order['status']}**. Parcel code: `{order['tracking']}`. {order['eta']}.", [])
    if re.search(r"refund|return|pulangan|pulang|bayaran balik|tukar barang", q):
        return FAQ["returns"], []
    if re.search(r"shipping option|delivery option|courier|penghantaran apa|pos apa", q):
        return FAQ["shipping"], []
    if re.search(r"size chart|size guide|carta saiz", q):
        return FAQ["sizes"], []
    if asks_order:
        return ("I can check a demo order for you. Please paste the **order ID** or **parcel code** shown in My Orders. I can't access real courier systems.", [])
    result = assistant.answer(user_wording, top_k=5)
    if not result["evidence"]:
        return ("I couldn't find enough evidence for that in the Baju Melayu reviews. Ask about fabric, fit, stitching, colour or delivery experience, or give me a demo order code.", [])
    # The existing engine summarises themes in English and supplies original reviews.
    return result["answer"], result["evidence"]


def send_message(question, assistant):
    question = question.strip()
    if not question:
        return
    st.session_state.messages.append({"role": "user", "content": question})
    answer, evidence = answer_question(question, assistant)
    st.session_state.messages.append({"role": "assistant", "content": answer, "evidence": evidence})
    st.session_state.last_chat_at = datetime.now()


def send_draft(assistant):
    question = st.session_state.chat_draft.strip()
    if question:
        send_message(question, assistant)
        st.session_state.chat_draft = ""


def message_html(content):
    safe = html.escape(content)
    safe = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", safe)
    safe = re.sub(r"`([^`]+)`", r"<code>\1</code>", safe)
    return safe.replace("\n", "<br>")


def show_header():
    left, nav1, nav2, nav3, support = st.columns([3.2, 1, 1.1, 1.25, 1.5], vertical_alignment="center")
    with left:
        st.markdown('<div class="brand">✦ Rojak Wardrobe</div><div class="muted">Malaysian style, made easy</div>', unsafe_allow_html=True)
    for col, label in [(nav1, "Shop"), (nav2, "My Orders"), (nav3, "About")]:
        with col:
            if st.button(label, key=f"nav_{label}", use_container_width=True):
                st.session_state.page = label
                st.session_state.chat_open = False
                st.rerun()
    with support:
        if st.button("💬 Customer support", type="primary", use_container_width=True):
            open_chat()
    st.divider()


def show_store():
    st.markdown('<div class="hero"><div class="eyebrow" style="color:#d4b883">Everyday heritage collection</div><h1>Dress well. Ask anything.</h1><p>Explore our demo Baju Melayu collection and ask our assistant about real customer review experiences in English, BM or Rojak.</p></div>', unsafe_allow_html=True)
    st.markdown("## Featured collection")
    st.caption("Demo products and prices. Reviews in the dataset refer to the Baju Melayu collection as a whole, not individual items below.")
    cols = st.columns(3, gap="large")
    for col, product in zip(cols, PRODUCTS):
        with col:
            st.markdown(f'<div class="card"><div class="product-art">{product["icon"]}</div><span class="pill">{product["tag"]}</span><div class="product-name">{product["name"]}</div><div class="muted">{product["colour"]}</div><p class="muted">{product["description"]}</p><div class="price">RM {product["price"]:.2f}</div></div>', unsafe_allow_html=True)
            st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)
            if st.button("Ask about this collection", key=f"ask_{product['id']}", use_container_width=True):
                open_chat()
    st.write("")
    st.info("💬 Wondering about the fabric, size or stitching? Open customer support to ask in your own words.")


def show_orders():
    st.markdown("# My Orders")
    st.caption("These are fictional orders for the classroom shop simulation.")
    for order in ORDERS:
        st.markdown(f'<div class="card"><span class="pill">{order["status"]}</span><h3>{order["product"]}</h3><div class="muted">{order["variant"]} · Qty {order["quantity"]} · Ordered {order["date"]}</div><p>Order ID: <span class="order-code">{order["id"]}</span><br>Parcel code: <span class="order-code">{order["tracking"]}</span></p><strong>RM {order["total"]:.2f}</strong></div>', unsafe_allow_html=True)
        st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)
        a, b, c = st.columns([1.4, 1.4, 3])
        with a:
            if st.button("View order", key=f"view_{order['id']}", use_container_width=True):
                st.session_state.page = f"order:{order['id']}"
                st.rerun()
        with b:
            if st.button("Customer support", key=f"support_{order['id']}", use_container_width=True):
                open_chat(order["id"], order["product"])
        with c:
            st.caption("Copy the order or parcel code displayed above when asking for help.")
        st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)


def show_order_detail(order):
    if st.button("← Back to orders"):
        st.session_state.page = "My Orders"
        st.rerun()
    st.markdown(f"# Order {order['id']}")
    st.markdown(f'<div class="card"><span class="pill">{order["status"]}</span><h3>{order["product"]}</h3><p>{order["variant"]} · Quantity {order["quantity"]}</p><p>Order ID: <span class="order-code">{order["id"]}</span><br>Parcel code: <span class="order-code">{order["tracking"]}</span></p><p>Estimated delivery / result: <strong>{order["eta"]}</strong></p><strong>Total RM {order["total"]:.2f}</strong></div>', unsafe_allow_html=True)
    code_a, code_b = st.columns(2)
    with code_a:
        st.caption("Copy order ID")
        st.code(order["id"], language=None)
    with code_b:
        st.caption("Copy parcel code")
        st.code(order["tracking"], language=None)
    st.markdown("### Order journey")
    for event in order["events"]:
        st.write("✓", event)
    if st.button("💬 Ask customer support about this order", type="primary"):
        open_chat(order["id"], order["product"])


def show_chat(assistant):
    back, heading = st.columns([1.2, 8], vertical_alignment="center")
    with back:
        if st.button("← Back", use_container_width=True):
            st.session_state.chat_open = False
            st.session_state.page = st.session_state.chat_return_page
            st.rerun()
    with heading:
        st.markdown("### Customer support")
    st.markdown('<div class="chat-header"><strong>✦ Rojak Assistant</strong><small>● Online · Ask in English, BM or Rojak</small></div>', unsafe_allow_html=True)
    st.caption("Product experiences come from customer reviews. Orders and shop policies are part of this demo.")

    with st.container(height=520, border=True):
        messages = st.session_state.messages
        last_greeting = max((i for i, msg in enumerate(messages) if msg.get("quick_replies")), default=-1)
        show_quick_replies = last_greeting >= 0 and not any(msg["role"] == "user" for msg in messages[last_greeting + 1:])
        for idx, msg in enumerate(messages):
            role = msg["role"]
            avatar = '<div class="message-avatar">🛍️</div>' if role == "assistant" else '<div class="message-avatar">👤</div>'
            bubble = f'<div class="message-bubble">{message_html(msg["content"])}</div>'
            inner = avatar + bubble if role == "assistant" else bubble + avatar
            st.markdown(f'<div class="message-row {"assistant" if role == "assistant" else "customer"}">{inner}</div>', unsafe_allow_html=True)
            if idx == last_greeting and show_quick_replies:
                st.caption("Common questions · tap one to send")
                prompt_cols = st.columns(2)
                for i, suggestion in enumerate(SUGGESTIONS):
                    with prompt_cols[i % 2]:
                        if st.button(suggestion, key=f"suggest_{idx}_{i}", use_container_width=True):
                            send_message(suggestion, assistant)
                            st.rerun()
            if msg.get("evidence"):
                with st.expander(f"See {len(msg['evidence'])} supporting reviews"):
                    for hit in msg["evidence"]:
                        st.write(f"{hit['rating']}★ · {hit['review']}")

    st.markdown('<div class="chat-compose-label">MESSAGE</div>', unsafe_allow_html=True)
    input_col, send_col = st.columns([8, 1.2], vertical_alignment="bottom")
    with input_col:
        st.text_input("Message", key="chat_draft", label_visibility="collapsed", placeholder="Type your message in English, BM or Rojak…", on_change=send_draft, args=(assistant,))
    with send_col:
        st.button("Send ➤", type="primary", use_container_width=True, on_click=send_draft, args=(assistant,))

    with st.expander("🎙️ Voice message"):
        audio = st.audio_input("Record a question")
        language = st.selectbox("Speech language", ["ms-MY", "en-US"], help="Code switching may be transcribed imperfectly.")
        if audio and st.button("Transcribe and send", key="send_audio"):
            try:
                import speech_recognition as sr
                recognizer = sr.Recognizer()
                with sr.AudioFile(BytesIO(audio.getvalue())) as source:
                    heard = recognizer.record(source)
                spoken = recognizer.recognize_google(heard, language=language)
                send_message(spoken, assistant)
                st.rerun()
            except Exception as exc:
                st.error(f"Could not transcribe this recording: {exc}")
    with st.expander("✍️ Correct an answer"):
        with st.form("feedback_form", clear_on_submit=True):
            original = st.text_input("Your question")
            correction = st.text_area("What should the assistant have answered?")
            if st.form_submit_button("Save correction"):
                if original.strip() and correction.strip():
                    with FEEDBACK.open("a", newline="", encoding="utf-8") as f:
                        writer = csv.DictWriter(f, fieldnames=["date", "question", "corrected_answer", "order_mentioned"])
                        if f.tell() == 0:
                            writer.writeheader()
                        found_order = find_order(original)
                        writer.writerow({"date": date.today().isoformat(), "question": original.strip(), "corrected_answer": correction.strip(), "order_mentioned": found_order["id"] if found_order else ""})
                    st.success("Correction saved for review. It is not applied automatically.")
                else:
                    st.warning("Please enter both the question and corrected answer.")


init_state()
show_header()
if not DATA.exists():
    st.error("Missing data/dataset.csv. Add the review dataset from the supplied project ZIP.")
    st.stop()
assistant = get_assistant()
if st.session_state.chat_open:
    show_chat(assistant)
elif st.session_state.page == "My Orders":
    show_orders()
elif st.session_state.page.startswith("order:"):
    selected = next((o for o in ORDERS if o["id"] == st.session_state.page.removeprefix("order:")), None)
    show_order_detail(selected) if selected else show_orders()
elif st.session_state.page == "About":
    st.markdown("# About this demo")
    st.write("Rojak Wardrobe is a fictional clothes shop built for an NLP class prototype. Product questions retrieve evidence from 450 customer reviews of a Baju Melayu collection. Order history, tracking, prices and policies are simulated.")
    st.write("The assistant supports English, Malay and mixed questions through word and character TF-IDF retrieval. Voice transcription requires internet access. Saved answer corrections require review before being incorporated.")
else:
    show_store()
