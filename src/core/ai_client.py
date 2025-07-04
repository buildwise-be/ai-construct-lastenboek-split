"""
AI Client Module for Vertex AI Integration

This module handles all Vertex AI interactions with proper retry logic and rate limiting.
Extracted from the monolithic main script to improve maintainability.
"""

import os
import time
import random
import logging
import re
from dotenv import load_dotenv
import vertexai
from vertexai.generative_models import GenerativeModel, SafetySetting

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Vertex AI configuration
GENERATION_CONFIG = {
    "max_output_tokens": 30000,
    "temperature": 1,
    "top_p": 0.95,
}

SAFETY_SETTINGS = [
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
        threshold=SafetySetting.HarmBlockThreshold.OFF
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
        threshold=SafetySetting.HarmBlockThreshold.OFF
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
        threshold=SafetySetting.HarmBlockThreshold.OFF
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_HARASSMENT,
        threshold=SafetySetting.HarmBlockThreshold.OFF
    ),
]

# Global variables for rate limiting
consecutive_failures = 0
last_failure_time = 0


class VertexAIClient:
    """
    A client for Vertex AI that handles initialization, rate limiting, and retry logic.
    """
    
    def __init__(self, project_id=None):
        """
        Initialize the Vertex AI client.
        
        Args:
            project_id (str, optional): Google Cloud project ID
        """
        self.project_id = project_id or os.environ.get("GOOGLE_CLOUD_PROJECT", "")
        self.model = None
        self._initialize_vertex_ai()
    
    def _initialize_vertex_ai(self):
        """Initialize Vertex AI with the specified project and location."""
        try:
            if not self.project_id:
                logger.warning("GOOGLE_CLOUD_PROJECT environment variable not set. Please set it before running in production.")
            
            vertexai.init(
                project=self.project_id,
                location="europe-west1",
                api_endpoint="europe-west1-aiplatform.googleapis.com"
            )
            logger.info(f"Successfully initialized Vertex AI (Project: {self.project_id})")
        except Exception as e:
            logger.error(f"Failed to initialize Vertex AI: {str(e)}")
            raise
    
    def create_model(self, model_name="gemini-2.5-pro", system_instruction=None):
        """
        Create a Vertex AI model instance.
        
        Args:
            model_name (str): The model name to use
            system_instruction (str, optional): System instruction for the model
            
        Returns:
            GenerativeModel: Initialized model instance
        """
        try:
            self.model = GenerativeModel(
                model_name,
                generation_config=GENERATION_CONFIG,
                safety_settings=SAFETY_SETTINGS,
                system_instruction=[system_instruction] if system_instruction else None
            )
            logger.info(f"Successfully created {model_name} model")
            return self.model
        except Exception as e:
            logger.error(f"Failed to create model: {str(e)}")
            raise
    
    def process_with_retry(self, model, prompt, post_process=False, max_retries=5):
        """
        Process a prompt with Vertex AI with advanced retry logic and rate limiting.
        
        Args:
            model: The Vertex AI model instance
            prompt (str): The prompt to process
            post_process (bool): Whether to post-process the response to extract Python code
            max_retries (int): Maximum number of retries on failure
            
        Returns:
            str or dict: The model's response text, or extracted Python code if post_process=True
        """
        global consecutive_failures, last_failure_time
        
        # Apply dynamic cooldown if we're hitting rate limits
        if consecutive_failures > 3:
            cooldown = min(30, consecutive_failures * 5)  # Max 30 second cooldown
            time_since_last_failure = time.time() - last_failure_time
            if time_since_last_failure < cooldown:
                sleep_time = cooldown - time_since_last_failure
                logger.info(f"Rate limit cooldown: Waiting {sleep_time:.1f} seconds before next request...")
                time.sleep(sleep_time)
        
        for attempt in range(max_retries):
            try:
                # Calculate backoff with jitter to avoid thundering herd problem
                if attempt > 0:
                    base_delay = min(30, 2 ** attempt)  # Cap at 30 seconds
                    jitter = random.uniform(0, 0.1 * base_delay)  # 10% jitter
                    delay = base_delay + jitter
                    logger.info(f"Retry attempt {attempt+1}/{max_retries}: Waiting {delay:.2f} seconds...")
                    time.sleep(delay)
                
                # Make the API call
                response = model.generate_content(prompt)
                
                # Reset consecutive failures counter on success
                consecutive_failures = 0
                
                if post_process:
                    logger.debug(f"Post-processing enabled, raw response length: {len(response.text)}")
                    processed_response = self._post_process_response(response.text)
                    logger.debug(f"Post-processed response type: {type(processed_response)}")
                    if isinstance(processed_response, dict):
                        logger.debug(f"Dictionary keys: {list(processed_response.keys())}")
                    return processed_response
                
                return response.text
                
            except Exception as e:
                # Update failure tracking
                consecutive_failures += 1
                last_failure_time = time.time()
                
                error_message = str(e)
                # Check if it's a rate limit error
                if "429" in error_message and "Resource exhausted" in error_message:
                    if attempt < max_retries - 1:
                        logger.warning(f"Attempt {attempt + 1} failed with rate limit (429), applying exponential backoff: {error_message}")
                    else:
                        logger.error(f"Failed to process with Vertex AI after {max_retries} attempts: {error_message}")
                        raise
                else:
                    if attempt < max_retries - 1:
                        logger.warning(f"Attempt {attempt + 1} failed, retrying: {error_message}")
                    else:
                        logger.error(f"Failed to process with Vertex AI after {max_retries} attempts: {error_message}")
                        raise
    
    def _post_process_response(self, response_text):
        """
        Extract Python code from the response text.
        
        Args:
            response_text (str): The raw response from the model
            
        Returns:
            dict or str: Extracted Python dictionary or original text
        """
        logger.debug(f"Post-processing response (first 200 chars): {response_text[:200]}")
        
        code_block_match = None
        code_block = None
        
        try:
            code_block_match = re.search(r'```python\s*(.*?)\s*```', response_text, re.DOTALL)
            if code_block_match:
                code_block = code_block_match.group(1)
                logger.debug(f"Found Python code block (first 200 chars): {code_block[:200]}")
                
                # Extract the dictionary from various possible variable names
                local_vars = {}
                exec(code_block, {}, local_vars)
                
                logger.debug(f"Executed code block, local_vars keys: {list(local_vars.keys())}")
                
                # Check for different possible variable names
                for var_name in ['results', 'chapters', 'secties', 'response', 'data', 'result']:
                    if var_name in local_vars:
                        logger.debug(f"Found variable '{var_name}' of type {type(local_vars[var_name])}")
                        return local_vars[var_name]
                
                # If no named variable found, return the first dictionary found
                for var_name, value in local_vars.items():
                    if isinstance(value, dict):
                        logger.debug(f"Found dictionary variable '{var_name}' of type {type(value)}")
                        return value
                
                # If still no dictionary found, try to evaluate the code block directly as an expression
                try:
                    # Sometimes the AI returns just a dictionary without variable assignment
                    code_block_stripped = code_block.strip()
                    if code_block_stripped.startswith('{') and code_block_stripped.endswith('}'):
                        logger.debug("Attempting to evaluate code block as direct dictionary expression")
                        result = eval(code_block_stripped, {}, {})
                        if isinstance(result, dict):
                            logger.debug(f"Successfully evaluated direct dictionary of type {type(result)}")
                            return result
                except Exception as eval_error:
                    logger.debug(f"Failed to evaluate as direct expression: {eval_error}")
                
                logger.warning(f"No dictionary found in executed code. Variables: {local_vars}")
            else:
                logger.warning("No Python code block found in response")
                logger.debug(f"Full response text: {response_text}")
                        
        except Exception as e:
            logger.warning(f"Failed to post-process response: {str(e)}")
            logger.warning(f"Exception type: {type(e).__name__}")
            if code_block:
                logger.warning(f"Failed code block: {code_block}")
        
        # Fall back to returning raw text
        logger.warning("Falling back to raw text response")
        return response_text
    
    def update_project_id(self, new_project_id):
        """
        Update the project ID and reinitialize Vertex AI.
        
        Args:
            new_project_id (str): New Google Cloud project ID
        """
        self.project_id = new_project_id
        self._initialize_vertex_ai()
        logger.info(f"Updated project ID to: {new_project_id}")


# Global client instance for backward compatibility
_global_client = None

def get_global_client():
    """Get or create the global AI client instance."""
    global _global_client
    if _global_client is None:
        _global_client = VertexAIClient()
    return _global_client

def initialize_vertex_model(system_instruction=None, project_id=None):
    """
    Initialize the Vertex AI Gemini model (backward compatibility function).
    
    Args:
        system_instruction (str, optional): System instruction for the model
        project_id (str, optional): Google Cloud project ID to use
        
    Returns:
        GenerativeModel: Initialized model
    """
    client = get_global_client()
    if project_id:
        client.update_project_id(project_id)
    return client.create_model(system_instruction=system_instruction)

def process_with_vertex_ai(model, prompt, post_process=False, max_retries=5):
    """
    Process a prompt with Vertex AI (backward compatibility function).
    
    Args:
        model: The Vertex AI model instance
        prompt (str): The prompt to process
        post_process (bool): Whether to post-process the response to extract Python code
        max_retries (int): Maximum number of retries on failure
        
    Returns:
        str or dict: The model's response text, or extracted Python code if post_process=True
    """
    client = get_global_client()
    return client.process_with_retry(model, prompt, post_process, max_retries)