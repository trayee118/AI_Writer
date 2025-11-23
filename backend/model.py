# model.py - AI Model Configuration and Loading

from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIWriterModel:
    def __init__(self, model_name="gpt2"):
        """
        Initialize the AI Writer model with tokenizer
        Default: gpt2 (lightweight model)
        
        Alternatives: 
        - "gpt2" (124M params - Fast, lightweight)
        - "gpt2-medium" (355M params - Better quality)
        - "EleutherAI/gpt-neo-125M" (Good balance)
        - "facebook/opt-350m" (Better quality)
        - "distilgpt2" (Faster, smaller)
        """
        logger.info(f"Loading model: {model_name}...")
        self.model_name = model_name
        
        try:
            # Load tokenizer
            logger.info("Loading tokenizer...")
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            
            # Set pad token if not exists
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Load model
            logger.info("Loading model...")
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float32,
                low_cpu_mem_usage=True
            )
            
            # Set model to evaluation mode
            self.model.eval()
            
            # Create text generation pipeline
            logger.info("Creating text generation pipeline...")
            self.generator = pipeline(
                'text-generation',
                model=self.model,
                tokenizer=self.tokenizer,
                device=-1  # -1 for CPU, 0 for GPU
            )
            
            logger.info(f"✓ Model {model_name} loaded successfully!")
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise e
    
    def generate_text(self, prompt, max_length=500, temperature=0.7, top_p=0.9, top_k=50):
        """
        Generate text using the loaded model
        
        Args:
            prompt (str): Input text prompt
            max_length (int): Maximum length of generated text
            temperature (float): Creativity level (0.1-1.0)
                - Lower (0.1-0.5): More focused and deterministic
                - Higher (0.7-1.0): More creative and diverse
            top_p (float): Nucleus sampling parameter (0.0-1.0)
            top_k (int): Top-k sampling parameter
        
        Returns:
            str: Generated text string
        """
        try:
            logger.info(f"Generating text with prompt length: {len(prompt)}")
            
            # Generate text
            result = self.generator(
                prompt,
                max_length=max_length,
                temperature=temperature,
                top_p=top_p,
                top_k=top_k,
                num_return_sequences=1,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
                repetition_penalty=1.2,  # Avoid repetition
                no_repeat_ngram_size=3   # Avoid repeating 3-grams
            )
            
            # Extract generated text
            generated_text = result[0]['generated_text']
            
            # Remove the prompt from output
            if generated_text.startswith(prompt):
                generated_text = generated_text[len(prompt):].strip()
            
            logger.info(f"✓ Text generated successfully (length: {len(generated_text)})")
            return generated_text
            
        except Exception as e:
            logger.error(f"Error generating text: {e}")
            raise e
    
    def generate_with_tokens(self, prompt, max_new_tokens=300, temperature=0.7):
        """
        Generate text using token-based length control
        
        Args:
            prompt (str): Input text prompt
            max_new_tokens (int): Maximum number of new tokens to generate
            temperature (float): Creativity level
        
        Returns:
            str: Generated text
        """
        try:
            # Tokenize input
            inputs = self.tokenizer(prompt, return_tensors="pt")
            input_length = inputs['input_ids'].shape[1]
            
            # Generate
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs['input_ids'],
                    max_new_tokens=max_new_tokens,
                    temperature=temperature,
                    top_p=0.9,
                    top_k=50,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                    repetition_penalty=1.2
                )
            
            # Decode output
            generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Remove prompt from output
            if generated_text.startswith(prompt):
                generated_text = generated_text[len(prompt):].strip()
            
            return generated_text
            
        except Exception as e:
            logger.error(f"Error in token-based generation: {e}")
            raise e
    
    def get_model_info(self):
        """Get information about the loaded model"""
        try:
            info = {
                "model_name": self.model_name,
                "vocab_size": self.tokenizer.vocab_size,
                "model_type": self.model.config.model_type,
                "max_position_embeddings": getattr(self.model.config, 'max_position_embeddings', 'N/A'),
                "num_parameters": sum(p.numel() for p in self.model.parameters()),
                "num_parameters_human": f"{sum(p.numel() for p in self.model.parameters()) / 1e6:.1f}M"
            }
            return info
        except Exception as e:
            logger.error(f"Error getting model info: {e}")
            return {"error": str(e)}
    
    def count_tokens(self, text):
        """Count number of tokens in text"""
        tokens = self.tokenizer.encode(text)
        return len(tokens)


# Singleton instance (loaded once)
_model_instance = None

def get_model(model_name="gpt2"):
    """
    Get or create model instance
    Uses singleton pattern to avoid loading model multiple times
    """
    global _model_instance
    if _model_instance is None:
        logger.info("Creating new model instance...")
        _model_instance = AIWriterModel(model_name)
    return _model_instance

def reload_model(model_name="gpt2"):
    """Force reload model with different model name"""
    global _model_instance
    logger.info(f"Reloading model: {model_name}")
    _model_instance = AIWriterModel(model_name)
    return _model_instance