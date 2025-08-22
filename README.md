# Document Metadata Extractor

A FastAPI service that extracts metadata from documents (PDF, XLS, JPG, etc.) using Docling for prompt generation.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the server:
```bash
python main.py
```

The API will be available at `http://localhost:5000`

## Usage

### Extract Document Metadata

**POST** `/extract-metadata`

Upload a document file to extract metadata for prompt generation.

**Supported formats:**
- PDF (.pdf)
- Excel (.xls, .xlsx)  
- Images (.jpg, .jpeg, .png, .tiff)
- Word documents (.doc, .docx)
- Text files (.txt)

**Example using curl:**
```bash
curl -X POST "http://localhost:5000/extract-metadata" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@your_document.pdf"
```

**Response:**
```json
{
  "success": true,
  "metadata": {
    "document_type": "pdf",
    "page_count": 5,
    "text_preview": "Document content preview...",
    "tables_count": 2,
    "images_count": 1,
    "structure_elements": ["Paragraph", "Table", "Title"],
    "filename": "your_document.pdf",
    "file_size": 1024000,
    "mime_type": "application/pdf",
    "file_extension": ".pdf"
  },
  "prompt_context": "Document Analysis:\n- Type: pdf\n- Pages: 5\n- Tables: 2\n- Images: 1\n- Content preview: Document content preview...\n- Structure: Paragraph, Table, Title"
}
```

## API Documentation

Visit `http://localhost:5000/docs` for interactive API documentation.

## Health Check

**GET** `/health` - Returns service health status