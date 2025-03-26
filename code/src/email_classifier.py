import os
import json
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
import logging
import mimetypes
import base64
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class EmailClassifier:
    def __init__(self, api_key: str):
        """Initialize the EmailClassifier with Mistral AI API key."""
        self.client = MistralClient(api_key=api_key)
        self.model = "mistral-tiny"  # You can also use "mistral-small" or "mistral-medium" for better results

    def _encode_attachment(self, file_path: str) -> Optional[str]:
        """Encode attachment file to base64 string."""
        try:
            with open(file_path, 'rb') as file:
                return base64.b64encode(file.read()).decode('utf-8')
        except Exception as e:
            print(f"Error encoding attachment {file_path}: {str(e)}")
            return None

    def _get_attachment_info(self, attachment: Dict) -> str:
        """Get formatted information about an attachment."""
        file_path = attachment.get('path')
        if not file_path:
            return ""

        file_type = mimetypes.guess_type(file_path)[0] or 'unknown'
        file_size = os.path.getsize(file_path)
        file_size_mb = round(file_size / (1024 * 1024), 2)

        return f"\nAttachment: {attachment.get('filename')}\nType: {file_type}\nSize: {file_size_mb}MB"

    def _create_classification_prompt(self, email_data: Dict, categories: Dict) -> str:
        """Create a prompt for the classification task."""
        # Format categories for the prompt
        categories_text = "\n".join([
            f"- {category}:" + (f" {', '.join(subcategories)}" if subcategories else "")
            for category, subcategories in categories.items()
        ])
        
        return f"""Please classify this email into one of the following categories and subcategories:

Available Categories and Subcategories:
{categories_text}

Email Details:
Subject: {email_data.get('subject', 'No subject')}
From: {email_data.get('from', 'Unknown')}
Body: {email_data.get('body', 'No body')}

Respond with a JSON object in this exact format:
{{
    "category": "exact category name from the list above",
    "subcategory": "exact subcategory name from the list above (or null if none)",
    "explanation": "brief explanation of why this classification was chosen"
}}

IMPORTANT: The category and subcategory names must exactly match one from the list above."""

    def classify_email(self, email_data: Dict, categories: Dict) -> Dict:
        """
        Classify an email into a category and subcategory using Mistral AI.
        
        Args:
            email_data (dict): Dictionary containing email information
            categories (dict): Dictionary of available categories and subcategories
            
        Returns:
            dict: Classification result with category, subcategory, and explanation
        """
        try:
            # Create the prompt for classification
            prompt = self._create_classification_prompt(email_data, categories)
            
            # Create messages for the chat
            messages = [
                ChatMessage(role="system", content="You are an email classification assistant. Your task is to classify emails into predefined categories and subcategories. You must respond with a valid JSON object containing category, subcategory, and explanation fields."),
                ChatMessage(role="user", content=prompt)
            ]
            
            # Get classification from Mistral AI
            chat_response = self.client.chat(
                model=self.model,
                messages=messages
            )
            
            # Extract the response content
            response_text = chat_response.choices[0].message.content
            
            # Parse the response
            try:
                classification = json.loads(response_text)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse Mistral AI response: {str(e)}")
                return self._handle_classification_failure("Invalid response format", categories)
            
            # Validate the classification
            if not self._validate_classification(classification, categories):
                return self._handle_classification_failure("Invalid category or subcategory", categories)
            
            return classification
            
        except Exception as e:
            logger.error(f"Classification error: {str(e)}")
            return self._handle_classification_failure(str(e), categories)

    def _validate_classification(self, classification: Dict, categories: Dict) -> bool:
        """Validate that the classification matches available categories."""
        if not isinstance(classification, dict) or 'category' not in classification:
            return False
            
        category = classification['category']
        subcategory = classification.get('subcategory')
        
        # Check if category exists
        if category not in categories:
            return False
            
        # If subcategory is provided, check if it exists
        if subcategory and subcategory not in categories[category]:
            return False
            
        return True

    def _handle_classification_failure(self, error_message: str, categories: Dict) -> Dict:
        """Handle classification failure by finding the closest match."""
        logger.warning(f"Classification failed: {error_message}")
        
        # Try to find the closest matching category
        closest_category = self._find_closest_match(error_message, categories)
        
        return {
            'category': closest_category,
            'subcategory': None,
            'explanation': f"Classification failed: {error_message}. Assigned to closest matching category."
        }

    def _find_closest_match(self, text: str, categories: Dict) -> str:
        """Find the closest matching category based on text similarity."""
        # Simple implementation - can be enhanced with better matching algorithms
        text = text.lower()
        for category in categories:
            if category.lower() in text:
                return category
        return 'Unclassified' 