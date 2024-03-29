import streamlit as st
from PyPDF2 import PdfReader, PdfWriter, PageObject
import random
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO

# Define SessionState class to handle session state
class SessionState:
    def __init__(self, **kwargs):
        self._state = kwargs

    def __getattr__(self, attr):
        return self._state.get(attr, None)

    def __setattr__(self, attr, value):
        if attr == '_state':
            super().__setattr__(attr, value)
            return
        self._state[attr] = value

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

# Function to generate PDF for assigned question
def generate_pdf(assigned_question, roll_no):
    packet = BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    lines = assigned_question.split('\n')
    y = 750
    for line in lines:
        can.drawString(10, y, line)
        y -= 15
    can.save()
    packet.seek(0)
    new_pdf = PdfReader(packet)
    output = PdfWriter()
    output.add_page(new_pdf.pages[0])
    pdf_file_name = f"question_roll_{roll_no}.pdf"
    with open(pdf_file_name, "wb") as f:
        output.write(f)
    return pdf_file_name

# Main function
def main():
    st.title("Online Exam Questions")

    # Load PDF file and extract questions
    pdf_file = "ajpnew.pdf"
    questions = extract_questions_from_pdf(pdf_file)

    # Get roll number from user input
    roll_no = st.text_input("Enter your Roll Number")

    # Check if roll number is provided
    if roll_no:
        num_students = 74  # Total number of students

        # Initialize SessionState if not already initialized
        if 'session_state' not in st.session_state:
            st.session_state.session_state = SessionState(assigned_questions={})

        # Check if assigned_questions session state has been initialized
        try:
            assigned_questions = st.session_state.session_state.assigned_questions
        except TypeError:
            assigned_questions = {}

        # Assign questions to students if not already assigned
        if not assigned_questions:
            assigned_questions = assign_questions_to_students(questions, num_students)
            st.session_state.session_state.assigned_questions = assigned_questions

        # Display assigned question for the entered roll number
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
