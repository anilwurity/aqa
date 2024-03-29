import streamlit as st
from PyPDF2 import PdfReader, PdfWriter,PageObject
import random
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
# Function to extract questions from PDF file
def extract_questions_from_pdf(pdf_file):
    questions = []
    with open(pdf_file, "rb") as file:
        pdf_reader = PdfReader(file)
        num_pages = len(pdf_reader.pages)
        for page_num in range(num_pages):
            page = pdf_reader.pages[page_num]
            text = page.extract_text()
            questions.append(text)
    return questions

# Function to assign questions to students
def assign_questions_to_students(questions, num_students):
    assigned_questions = {}
    available_questions = list(range(len(questions)))
    random.shuffle(available_questions)
    for student_num in range(1, num_students + 1):
        if available_questions:
            question_index = available_questions.pop()  # Assigning 1 question per student
            assigned_questions[student_num] = questions[question_index]
        else:
            assigned_questions[student_num] = "No more questions available."
    return assigned_questions

def generate_pdf(assigned_question, roll_no):
    packet = BytesIO()
    # create a new PDF with ReportLab
    can = canvas.Canvas(packet, pagesize=letter)
    
    # Split the text into lines to handle multi-line text
    lines = assigned_question.split('\n')
    
    # Set initial y-coordinate for the first line
    y = 750
    
    # Draw each line of text
    for line in lines:
        can.drawString(10, y, line)  # Draw text at position (10, y)
        y -= 15  # Move to the next line (decrease y-coordinate)
    
    can.save()

    # move to the beginning of the BytesIO buffer
    packet.seek(0)
    new_pdf = PdfReader(packet)
    output = PdfWriter()

    # add the "watermark" (which is the new pdf) on the existing page
    output.add_page(new_pdf.pages[0])

    # save the new PDF to a file
    pdf_file_name = f"question_roll_{roll_no}.pdf"
    with open(pdf_file_name, "wb") as f:
        output.write(f)
    
    return pdf_file_name

def main():
    st.title("Online Exam Questions")

    # Load PDF file and extract questions
    pdf_file = "alp.pdf"  # Replace with the actual path to your PDF file
    questions = extract_questions_from_pdf(pdf_file)

    roll_no = st.text_input("Enter your Roll Number")

    if roll_no:
        num_students = 74  # Number of students
        
        # Assign questions to students if not already assigned
        assigned_questions = assign_questions_to_students(questions, num_students)

        # Display assigned questions for the entered roll number
        if roll_no.isdigit():
            roll_no = int(roll_no)
            if roll_no in assigned_questions:
                st.header(f"Question for Roll Number {roll_no}")
                st.markdown(f"**Question:** {assigned_questions[roll_no]}")

                # Generate PDF for the assigned question
                pdf_file_name = generate_pdf(assigned_questions[roll_no], roll_no)

                # Provide download link for the generated PDF
                st.markdown(f"[Download Question PDF](/{pdf_file_name})")
            else:
                st.write("Roll Number not found or no question assigned.")
        else:
            st.write("Please enter a valid Roll Number.")

if __name__ == "__main__":
    main()
