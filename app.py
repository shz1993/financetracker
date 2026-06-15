import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import extract

from utils.database import init_db, get_db, User, Category, Transaction, engine
from utils.auth import register_user, login_user, get_current_user
from utils.ai_insights import get_ai_insights
from utils.pdf_export import generate_pdf

# Page config
st.set_page_config(page_title="Finance Tracker", page_icon="💰", layout="wide")

# Initialize database
init_db()

# Session state
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "username" not in st.session_state:
    st.session_state.username = None

# ==================== AUTHENTICATION ====================

def show_login():
    st.title("💰 Personal Finance Tracker")
    st.subheader("Login or Register")
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")
            
            if submitted:
                db = next(get_db())
                success, result = login_user(db, username, password)
                if success:
                    st.session_state.user_id = result.id
                    st.session_state.username = result.username
                    st.rerun()
                else:
                    st.error(result)
    
    with tab2:
        with st.form("register_form"):
            email = st.text_input("Email")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            confirm = st.text_input("Confirm Password", type="password")
            submitted = st.form_submit_button("Register")
            
            if submitted:
                if password != confirm:
                    st.error("Passwords don't match")
                else:
                    db = next(get_db())
                    success, result = register_user(db, email, username, password)
                    if success:
                        st.success("Registration successful! Please login.")
                    else:
                        st.error(result)

# ==================== MAIN APP ====================

if not st.session_state.user_id:
    show_login()
