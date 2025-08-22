from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import tempfile
import os
import magic
from docling.document_converter import DocumentConverter
from typing import Dict, Any

app = FastAPI(title="Document Metadata Extractor", version="1.0.0")

SUPPORTED_TYPES = {
    'application/pdf': ['.pdf'],
    'application/vnd.ms-excel': ['.xls'],
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
    'image/jpeg': ['.jpg', '.jpeg'],
    'image/png': ['.png'],
    'image/tiff': ['.tif', '.tiff'],
    'text/plain': ['.txt'],
    'application/msword': ['.doc'],
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx']
}

def extract_metadata_for_prompt(doc_result) -> Dict[str, Any]:
    """Extract relevant metadata from Docling result to use as prompt context"""
    metadata = {
        "document_type": getattr(doc_result.document, 'document_type', 'unknown'),
        "page_count": len(doc_result.document.pages) if hasattr(doc_result.document, 'pages') else 0,
        "text_preview": "",
        "tables_count": 0,
        "images_count": 0,
        "structure_elements": []
    }
    
    # Extract text preview (first 500 characters)
    if hasattr(doc_result.document, 'export_to_markdown'):
        full_text = doc_result.document.export_to_markdown()
        metadata["text_preview"] = full_text[:500] + "..." if len(full_text) > 500 else full_text
    
    # Count structural elements
    if hasattr(doc_result.document, 'body'):
        for element in doc_result.document.body.children:
            element_type = type(element).__name__
            metadata["structure_elements"].append(element_type)
            
            if 'table' in element_type.lower():
                metadata["tables_count"] += 1
            elif 'picture' in element_type.lower() or 'image' in element_type.lower():
                metadata["images_count"] += 1
    
    return metadata

@app.post("/extract-metadata")
async def extract_document_metadata(file: UploadFile = File(...)):
    """
    Extract metadata from uploaded document (PDF, XLS, JPG, etc.) for prompt generation
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
        content = await file.read()
        temp_file.write(content)
        temp_file_path = temp_file.name
    
    try:
        # Detect file type
        mime_type = magic.from_file(temp_file_path, mime=True)
        
        # Validate supported file type
        if mime_type not in SUPPORTED_TYPES:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type: {mime_type}. Supported types: {list(SUPPORTED_TYPES.keys())}"
            )
        
        # Initialize Docling converter
        converter = DocumentConverter()
        
        # Process document
        result = converter.convert(temp_file_path)
        
        # Extract metadata for prompt
        metadata = extract_metadata_for_prompt(result)
        
        # Add file info
        metadata.update({
            "filename": file.filename,
            "file_size": len(content),
            "mime_type": mime_type,
            "file_extension": os.path.splitext(file.filename)[1]
        })
        
        return JSONResponse(content={
            "success": True,
            "metadata": metadata,
            "prompt_context": f"""Document Analysis:
- Type: {metadata['document_type']}
- Pages: {metadata['page_count']}
- Tables: {metadata['tables_count']}
- Images: {metadata['images_count']}
- Content preview: {metadata['text_preview']}
- Structure: {', '.join(set(metadata['structure_elements']))}"""
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")
    
    finally:
        # Clean up temporary file
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

@app.get("/")
async def root():
    return {"message": "Document Metadata Extractor API", "endpoints": ["/extract-metadata"]}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)