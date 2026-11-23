# Rojak Wardrobe shop simulation

Run from this project directory:

```powershell
pip install -r requirements.txt
streamlit run shop_app.py
```

The original `app.py` is retained. `shop_app.py` adds a fictional clothes-shop storefront, two demo orders, a full-width customer-support messenger, a greeting with suggested questions, review evidence, voice input, and a correction form. Customer messages appear on the right and bot messages on the left.

The chat has a Back button. Opening support from an order places the order code in the message box and asks what the customer wants to know. The customer can edit the message before sending. The initial greeting appears when chat history is empty and again when support is reopened after more than 30 minutes.

`data/dataset.csv` is the supplied 450-review Baju Melayu dataset. Its reviews describe the collection generally; they do not identify the individual demo products. Product names, prices, order codes, tracking events, and shop policies are simulated. The chatbot answers product questions from retrieved reviews and order questions from the two in-app mock records.

Saved corrections go to `shop_feedback.csv` for review. They do not automatically change the answer model.
