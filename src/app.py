import streamlit as st
import pandas as pd
import json
import ollama


def load_data():
    history = pd.read_csv("./data/historico_atendimento.csv")
    transactions = pd.read_csv("./data/transacoes.csv")

    with open("./data/perfil_investidor.json", "r", encoding="utf-8") as f:
        user_profile = json.load(f)

    with open("./data/produtos_financeiros.json", "r", encoding="utf-8") as f:
        financial_products = json.load(f)

    return history, transactions, user_profile, financial_products


def build_context(profile, transactions_df, history_df):
    context = f"""
    Client Data:
    - Name: {profile.get('nome')}
    - Profile: {profile.get('perfil')}
    - Available Balance: R$ {profile.get('saldo')}

    Latest Transactions:
    """
    for _, row in transactions_df.head(5).iterrows():
        context += f"- {row['data']}: {row['descricao']} - R$ {row['valor']}\n"

    context += "\nPrevious Interactions:\n"
    for _, row in history_df.head(3).iterrows():
        context += f"- {row['data']}: {row['interacao']}\n"

    return context


SYSTEM_PROMPT = """
You are Galgo, a digital financial agent.
Your mission is to help users monitor expenses, identify patterns, and send proactive alerts in a simple and accessible way.

Personality:
Relaxed
Polite
Calm

Communication Style:
Accessible
Informal
Avoid complex technical jargon, prefer clear and direct explanations.

Language Examples:
Greeting: "Hey, how’s it going?"
Confirmation: "Alright, I’ll check that out."
Error/Limitation: "I don’t have that info, but I can help with something else..."

Behavior Rules:
Always contextualize financial information in a practical and useful way.
Use simple examples to explain concepts.
Keep the tone friendly and approachable, without losing clarity.
When you don’t know something, acknowledge the limitation and offer alternatives.
"""


def main():
    st.title("💸 Galgo - Digital Financial Agent")
    st.write("Your assistant to monitor expenses and suggest financial recommendations.")

    history, transactions, user_profile, financial_products = load_data()
    context = build_context(user_profile, transactions, history)

    st.subheader("Current Client Context")
    st.text(context)

    user_message = st.text_input("Type your message to Galgo:")

    if st.button("Send"):
        response = ollama.chat(model="llama3", messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": context},
            {"role": "user", "content": user_message}
        ])
        st.markdown("### Galgo’s Response")
        st.write(response["message"]["content"])

if __name__ == "__main__":
    main()
