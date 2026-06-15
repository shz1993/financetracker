import os
import streamlit as st
import pandas as pd

def get_ai_insights(transactions_df, period="monthly"):
    """Get AI insights from transaction data"""
    
    if transactions_df.empty:
        return "Add some transactions to get AI insights!"
    
    # Prepare summary stats
    total_income = transactions_df[transactions_df['type'] == 'income']['amount'].sum()
    total_expense = transactions_df[transactions_df['type'] == 'expense']['amount'].sum()
    savings = total_income - total_expense
    saving_rate = (savings / total_income * 100) if total_income > 0 else 0
    
    # Get top spending categories
    expense_df = transactions_df[transactions_df['type'] == 'expense']
    if not expense_df.empty:
        top_categories = expense_df.groupby('category_name')['amount'].sum().sort_values(ascending=False).head(3)
        # Format dengan pemisah ribuan yang benar
        top_cats_str = ", ".join([f"{cat}: Rp{amount:,.0f}".replace(',', '.') for cat, amount in top_categories.items()])
    else:
        top_cats_str = "No expenses recorded"
    
    # Get daily average spending
    if not transactions_df.empty:
        days = transactions_df['date'].nunique()
        avg_daily = total_expense / days if days > 0 else 0
    else:
        avg_daily = 0
    
    # Format currency dengan pemisah titik
    income_str = f"Rp{total_income:,.0f}".replace(',', '.')
    expense_str = f"Rp{total_expense:,.0f}".replace(',', '.')
    avg_daily_str = f"Rp{avg_daily:,.0f}".replace(',', '.')
    
    # Return tips with proper formatting
    tips = f"""
Based on your spending data:

📊 SUMMARY:
• Income: {income_str}
• Expenses: {expense_str}
• Savings Rate: {saving_rate:.0f}%

📈 TOP SPENDING CATEGORIES:
{top_cats_str}

💡 PERSONALIZED TIPS:
1. Track every expense - Continue logging all transactions to identify patterns
2. Aim for 20% savings - Your current savings rate is {saving_rate:.0f}%
3. Review subscriptions - Check for unused monthly subscriptions
4. Set daily budget - Average daily spend is {avg_daily_str}
5. Emergency fund - Aim for 3-6 months of expenses saved

---
Note: Using rule-based financial tips.
    """
    
    return tips