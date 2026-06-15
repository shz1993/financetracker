import os
from groq import Groq
import streamlit as st
import pandas as pd

def get_ai_insights(transactions_df, period="monthly"):
    """Get AI insights from transaction data using Groq"""
    
    # Prepare summary stats
    total_income = transactions_df[transactions_df['type'] == 'income']['amount'].sum()
    total_expense = transactions_df[transactions_df['type'] == 'expense']['amount'].sum()
    savings = total_income - total_expense
    saving_rate = (savings / total_income * 100) if total_income > 0 else 0
    
    # Get top spending categories
    expense_df = transactions_df[transactions_df['type'] == 'expense']
    if not expense_df.empty:
        top_categories = expense_df.groupby('category_name')['amount'].sum().sort_values(ascending=False).head(3)
        top_cats_str = ", ".join([f"{cat}: Rp{amount:,.0f}" for cat, amount in top_categories.items()])
    else:
        top_cats_str = "No expenses recorded"
    
    # Get daily average spending
    days = transactions_df['date'].nunique() if not transactions_df.empty else 1
    avg_daily = total_expense / days if days > 0 else 0
    
    # Sample transactions for context
    recent = transactions_df.head(5).to_dict('records') if not transactions_df.empty else []
    
    # Create prompt for Groq
    prompt = f"""
    You are a personal finance advisor. Analyze this user's spending and provide insights.

    DATA SUMMARY:
    - Period: {period}
    - Total Income: Rp{total_income:,.0f}
    - Total Expenses: Rp{total_expense:,.0f}
    - Savings: Rp{savings:,.0f}
    - Saving Rate: {saving_rate:.1f}%
    - Average Daily Spending: Rp{avg_daily:,.0f}
    - Top Spending Categories: {top_cats_str}

    TASK:
    Provide 3 personalized saving tips based on their spending pattern.
    Make the tips specific, actionable, and friendly.

    Format your response as:
    1. [Tip 1]
    2. [Tip 2]
    3. [Tip 3]
    """
    
    try:
        client = Groq(
    api_key=st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY")),
    proxy=None  # Menonaktifkan proxy
)
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a friendly, helpful personal finance advisor. Be concise and practical."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500,
        )
        insights = response.choices[0].message.content.strip()
        return insights
    except Exception as e:
        return f"⚠️ AI insights temporarily unavailable: {str(e)}\n\n**Quick Tips:**\n1. Track every expense\n2. Aim for 20% savings rate\n3. Review subscriptions monthly"

def suggest_budget(tips):
    """Convert AI tips to budget suggestions"""
    return tips