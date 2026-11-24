# Rojak Wardrobe HTML website

Run from this folder:

```powershell
python web_app.py
```

Open `http://127.0.0.1:8765` in a browser. The Python standard-library server serves `web/index.html`, `web/styles.css`, and `web/app.js`, and runs the chatbot API. The existing `data/dataset.csv` and `nlp_engine.py` provide the 450 review records and TF-IDF retrieval. No additional web framework is required. The original Streamlit files remain for comparison.

## What the chatbot does

- Understands common English, Malay and mixed terms for fit, fabric, stitching, colour and delivery.
- Retrieves relevant reviews and gives a question-specific English response with original review excerpts.
- Checks two fictional order records when the customer provides an order or parcel code.
- Attaches a removable product card when a customer chooses **Ask about collection**. The order card is attached only from an order detail page. The chosen card is passed to the chatbot with the next message and can be removed with **×** before sending.
- Shows a fresh greeting and quick questions when chat is first opened or reopened after 30 minutes.
- Accepts corrections in chat and stores them in `web_feedback.jsonl` for review. Corrections are not automatically treated as verified facts.
- Records microphone audio with live sound-responsive bars, shows an interim transcript when browser speech recognition is supported, and offers playback of the captured clip before sending. The transcript is added to the message box only when the customer chooses **Use transcript in message**. Speech recognition accuracy for mixed language varies by browser.

Product cards, prices, orders and return policy are classroom simulations. The website now presents a women's Baju Kurung and kurta collection. The existing review dataset describes Baju Melayu/kurta garments and does not identify these women's styles, so the chatbot does not claim that the reviews verify fit for a specific women's cut. The website runs locally; it has not been published to a hosting service.

Add your images using the filenames in [web/assets/README.md](web/assets/README.md). Until an image is supplied, product cards use the built-in garment illustrations and the header uses the text logo.
