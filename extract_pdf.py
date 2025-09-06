import PyPDF2
import os

# Change to the project directory
os.chdir('/Users/trose/src/locator-mcp')

# Open the PDF file
pdf_file = open('methodology_writeup.pdf', 'rb')
pdf_reader = PyPDF2.PdfReader(pdf_file)

# Extract text from all pages
text = ''
for page in pdf_reader.pages:
    text += page.extract_text() + '\n'

# Close the PDF file
pdf_file.close()

# Save the extracted text to a file
with open('methodology_writeup.txt', 'w', encoding='utf-8') as f:
    f.write(text)

print(f'Extracted text from {len(pdf_reader.pages)} pages')
print('Text saved to methodology_writeup.txt')