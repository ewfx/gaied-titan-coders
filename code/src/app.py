from flask import Flask, render_template, request, send_file, redirect, url_for, flash
import email
import os
from email.header import decode_header
import tempfile
from werkzeug.utils import secure_filename
from category_manager import CategoryManager
from email_classifier import EmailClassifier
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Required for flash messages

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'eml'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize managers
logger.debug("Initializing CategoryManager")
category_manager = CategoryManager()

logger.debug("Initializing EmailClassifier")
classifier = EmailClassifier(api_key=os.getenv('MISTRAL_API_KEY'))

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_eml_file(file_path):
    """Process an .eml file and extract its contents and attachments."""
    logger.debug(f"Processing EML file: {file_path}")
    try:
        with open(file_path, 'rb') as f:
            msg = email.message_from_bytes(f.read())
        
        # Initialize email data dictionary
        email_data = {
            'subject': '',
            'from': '',
            'to': '',
            'date': '',
            'body': '',
            'attachments': []
        }
        
        # Decode subject
        subject = msg.get('subject')
        if subject:
            decoded_subject = decode_header(subject)[0][0]
            if isinstance(decoded_subject, bytes):
                email_data['subject'] = decoded_subject.decode()
            else:
                email_data['subject'] = decoded_subject
        
        # Get other headers
        email_data['from'] = msg.get('from', '')
        email_data['to'] = msg.get('to', '')
        email_data['date'] = msg.get('date', '')
        
        # Process body and attachments
        for part in msg.walk():
            if part.get_content_maintype() == 'multipart':
                continue
            
            if part.get_content_maintype() == 'text':
                try:
                    body = part.get_payload(decode=True).decode()
                    email_data['body'] = body
                except Exception as e:
                    logger.error(f"Error decoding email body: {str(e)}")
                    email_data['body'] = "Could not decode email body"
            
            elif part.get_content_maintype() == 'application':
                filename = part.get_filename()
                if filename:
                    decoded_filename = decode_header(filename)[0][0]
                    if isinstance(decoded_filename, bytes):
                        filename = decoded_filename.decode()
                    
                    # Save attachment
                    attachment_path = os.path.join(UPLOAD_FOLDER, secure_filename(filename))
                    with open(attachment_path, 'wb') as f:
                        f.write(part.get_payload(decode=True))
                    
                    email_data['attachments'].append({
                        'filename': filename,
                        'path': attachment_path,
                        'content_type': part.get_content_type()
                    })
        
        logger.debug(f"Successfully processed email: {email_data['subject']}")
        return email_data
    except Exception as e:
        logger.error(f"Error processing EML file: {str(e)}")
        raise

@app.route('/')
def home():
    logger.debug("Rendering home page")
    return render_template('index.html', title='Home')

@app.route('/categories')
def categories():
    logger.debug("Rendering categories page")
    categories_data = category_manager.get_categories()
    return render_template('categories.html', categories=categories_data, title='Categories')

@app.route('/categories/add', methods=['POST'])
def add_category():
    logger.debug("Adding new category")
    category_name = request.form.get('category_name')
    if category_name:
        if category_manager.add_category(category_name):
            logger.info(f"Successfully added category: {category_name}")
            flash(f'Category "{category_name}" added successfully!', 'success')
            return redirect(url_for('categories'))
    logger.error("Failed to add category")
    return 'Failed to add category', 400

@app.route('/categories/<category_name>/add_subcategory', methods=['POST'])
def add_subcategory(category_name):
    logger.debug(f"Adding subcategory to category: {category_name}")
    subcategory_name = request.form.get('subcategory_name')
    if subcategory_name:
        if category_manager.add_subcategory(category_name, subcategory_name):
            logger.info(f"Successfully added subcategory {subcategory_name} to {category_name}")
            flash(f'Subcategory "{subcategory_name}" added to "{category_name}" successfully!', 'success')
            return redirect(url_for('categories'))
    logger.error(f"Failed to add subcategory to {category_name}")
    return 'Failed to add subcategory', 400

@app.route('/categories/<category_name>/delete', methods=['POST'])
def delete_category(category_name):
    logger.debug(f"Deleting category: {category_name}")
    if category_manager.delete_category(category_name):
        logger.info(f"Successfully deleted category: {category_name}")
        flash(f'Category "{category_name}" deleted successfully!', 'success')
        return redirect(url_for('categories'))
    logger.error(f"Failed to delete category: {category_name}")
    return 'Failed to delete category', 400

@app.route('/categories/<category_name>/subcategories/<subcategory_name>/delete', methods=['POST'])
def delete_subcategory(category_name, subcategory_name):
    logger.debug(f"Deleting subcategory {subcategory_name} from category {category_name}")
    if category_manager.delete_subcategory(category_name, subcategory_name):
        logger.info(f"Successfully deleted subcategory {subcategory_name} from {category_name}")
        flash(f'Subcategory "{subcategory_name}" deleted from "{category_name}" successfully!', 'success')
        return redirect(url_for('categories'))
    logger.error(f"Failed to delete subcategory {subcategory_name} from {category_name}")
    return 'Failed to delete subcategory', 400

@app.route('/upload', methods=['POST'])
def upload_file():
    logger.debug("Starting file upload process")
    if 'file' not in request.files:
        logger.error("No file uploaded")
        flash('No file uploaded', 'error')
        return redirect(url_for('home'))
    
    file = request.files['file']
    if file.filename == '':
        logger.error("No file selected")
        flash('No file selected', 'error')
        return redirect(url_for('home'))
    
    if file and allowed_file(file.filename):
        try:
            logger.debug(f"Processing uploaded file: {file.filename}")
            # Save the uploaded file temporarily
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Process the .eml file
            email_data = process_eml_file(filepath)
            
            # Get categories for classification
            categories = category_manager.get_categories()
            logger.debug(f"Available categories: {list(categories.keys())}")
            
            if not categories:
                logger.error("No categories available for classification")
                flash('Please create at least one category before classifying emails.', 'error')
                return redirect(url_for('home'))
            
            # Classify the email
            logger.debug("Starting email classification")
            classification = classifier.classify_email(email_data, categories)
            logger.debug(f"Classification result: {classification}")
            
            # Check if classification failed
            if classification['category'] == 'Unclassified':
                logger.error(f"Classification failed: {classification['explanation']}")
                flash(f'Classification failed: {classification["explanation"]}', 'error')
                return redirect(url_for('home'))
            
            # Add classification to email data
            email_data['classification'] = classification
            
            # Clean up the temporary file
            os.remove(filepath)
            
            logger.info("Successfully processed and classified email")
            flash(f'Email classified successfully! Category: {classification["category"]}, Subcategory: {classification["subcategory"]}', 'success')
            return render_template('email_view.html', email=email_data)
            
        except Exception as e:
            logger.error(f"Error processing email: {str(e)}", exc_info=True)
            flash(f'Error processing email: {str(e)}', 'error')
            return redirect(url_for('home'))
    
    logger.error("Invalid file type")
    flash('Invalid file type. Please upload an .eml file.', 'error')
    return redirect(url_for('home'))

@app.route('/download/<filename>')
def download_file(filename):
    logger.debug(f"Downloading file: {filename}")
    return send_file(
        os.path.join(UPLOAD_FOLDER, filename),
        as_attachment=True
    )

if __name__ == '__main__':
    logger.info("Starting Flask application")
    # Check for required environment variables
    if not os.getenv('MISTRAL_API_KEY'):
        logger.error("MISTRAL_API_KEY not found in environment variables")
        print("Error: MISTRAL_API_KEY not found in environment variables")
        exit(1)
    
    app.run(debug=True) 