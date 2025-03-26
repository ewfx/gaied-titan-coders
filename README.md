# 🚀 Project Name

## 📌 Table of Contents
- [Introduction](#introduction)
- [Demo](#demo)
- [Inspiration](#inspiration)
- [What It Does](#what-it-does)
- [How We Built It](#how-we-built-it)
- [Challenges We Faced](#challenges-we-faced)
- [How to Run](#how-to-run)
- [Tech Stack](#tech-stack)
- [Team](#team)

---

## 🎯 Introduction
A brief overview of your project and its purpose. Mention which problem statement are your attempting to solve. Keep it concise and engaging.

## 🎥 Demo
🔗 [Live Demo](#) (artifacts/demo/gaied-titan-coders-video.mkv)  
📹 [Video Demo](#) (artifacts/demo/gaied-titan-coders-video.mkv)  
🖼️ Screenshots:

![Screenshot 1](link-to-image)

## 💡 Inspiration
What inspired you to create this project? Describe the problem you're solving.

## ⚙️ What It Does
Here are the key features of the project:

1. Email Upload and Processing
   Users can upload .eml files through the web interface.
   The application processes the uploaded email to extract:
      Metadata: Subject, sender, recipient, and date.
      Body: Decodes and extracts the email content.
      Attachments: Saves attachments to a local directory.
2. Email Classification
   Uses Mistral AI to classify emails into predefined categories and subcategories.
   Provides feedback if the email cannot be classified.
3. Category Management
   Users can:
      Add new categories.
      Add subcategories to existing categories.
      Delete categories or subcategories.
      Categories are managed using the CategoryManager module.
4. File Management
   Uploaded files are securely saved in a designated uploads folder.
   Attachments from emails are extracted and stored locally.
   
## 🛠️ How We Built It
Briefly outline the technologies, frameworks, and tools used in development.

## 🚧 Challenges We Faced
Describe the major technical or non-technical challenges your team encountered.

## 🏃 How to Run
1. Clone the repository  
   ```sh
   git clone https://github.com/ewfx/gaied-titan-coders.git
   ```
2. Install dependencies  
   ```sh
   pip install -r requirements.txt 
   ```
3. Run the project  
   ```sh
    python app.py
   ```

## 🏗️ Tech Stack
- Python: The core programming language used for backend development, file handling, and email processing.
- Flask: A lightweight web framework for building the web application, handling routes, and managing user interactions.
- Mistral AI: A library used for email classification, leveraging AI to categorize emails into predefined categories and subcategories.

## 👥 Team
- Sainath Thadaka 
- Kalesha
- Lokeshwaran
- Jeeva
