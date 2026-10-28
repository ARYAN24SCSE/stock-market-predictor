"""
Script to convert Stock_Market_Prediction_Project_Report.docx to PDF
using native Microsoft Word COM engine via win32com.client.
"""

import os
import sys
import win32com.client

def convert_docx_to_pdf():
    base_dir = os.path.abspath(os.path.dirname(__file__))
    docx_path = os.path.join(base_dir, "Stock_Market_Prediction_Project_Report.docx")
    pdf_path = os.path.join(base_dir, "Stock_Market_Prediction_Project_Report.pdf")

    if not os.path.exists(docx_path):
        print(f"Error: {docx_path} does not exist.")
        sys.exit(1)

    print(f"Input DOCX: {docx_path}")
    print(f"Output PDF: {pdf_path}")

    word = win32com.client.Dispatch("Word.Application")
    word.Visible = False

    try:
        doc = word.Documents.Open(docx_path)
        # 17 represents wdExportFormatPDF
        wdExportFormatPDF = 17
        doc.SaveAs(pdf_path, FileFormat=wdExportFormatPDF)
        doc.Close()
        print(f"Successfully created PDF: {pdf_path}")
    except Exception as e:
        print(f"Error during PDF conversion: {e}")
        try:
            doc.Close()
        except Exception:
            pass
        sys.exit(1)
    finally:
        word.Quit()

if __name__ == "__main__":
    convert_docx_to_pdf()
