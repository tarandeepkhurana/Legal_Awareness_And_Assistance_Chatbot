from PyPDF2 import PdfReader, PdfWriter

def split_pdf(input_path, pages_per_file=30):
    reader = PdfReader(input_path)
    total_pages = len(reader.pages)
    part_num = 1

    for start in range(0, total_pages, pages_per_file):
        writer = PdfWriter()
        end = min(start + pages_per_file, total_pages)
        for page_num in range(start, end):
            writer.add_page(reader.pages[page_num])

        output_filename = f"output_part_{part_num}.pdf"
        with open(output_filename, "wb") as output_file:
            writer.write(output_file)
        print(f"✅ Created {output_filename} with pages {start+1}-{end}")
        part_num += 1

def extract_pages(input_path, start_page, end_page, output_path):
    """
    Extracts pages from start_page to end_page (inclusive) and saves to output_path.
    Pages are 1-indexed.
    """
    reader = PdfReader(input_path)
    writer = PdfWriter()

    # Adjust because PyPDF2 uses 0-based indexing
    for i in range(start_page - 1, end_page):
        writer.add_page(reader.pages[i])

    with open(output_path, "wb") as output_file:
        writer.write(output_file)

    print(f"✅ Extracted pages {start_page}–{end_page} into '{output_path}'")


extract_pages("SOP for Investigation and Prosecution of Rape against Women -Final submitted (Revised) to JS WS MHA.pdf", 3, 16, "extracted_21_50.pdf")


# split_pdf("src\docs\Bharatiya_Nyaya_Sanhita_2023.PDF", pages_per_file=30)
