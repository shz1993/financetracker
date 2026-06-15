from fpdf import FPDF
import pandas as pd
from datetime import datetime
import re

class PDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'Personal Finance Report', 0, 1, 'C')
        self.set_font('Arial', 'I', 10)
        self.cell(0, 5, f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}', 0, 1, 'C')
        self.ln(10)
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def clean_text(text):
    """Remove special characters"""
    if not text:
        return ""
    text = str(text)
    # Remove emojis and keep only basic characters
    text = re.sub(r'[^\x00-\x7F]+', '', text)
    text = text.replace('_', ' ')
    return text[:200]

def generate_pdf(summary_data, transactions_df, insights):
    """Generate PDF report and return bytes"""
    pdf = PDFReport()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Summary
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Financial Summary', 0, 1)
    pdf.set_font('Arial', '', 12)
    
    for key, value in summary_data.items():
        pdf.cell(60, 8, key, 0, 0)
        pdf.cell(0, 8, str(value), 0, 1)
    
    pdf.ln(10)
    
    # AI Insights
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'AI Insights & Tips', 0, 1)
    pdf.set_font('Arial', '', 11)
    cleaned_insights = clean_text(str(insights))
    pdf.multi_cell(0, 6, cleaned_insights)
    
    pdf.ln(10)
    
    # Transactions
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Recent Transactions', 0, 1)
    pdf.set_font('Arial', 'B', 9)
    
    # Headers
    pdf.cell(35, 8, 'Date', 1, 0, 'C')
    pdf.cell(45, 8, 'Category', 1, 0, 'C')
    pdf.cell(55, 8, 'Description', 1, 0, 'C')
    pdf.cell(35, 8, 'Amount', 1, 0, 'C')
    pdf.ln()
    
    pdf.set_font('Arial', '', 9)
    count = 0
    for _, row in transactions_df.iterrows():
        if count >= 20:
            break
        try:
            date_str = str(row['date'])[:10] if pd.notna(row['date']) else '-'
            cat_str = clean_text(str(row['category_name']))[:20]
            desc_str = clean_text(str(row['description']))[:25] if pd.notna(row['description']) else '-'
            amount_str = f"Rp{row['amount']:,.0f}"
            
            pdf.cell(35, 7, date_str, 1, 0, 'L')
            pdf.cell(45, 7, cat_str, 1, 0, 'L')
            pdf.cell(55, 7, desc_str, 1, 0, 'L')
            pdf.cell(35, 7, amount_str, 1, 0, 'R')
            pdf.ln()
            count += 1
        except Exception:
            continue
    
    # Return as bytes (proper format for Streamlit)
    return bytes(pdf.output(dest='S'))