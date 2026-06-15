from fpdf import FPDF
import pandas as pd
from datetime import datetime

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

def generate_pdf(summary_data, transactions_df, insights):
    """Generate PDF report"""
    pdf = PDFReport()
    pdf.add_page()
    
    # Summary Section
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Financial Summary', 0, 1)
    pdf.set_font('Arial', '', 12)
    
    for key, value in summary_data.items():
        pdf.cell(60, 8, key, 0, 0)
        pdf.cell(0, 8, value, 0, 1)
    
    pdf.ln(10)
    
    # AI Insights
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'AI Insights & Tips', 0, 1)
    pdf.set_font('Arial', '', 12)
    pdf.multi_cell(0, 8, insights)
    
    pdf.ln(10)
    
    # Transactions Table
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Recent Transactions', 0, 1)
    pdf.set_font('Arial', 'B', 9)
    
    # Headers
    pdf.cell(40, 8, 'Date', 1, 0, 'C')
    pdf.cell(50, 8, 'Category', 1, 0, 'C')
    pdf.cell(50, 8, 'Description', 1, 0, 'C')
    pdf.cell(30, 8, 'Amount', 1, 0, 'C')
    pdf.ln()
    
    pdf.set_font('Arial', '', 9)
    for _, row in transactions_df.head(20).iterrows():
        pdf.cell(40, 8, str(row['date']), 1, 0, 'L')
        pdf.cell(50, 8, row['category_name'], 1, 0, 'L')
        desc = row['description'][:40] if row['description'] else '-'
        pdf.cell(50, 8, desc, 1, 0, 'L')
        amount = f"Rp{row['amount']:,.0f}"
        pdf.cell(30, 8, amount, 1, 0, 'R')
        pdf.ln()
    
    return pdf.output(dest='S').encode('latin1')