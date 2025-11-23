from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import logging
import uvicorn
from typing import Optional
from model import get_model
from prompts import PromptTemplates
from config import Config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Writer API",
    description="Generate high-quality content with AI-powered writing tools",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if Config.CORS_ORIGINS == "*" else Config.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global model instance
model = None


# Pydantic Models (Request/Response schemas)
class GenerateRequest(BaseModel):
    input: str = Field(..., min_length=1, description="Input text for content generation")
    type: str = Field(default="blog", description="Type of content to generate")
    max_length: Optional[int] = Field(default=500, ge=50, le=2000, description="Maximum length of generated content")
    temperature: Optional[float] = Field(default=0.7, ge=0.1, le=1.0, description="Temperature for text generation")

    class Config:
        schema_extra = {
            "example": {
                "input": "The benefits of artificial intelligence in healthcare",
                "type": "blog",
                "max_length": 500,
                "temperature": 0.7
            }
        }


class GenerateResponse(BaseModel):
    success: bool
    content: str
    type: str
    input_length: int
    output_length: int


class TemplateRequest(BaseModel):
    templateName: str = Field(..., min_length=1)
    templateContent: str = Field(..., min_length=1)


class HealthResponse(BaseModel):
    status: str
    message: str
    model_loaded: bool
    model_name: Optional[str]


# Startup event - Load model
@app.on_event("startup")
async def startup_event():
    """Load model on startup"""
    global model
    try:
        logger.info("=" * 60)
        logger.info("🚀 FastAPI Server Starting...")
        logger.info("=" * 60)
        logger.info("Loading AI model...")
        model = get_model(Config.MODEL_NAME)
        logger.info("=" * 60)
        logger.info("✓ Model loaded successfully!")
        logger.info("=" * 60)
    except Exception as e:
        logger.error(f"❌ Failed to load model: {e}")


# Routes
@app.get("/")
async def home():
    """Home route"""
    return {
        "message": "AI Writer API is running",
        "version": "1.0.0",
        "status": "online",
        "docs": "/docs",
        "endpoints": {
            "generate": "/api/generate [POST]",
            "health": "/api/health [GET]",
            "model_info": "/api/model-info [GET]",
            "create_template": "/api/create-template [POST]"
        }
    }


@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "message": "Server is running",
        "model_loaded": model is not None,
        "model_name": Config.MODEL_NAME if model else None
    }


@app.get("/api/model-info")
async def model_info():
    """Get model information"""
    if model is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded"
        )
    
    try:
        info = model.get_model_info()
        return {
            "success": True,
            "model_info": info
        }
    except Exception as e:
        logger.error(f"Error getting model info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate", response_model=GenerateResponse)
async def generate_content(request: GenerateRequest):
    """
    Generate AI content
    
    - **input**: Text input for content generation
    - **type**: Type of content (blog, email, copy, seo, video, summarize)
    - **max_length**: Maximum length of generated content (50-2000)
    - **temperature**: Creativity level (0.1-1.0)
    """
    try:
        # Check if model is loaded
        if model is None:
            raise HTTPException(
                status_code=503,
                detail="Model not loaded. Please wait and try again."
            )
        
        # Log request
        logger.info(f"📝 Generating {request.type} content...")
        logger.info(f"   Input length: {len(request.input)} characters")
        logger.info(f"   Max length: {request.max_length}")
        logger.info(f"   Temperature: {request.temperature}")
        
        # Generate prompt
        prompt = PromptTemplates.get_prompt(request.type, request.input)
        logger.info(f"   Prompt created (length: {len(prompt)})")
        
        # Generate content
        generated_text = model.generate_text(
            prompt=prompt,
            max_length=request.max_length,
            temperature=request.temperature,
            top_p=Config.TOP_P
        )
        
        # Clean output
        cleaned_text = PromptTemplates.clean_output(generated_text, request.type)
        
        logger.info(f"✓ Content generated successfully!")
        logger.info(f"   Output length: {len(cleaned_text)} characters")
        
        return {
            "success": True,
            "content": cleaned_text,
            "type": request.type,
            "input_length": len(request.input),
            "output_length": len(cleaned_text)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error generating content: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/create-template")
async def create_template(request: TemplateRequest):
    """
    Create custom template
    
    - **templateName**: Name of the template
    - **templateContent**: Content of the template
    """
    try:
        logger.info(f"📄 Template created: {request.templateName}")
        
        return {
            "success": True,
            "message": "Template created successfully",
            "template": {
                "name": request.templateName,
                "content": request.templateContent,
                "created_at": "2024-01-01T00:00:00Z"
            }
        }
        
    except Exception as e:
        logger.error(f"Error creating template: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Exception handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    """Handle 404 errors"""
    return JSONResponse(
        status_code=404,
        content={
            "success": False,
            "error": "Route not found",
            "message": "The requested endpoint does not exist"
        }
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: Exception):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "message": "Something went wrong on the server"
        }
    )


# Run server
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🚀 AI Writer FastAPI Server Starting...")
    print("=" * 60)
    print(f"📍 Server URL: http://{Config.HOST}:{Config.PORT}")
    print(f"📚 API Docs: http://{Config.HOST}:{Config.PORT}/docs")
    print(f"🤖 AI Model: {Config.MODEL_NAME}")
    print(f"🔧 Debug Mode: {Config.DEBUG}")
    print(f"🌐 CORS Origins: {Config.CORS_ORIGINS}")
    print("=" * 60)
    print("\n📋 Available Endpoints:")
    print(f"   • GET  /                    - Home")
    print(f"   • GET  /api/health          - Health Check")
    print(f"   • GET  /api/model-info      - Model Information")
    print(f"   • POST /api/generate        - Generate Content")
    print(f"   • POST /api/create-template - Create Template")
    print(f"   • GET  /docs                - Interactive API Documentation")
    print("=" * 60)
    print("\n⏳ Server is starting... Please wait for model to load.\n")
    
    uvicorn.run(
        "app:app",
        host=Config.HOST,
        port=Config.PORT,
        reload=Config.DEBUG,
        log_level="info"
    )