else:
    db = next(get_db())
    user = get_current_user(db)
    
    # Sidebar
    with st.sidebar:
        st.header(f"👋 Hello, {st.session_state.username}")
        
        if st.button("🚪 Logout"):
            st.session_state.user_id = None
            st.session_state.username = None
            st.rerun()
        
        st.divider()
        st.subheader("➕ Add Transaction")
        
        with st.form("add_transaction"):
            categories = db.query(Category).all()
            cat_options = {c.name: c.id for c in categories}
            
            txn_type = st.selectbox("Type", ["expense", "income"])
            category = st.selectbox("Category", list(cat_options.keys()))
            amount = st.number_input("Amount (Rp)", min_value=0.0, step=10000.0)
            description = st.text_input("Description")
            date = st.date_input("Date", datetime.now())
            
            submitted = st.form_submit_button("Add")
            
            if submitted and amount > 0:
                new_txn = Transaction(
                    user_id=st.session_state.user_id,
                    category_id=cat_options[category],
                    amount=amount,
                    description=description,
                    date=date,
                    type=txn_type
                )
                db.add(new_txn)
                db.commit()
                st.success("Transaction added!")
                st.rerun()
    
    # Main content
    st.title("💰 Personal Finance Tracker")
    
    # Date filter
    col1, col2, col3 = st.columns(3)
    with col1:
        period = st.selectbox("Period", ["Monthly", "Yearly", "All Time"])
    with col2:
        if period == "Monthly":
            month = st.selectbox("Month", range(1, 13), format_func=lambda x: f"{x}/2026")
        else:
            month = None
    with col3:
        if period == "Yearly":
            year = st.selectbox("Year", [2024, 2025, 2026])
        else:
            year = None
    
    # Query transactions
    query = db.query(Transaction).filter(Transaction.user_id == st.session_state.user_id)

    if period == "Monthly":
        if month:
            start_date = f"2026-{month:02d}-01"
            if month == 12:
                end_date = "2027-01-01"
            else:
                end_date = f"2026-{month+1:02d}-01"
            query = query.filter(Transaction.date >= start_date)
            query = query.filter(Transaction.date < end_date)
            st.success(f"Menampilkan data bulan {month}/2026")
            
    elif period == "Yearly":
        if year:
            start_date = f"{year}-01-01"
            end_date = f"{year+1}-01-01"
            query = query.filter(Transaction.date >= start_date)
            query = query.filter(Transaction.date < end_date)
            st.success(f"Menampilkan data tahun {year}")
    
    transactions = query.order_by(Transaction.date.desc()).all()
    
    # Convert to DataFrame
    data = []
    for t in transactions:
        data.append({
            "id": t.id,
            "amount": t.amount,
            "description": t.description,
            "date": t.date,
            "type": t.type,
            "category_name": t.category.name,
            "category_icon": t.category.icon
        })
    df = pd.DataFrame(data)
    
    # Summary cards
    if not df.empty:
        income = df[df['type'] == 'income']['amount'].sum()
        expense = df[df['type'] == 'expense']['amount'].sum()
        balance = income - expense
        saving_rate = (balance / income * 100) if income > 0 else 0
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("💰 Income", f"Rp{income:,.0f}")
        col2.metric("💸 Expense", f"Rp{expense:,.0f}")
        col3.metric("💎 Balance", f"Rp{balance:,.0f}", delta=f"{saving_rate:.0f}% saved")
        col4.metric("📊 Transactions", len(df))
    else:
        st.info("No transactions yet. Add your first transaction from the sidebar!")
        income = expense = balance = 0
    
    # Charts
    if not df.empty:
        tab1, tab2, tab3 = st.tabs(["📊 Charts", "🤖 AI Insights", "📋 Transactions"])
        
        with tab1:
            col1, col2 = st.columns(2)
            
            with col1:
                expense_df = df[df['type'] == 'expense']
                if not expense_df.empty:
                    cat_expense = expense_df.groupby('category_name')['amount'].sum().reset_index()
                    fig = px.pie(cat_expense, values='amount', names='category_name', title='Expenses by Category')
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No expense data")
            
            with col2:
                if not df.empty:
                    df['date'] = pd.to_datetime(df['date'])
                    monthly = df.groupby([df['date'].dt.strftime('%Y-%m'), 'type'])['amount'].sum().reset_index()
                    fig2 = px.bar(monthly, x='date', y='amount', color='type', barmode='group', title='Monthly Overview')
                    st.plotly_chart(fig2, use_container_width=True)
                else:
                    st.info("No data available")
            
            if not df.empty:
                daily = df.groupby('date')['amount'].sum().reset_index()
                fig3 = px.line(daily, x='date', y='amount', title='Daily Spending Trend')
                st.plotly_chart(fig3, use_container_width=True)
            else:
                st.info("No data available")
        
        with tab2:
            st.subheader("🤖 AI Financial Insights")
            with st.spinner("Analyzing your spending..."):
                insights = get_ai_insights(df, period)
                st.markdown(insights)
            st.divider()
            st.caption("💡 AI uses Groq Llama 3 (free) to analyze your spending patterns")
        
        with tab3:
            st.subheader("Transaction History")
            search = st.text_input("🔍 Search transactions", placeholder="Type description or category...")
            filtered_df = df
            if search:
                filtered_df = df[df['description'].str.contains(search, case=False) | df['category_name'].str.contains(search, case=False)]
            
            display_df = filtered_df[['date', 'category_name', 'description', 'amount', 'type']].copy()
            display_df['amount'] = display_df['amount'].apply(lambda x: f"Rp{x:,.0f}")
            st.dataframe(display_df, use_container_width=True)
            
            with st.expander("🗑️ Delete Transaction"):
                txn_id = st.number_input("Transaction ID to delete", min_value=0, step=1)
                if st.button("Delete"):
                    txn = db.query(Transaction).filter(Transaction.id == txn_id, Transaction.user_id == st.session_state.user_id).first()
                    if txn:
                        db.delete(txn)
                        db.commit()
                        st.success(f"Deleted transaction {txn_id}")
                        st.rerun()
                    else:
                        st.error("Transaction not found")
    
    # Export
    if not df.empty:
        st.divider()
        col1, col2 = st.columns([1, 5])
        with col1:
            if st.button("📄 Export PDF"):
                summary = {
                    "Period": period,
                    "Total Income": f"Rp{income:,.0f}",
                    "Total Expense": f"Rp{expense:,.0f}",
                    "Balance": f"Rp{balance:,.0f}"
                }
                with st.spinner("Generating PDF..."):
                    pdf_bytes = generate_pdf(summary, df, insights)
                    st.download_button(
                        label="⬇️ Download PDF Report",
                        data=pdf_bytes,
                        file_name=f"finance_report_{datetime.now().strftime('%Y%m%d')}.pdf",
                        mime="application/pdf"
                    )

if __name__ == "__main__":
    pass