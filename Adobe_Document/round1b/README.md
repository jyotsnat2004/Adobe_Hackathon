# Round 1B: Persona-Driven Document Intelligence

## Overview

This module implements intelligent document analysis that extracts and prioritizes the most relevant sections from document collections based on specific personas and job requirements.

## Features

- **Persona-Specific Analysis**: Tailored content extraction for different user types
- **Multi-Document Intelligence**: Processes collections of related documents
- **Relevance Ranking**: Prioritizes sections based on job-to-be-done criteria
- **Sub-Section Analysis**: Granular content extraction and refinement
- **TF-IDF Vectorization**: Advanced similarity analysis using statistical methods

## Files

- `persona_analysis.py`: Entry point for persona-driven analysis
- `persona_analyzer.py`: Core analysis and ranking logic
- `approach_explanation.md`: Detailed methodology explanation
- `sample_config.json`: Example configuration file

## Usage

### Docker (Recommended)
```bash
# Build the image
docker build --platform linux/amd64 -t pdf-intelligence:latest .

# Run Round 1B
docker run --rm -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output --network none pdf-intelligence:latest python round1b/persona_analysis.py
```

### Direct Execution
```bash
# From project root
python round1b/persona_analysis.py
```

## Configuration

Create a `config.json` file in the input directory:

```json
{
  "persona": "PhD Researcher in Computational Biology",
  "job_to_be_done": "Prepare a comprehensive literature review focusing on methodologies, datasets, and performance benchmarks"
}
```

## Input/Output

### Input
- Place PDF files in the `/app/input` directory
- Include `config.json` for persona and job configuration
- Supports 3-10 related PDFs

### Output
- Generates `persona_analysis.json` in the output directory
- Output format:
```json
{
  "metadata": {
    "input_documents": ["doc1.pdf", "doc2.pdf"],
    "persona": "Research Analyst",
    "job_to_be_done": "Analyze market trends",
    "processing_timestamp": "2024-01-01T12:00:00Z"
  },
  "extracted_sections": [
    {
      "document": "doc1.pdf",
      "page_number": 5,
      "section_title": "Market Analysis",
      "importance_rank": 0.95
    }
  ],
  "sub_section_analysis": [
    {
      "document": "doc1.pdf",
      "page_number": 5,
      "refined_text": "Key market insights...",
      "importance_rank": 0.92
    }
  ]
}
```

## Supported Personas

### Predefined Personas
- **Researchers**: Focus on methodology, results, conclusions, statistical analysis
- **Students**: Emphasize concepts, definitions, examples, fundamental principles
- **Analysts**: Prioritize trends, performance metrics, comparative analysis
- **Managers**: Target strategic overviews, executive summaries, planning content
- **Journalists**: Seek news angles, quotes, background context, timelines

### Custom Personas
The system can handle any persona by extracting relevant keywords from the description.

## Job-to-Be-Done Examples

### Academic Research
- "Prepare a comprehensive literature review focusing on methodologies"
- "Identify key concepts for exam preparation"
- "Analyze research gaps and future directions"

### Business Analysis
- "Analyze revenue trends and market positioning"
- "Compare competitive strategies and performance metrics"
- "Evaluate investment opportunities and risks"

### Technical Review
- "Review system architecture and implementation details"
- "Assess performance benchmarks and optimization strategies"
- "Analyze scalability and efficiency considerations"

## Algorithm Details

### Relevance Scoring
1. **Persona Relevance**: Keyword matching with persona-specific terms
2. **Job Relevance**: Alignment with job-to-be-done requirements
3. **Content Quality**: Text length, structure, and information density
4. **Positional Importance**: Location within document hierarchy

### TF-IDF Analysis
- **Vectorization**: Converts text to numerical vectors
- **Cosine Similarity**: Measures content relevance and relationships
- **Clustering**: Identifies related sections across documents

### Sub-Section Extraction
- **Paragraph Analysis**: Granular content scoring
- **Keyword Density**: Relevance based on term frequency
- **Information Completeness**: Quality assessment of content snippets

## Performance Characteristics

- **Execution Time**: < 60 seconds for 3-5 documents
- **Memory Usage**: Optimized for 16GB RAM systems
- **CPU Usage**: Efficient for 8-core systems
- **Model Size**: < 1GB (no external models)

## Testing

Run the test suite to verify functionality:
```bash
python test_system.py
```

## Error Handling

The system gracefully handles:
- Missing configuration files
- Unsupported document formats
- Processing failures
- Empty or corrupted documents

Error outputs include:
```json
{
  "metadata": {
    "input_documents": ["doc1.pdf"],
    "persona": "Research Analyst",
    "job_to_be_done": "Analyze content",
    "processing_timestamp": "2024-01-01T12:00:00Z",
    "error": "Error description"
  },
  "extracted_sections": [],
  "sub_section_analysis": []
}
```

## Constraints Compliance

✅ **Execution Time**: < 60 seconds for 3-5 documents  
✅ **Network**: No internet access required  
✅ **Model Size**: < 1GB (no external models)  
✅ **Architecture**: AMD64 compatible  
✅ **Runtime**: CPU-only processing  
✅ **Memory**: Optimized for 16GB RAM systems

## Methodology

See `approach_explanation.md` for detailed methodology explanation (300-500 words) covering:
- Multi-stage analysis pipeline
- Statistical text analysis
- Semantic understanding
- Relevance ranking algorithms
- Quality assurance measures 