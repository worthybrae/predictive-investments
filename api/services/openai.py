# api/services/openai_template.py
import os
import uuid
from typing import Dict, Any
from openai import OpenAI
from api.core.exceptions import ConfigurationException
from api.models.templates import TEMPLATES

class OpenAITemplateService:
    """Service for interacting with OpenAI API using templates."""
    
    @classmethod
    def _get_client(cls):
        """Get the OpenAI client."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ConfigurationException(detail="OpenAI API key not configured")
        
        # Initialize the client with the API key and other optional settings
        client_options = {
            "api_key": api_key,
            "timeout": 60.0,  # Set a reasonable timeout
        }
            
        return OpenAI(**client_options)
    
    @classmethod
    def get_template(cls, template_name: str):
        """Get a template by name."""
        if template_name not in TEMPLATES:
            raise ValueError(f"Template '{template_name}' not found")
        
        return TEMPLATES[template_name]
    
    @classmethod
    def validate_variables(cls, template: Dict[str, Any], variables: Dict[str, Any]):
        """Validate that all required variables are provided."""
        required_vars = set(template["required_vars"])
        provided_vars = set(variables.keys())
        
        missing_vars = required_vars - provided_vars
        if missing_vars:
            raise ValueError(f"Missing required variables: {', '.join(missing_vars)}")
        
        # Add default values for optional variables if not provided
        for var, default_value in template["optional_vars"].items():
            if var not in variables:
                variables[var] = default_value
                
        return variables
    
    @classmethod
    def format_prompt(cls, template: Dict[str, Any], variables: Dict[str, Any]):
        """Format the prompt template with the provided variables."""
        try:
            return template["user_prompt_template"].format(**variables)
        except KeyError as e:
            raise ValueError(f"Error formatting prompt template: {str(e)}")
    
    @classmethod
    async def process_template(
        cls,
        template_name: str,
        variables: Dict[str, Any],
        model: str = "gpt-4o-mini-mini"
    ) -> Dict[str, Any]:
        """
        Process a template with the provided variables.
        
        Args:
            template_name: Name of the template to use
            variables: Variables to populate the template
            model: OpenAI model to use
            
        Returns:
            Structured output response
        """
        try:
            # Get the template
            template = cls.get_template(template_name)
            
            # Validate variables
            validated_vars = cls.validate_variables(template, variables)
            
            # Format the prompt
            formatted_prompt = cls.format_prompt(template, validated_vars)
            
            # Get the response model
            response_model = template["model"]
            
            # Get the system prompt
            system_prompt = template["system_prompt"]
            
            # Get the client
            client = cls._get_client()
            
            # Prepare messages
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": formatted_prompt}
            ]
            
            # Call OpenAI API for structured output
            completion = client.beta.chat.completions.parse(
                model=model,
                messages=messages,
                response_format=response_model,
            )
            parsed_response = completion.choices[0].message.parsed
    
            # Format the response
            response = {
                "request_id": str(uuid.uuid4()),
                "model": model,
                "success": True,
                "result": parsed_response.dict(),
                "template_used": template_name
            }
            
            return response
        
        except Exception as e:
            # Handle errors
            return {
                "request_id": str(uuid.uuid4()),
                "model": model,
                "success": False,
                "error": str(e),
                "result": None,
                "template_used": template_name
            }