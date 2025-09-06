import PyPDF2
import os

# Change to the project directory
os.chdir('/Users/trose/src/locator-mcp')

# Open the PDF file
pdf_file = open('methodology_writeup.pdf', 'rb')
pdf_reader = PyPDF2.PdfReader(pdf_file)

# Extract text from all pages
print(f"Number of pages: {len(pdf_reader.pages)}")

full_text = ""
for i, page in enumerate(pdf_reader.pages):
    text = page.extract_text()
    print(f"\n--- Page {i+1} ---")
    print(f"Text length: {len(text)} characters")
    print(text[:500] + "..." if len(text) > 500 else text)
    full_text += text + "\n\n"

# Close the PDF file
pdf_file.close()

# Save the extracted text to a file
with open('methodology_writeup_detailed.txt', 'w', encoding='utf-8') as f:
    f.write(full_text)

print(f"\nFull text saved to methodology_writeup_detailed.txt")