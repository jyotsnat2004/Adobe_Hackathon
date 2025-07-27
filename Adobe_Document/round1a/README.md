# Round 1A: PDF Outline Extraction

## Overview

This module implements intelligent PDF outline extraction that identifies and extracts hierarchical headings (H1, H2, H3) from PDF documents with high accuracy and speed.

## Features

- **Multi-stage Heading Detection**: Combines font analysis, pattern matching, and content analysis
- **Hierarchical Classification**: Automatically assigns H1, H2, H3 levels based on visual and semantic cues
- **Fast Processing**: < 10 seconds for 50-page PDFs
- **Robust Error Handling**: Graceful degradation for problematic PDFs
- **Accurate Page Tracking**: Maintains precise page number information

## Files

- `main.py`: Entry point for PDF outline extraction
- `outline_extractor.py`: Core heading detection and classification logic

## Usage

### Docker (Recommended)
```bash
# Build the image
docker build --platform linux/amd64 -t pdf-intelligence:latest .

# Run Round 1A
docker run --rm -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output --network none pdf-intelligence:latest
```

### Direct Execution
```bash
# From project root
python round1a/main.py
```

## Input/Output

### Input
- Place PDF files in the `/app/input` directory
- Supports multiple PDF files
- Maximum 50 pages per PDF

### Output
- Generates `{filename}.json` for each `{filename}.pdf`
- Output format:
```json
{
  "title": "Document Title",
  "outline": [
    {"level": "H1", "text": "Introduction", "page": 1},
    {"level": "H2", "text": "Background", "page": 2},
    {"level": "H3", "text": "Historical Context", "page": 3}
  ]
}
```

## Algorithm Details

### Heading Detection Methods

1. **Font Analysis**
   - Font size ≥ 16pt → H1
   - Font size ≥ 14pt → H2  
   - Font size ≥ 12pt → H3
   - Bold font weight boosts level by 1

2. **Pattern Matching**
   - ALL CAPS text → H1
   - Numbered headings (1. Introduction) → H1
   - Title Case text → H2
   - Sub-numbered headings (1.1 Background) → H2

3. **Content Analysis**
   - Keywords like "Introduction", "Conclusion", "Abstract" → H1
   - Keywords like "Method", "Results", "Discussion" → H2
   - Keywords like "Overview", "Review" → H3

### Performance Characteristics

- **Execution Time**: < 10 seconds for 50-page PDFs
- **Memory Usage**: Optimized for 16GB RAM systems
- **CPU Usage**: Efficient for 8-core systems
- **Model Size**: < 200MB (no external models)

## Testing

Run the test suite to verify functionality:
```bash
python test_system.py
```

## Error Handling

The system gracefully handles:
- Corrupted PDF files
- Password-protected PDFs
- PDFs with no extractable text
- Unsupported PDF formats

Error outputs include:
```json
{
  "title": "Error Processing {filename}",
  "outline": []
}
```

## Constraints Compliance

✅ **Execution Time**: < 10 seconds for 50-page PDFs  
✅ **Network**: No internet access required  
✅ **Model Size**: < 200MB (no external models)  
✅ **Architecture**: AMD64 compatible  
✅ **Runtime**: CPU-only processing  
✅ **Memory**: Optimized for 16GB RAM systems 