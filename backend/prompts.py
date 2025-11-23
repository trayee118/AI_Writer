# prompts.py - Prompt Templates for Different Content Types

class PromptTemplates:
    """
    Prompt templates for different content generation types
    """
    
    @staticmethod
    def get_prompt(content_type, user_input):
        """
        Generate appropriate prompt based on content type
        
        Args:
            content_type (str): Type of content (blog, email, copy, etc.)
            user_input (str): User's input text
        
        Returns:
            str: Formatted prompt string
        """
        
        prompts = {
            'blog': f"""Write a comprehensive and engaging blog post about: {user_input}

Create a well-structured blog post with the following elements:
- An attention-grabbing introduction
- Clear and informative main content with multiple paragraphs
- Practical examples or insights
- A strong conclusion

Blog Post:
""",
            
            'email': f"""Write a professional email about: {user_input}

The email should include:
- A clear and relevant subject line
- Professional greeting
- Well-structured body with main message
- Appropriate closing and sign-off

Email:
Subject: 
Dear [Recipient],

""",
            
            'copy': f"""Write persuasive marketing copy for: {user_input}

Create compelling marketing copy that includes:
- An attention-grabbing headline
- Benefits-focused body text that resonates with the audience
- Emotional appeal and value proposition
- Strong call-to-action that motivates readers

Marketing Copy:
""",
            
            'seo': f"""Write SEO-optimized content about: {user_input}

Create search engine optimized content that includes:
- Relevant keywords naturally integrated throughout
- Clear headings and subheadings
- Informative and valuable content for readers
- Meta description friendly structure

SEO Content:
""",
            
            'video': f"""Write an engaging video script about: {user_input}

Create a video script with:
- A powerful hook to grab attention in the first 5 seconds
- Clear and engaging main content
- Natural conversational tone
- Strong call-to-action at the end

Video Script:
[Opening Hook]
""",
            
            'summarize': f"""Provide a clear and concise summary of the following text. Capture the main points and key information:

{user_input}

Summary:
""",
            
            'content': f"""Generate creative and engaging content about: {user_input}

Create original content that is:
- Well-written and easy to read
- Informative and valuable
- Properly structured with clear flow

Content:
"""
        }
        
        # Return the appropriate prompt or default to 'content'
        return prompts.get(content_type, prompts['content'])
    
    
    @staticmethod
    def get_short_prompt(content_type, user_input):
        """
        Generate shorter, more direct prompts for faster generation
        
        Args:
            content_type (str): Type of content
            user_input (str): User's input text
        
        Returns:
            str: Short formatted prompt
        """
        
        short_prompts = {
            'blog': f"Write a blog post about {user_input}:\n\n",
            'email': f"Write a professional email about {user_input}:\n\n",
            'copy': f"Write marketing copy for {user_input}:\n\n",
            'seo': f"Write SEO content about {user_input}:\n\n",
            'video': f"Write a video script about {user_input}:\n\n",
            'summarize': f"Summarize: {user_input}\n\nSummary:\n",
            'content': f"Write about {user_input}:\n\n"
        }
        
        return short_prompts.get(content_type, short_prompts['content'])
    
    
    @staticmethod
    def clean_output(generated_text, content_type):
        """
        Clean and format the generated output
        
        Args:
            generated_text (str): Raw generated text
            content_type (str): Type of content
        
        Returns:
            str: Cleaned and formatted text
        """
        
        # Remove leading/trailing whitespace
        text = generated_text.strip()
        
        # Remove excessive newlines (more than 2 consecutive)
        while '\n\n\n' in text:
            text = text.replace('\n\n\n', '\n\n')
        
        # Remove excessive spaces
        while '  ' in text:
            text = text.replace('  ', ' ')
        
        # Remove common artifacts from generation
        artifacts = [
            '[END]',
            '[DONE]',
            '<|endoftext|>',
            '<END>',
            '</s>',
        ]
        
        for artifact in artifacts:
            if artifact in text:
                text = text.split(artifact)[0]
        
        # Content-specific cleaning
        if content_type == 'email':
            # Ensure email has proper structure
            if not text.startswith('Subject:'):
                text = f"Subject: Re: Your Inquiry\n\n{text}"
        
        elif content_type == 'video':
            # Ensure video script markers are present
            if '[Opening Hook]' not in text and '[Hook]' not in text:
                text = f"[Opening Hook]\n{text}"
        
        elif content_type == 'summarize':
            # For summaries, remove redundant "Summary:" labels
            if text.startswith('Summary:'):
                text = text.replace('Summary:', '', 1).strip()
        
        # Remove incomplete sentences at the end (optional)
        if len(text) > 100 and not text[-1] in ['.', '!', '?', '"', "'", ')']:
            # Find the last complete sentence
            last_period = max(
                text.rfind('.'),
                text.rfind('!'),
                text.rfind('?')
            )
            if last_period > len(text) * 0.7:  # Only if it's in the last 30%
                text = text[:last_period + 1]
        
        return text.strip()
    
    
    @staticmethod
    def add_context(content_type, user_input, additional_context=""):
        """
        Add additional context to improve generation quality
        
        Args:
            content_type (str): Type of content
            user_input (str): User's input text
            additional_context (str): Extra context or requirements
        
        Returns:
            str: Enhanced prompt with context
        """
        
        base_prompt = PromptTemplates.get_prompt(content_type, user_input)
        
        if additional_context:
            context_section = f"\nAdditional Context: {additional_context}\n\n"
            # Insert context before the content generation starts
            parts = base_prompt.split('\n\n')
            if len(parts) > 1:
                parts.insert(-1, context_section)
                return '\n\n'.join(parts)
        
        return base_prompt
    
    
    @staticmethod
    def get_available_types():
        """
        Get list of available content types
        
        Returns:
            list: Available content types
        """
        return [
            'blog',
            'email',
            'copy',
            'seo',
            'video',
            'summarize',
            'content'
        ]
    
    
    @staticmethod
    def validate_content_type(content_type):
        """
        Validate if content type is supported
        
        Args:
            content_type (str): Content type to validate
        
        Returns:
            bool: True if valid, False otherwise
        """
        return content_type in PromptTemplates.get_available_types()
    
    
    @staticmethod
    def get_type_description(content_type):
        """
        Get description for a content type
        
        Args:
            content_type (str): Content type
        
        Returns:
            str: Description of the content type
        """
        
        descriptions = {
            'blog': 'Generate comprehensive blog posts with introduction, body, and conclusion',
            'email': 'Create professional emails with proper structure and formatting',
            'copy': 'Write persuasive marketing copy with strong call-to-action',
            'seo': 'Generate SEO-optimized content with relevant keywords',
            'video': 'Create engaging video scripts with hooks and CTAs',
            'summarize': 'Provide concise summaries of longer text content',
            'content': 'Generate general creative content on any topic'
        }
        
        return descriptions.get(content_type, 'Generate content')