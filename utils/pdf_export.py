from fpdf import FPDF
import pandas as pd
from datetime import datetime
import re

class PDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.set_text_color(40, 40, 100)
        self.cell(0, 10, 'Personal Finance Report', 0, 1, 'C')
        self.set_font('Arial', 'I', 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 5, f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}', 0, 1, 'C')
        self.ln(8)
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def clean_text(text):
    """Clean text for PDF"""
    if not text:
        return ""
    text = str(text)
    # Remove emojis
    text = re.sub(r'[^\x00-\x7F]+', '', text)
    return text.strip()

def generate_pdf(summary_data, transactions_df, insights):
    """Generate PDF report"""
    pdf = PDFReport()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Summary Section
    pdf.set_font('Arial', 'B', 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 8, 'FINANCIAL SUMMARY', 0, 1)
    pdf.set_font('Arial', '', 11)
    
    for key, value in summary_data.items():
        pdf.cell(50, 7, key, 0, 0)
        pdf.cell(0, 7, str(value), 0, 1)
    
    pdf.ln(5)
    
    # AI Insights
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, 'AI INSIGHTS & TIPS', 0, 1)
    pdf.set_font('Arial', '', 10)
    
    cleaned_insights = clean_text(str(insights))
    pdf.multi_cell(0, 5, cleaned_insights)
    
    pdf.ln(5)
    
    # Transactions
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, 'RECENT TRANSACTIONS', 0, 1)
    pdf.set_font('Arial', 'B', 9)
    
    # Headers
    pdf.set_fill_color(200, 200, 220)
    pdf.cell(35, 8, 'Date', 1, 0, 'C', 1)
    pdf.cell(45, 8, 'Category', 1, 0, 'C', 1)
    pdf.cell(55, 8, 'Description', 1, 0, 'C', 1)
    pdf.cell(35, 8, 'Amount', 1, 0, 'C', 1)
    pdf.ln()
    
    pdf.set_font('Arial', '', 9)
    pdf.set_fill_color(255, 255, 255)
    count = 0
    for _, row in transactions_df.iterrows():
        if count >= 20:
            break
        try:
            date_str = str(row['date'])[:10] if pd.notna(row['date']) else '-'
            cat_str = clean_text(str(row['category_name']))[:20]
            desc_str = clean_text(str(row['description']))[:25] if pd.notna(row['description']) else '-'
            amount_str = f"Rp{row['amount']:,.0f}".replace(',', '.')
            
            pdf.cell(35, 7, date_str, 1, 0, 'L')
            pdf.cell(45, 7, cat_str, 1, 0, 'L')
            pdf.cell(55, 7, desc_str, 1, 0, 'L')
            pdf.cell(35, 7, amount_str, 1, 0, 'R')
            pdf.ln()
            count += 1
        except Exception:
            continue
    
    return pdf.output(dest='S')