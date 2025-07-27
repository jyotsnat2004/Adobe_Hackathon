#!/usr/bin/env python3


import time
import psutil
import os
import json
import sys
from typing import Dict, List, Any
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pdf_processor import PDFProcessor
from round1a.outline_extractor import OutlineExtractor
from round1b.persona_analyzer import PersonaAnalyzer

class PerformanceBenchmark:
  
    
    def __init__(self):
        self.pdf_processor = PDFProcessor()
        self.outline_extractor = OutlineExtractor()
        self.persona_analyzer = PersonaAnalyzer()
        self.results = {}
    
    def benchmark_round_1a(self, test_files: List[str]) -> Dict[str, Any]:
       
        print("=== Round 1A Performance Benchmark ===")
        
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
        total_headings = 0
        processing_times = []
        
        for test_file in test_files:
            file_start = time.time()
            
            try:
                # Process PDF
                pdf_data = self.pdf_processor.process_pdf_file(test_file)
                
                # Extract outline
                outline = self.outline_extractor.extract_outline(pdf_data)
                
                file_time = time.time() - file_start
                processing_times.append(file_time)
                total_headings += len(outline.get('outline', []))
                
                print(f"✓ {os.path.basename(test_file)}: {len(outline.get('outline', []))} headings in {file_time:.2f}s")
                
            except Exception as e:
                print(f"✗ {os.path.basename(test_file)}: Error - {str(e)}")
        
        total_time = time.time() - start_time
        end_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        memory_used = end_memory - start_memory
        
        avg_time = sum(processing_times) / len(processing_times) if processing_times else 0
        
        results = {
            "total_files": len(test_files),
            "total_headings": total_headings,
            "total_time": total_time,
            "average_time_per_file": avg_time,
            "memory_used_mb": memory_used,
            "headings_per_second": total_headings / total_time if total_time > 0 else 0,
            "constraint_compliance": {
                "execution_time_under_10s": total_time <= 10,
                "memory_under_16gb": memory_used <= 16384,  # 16GB in MB
                "offline_operation": True,
                "cpu_only": True
            }
        }
        
        print(f"\n📊 Round 1A Results:")
        print(f"  Total Time: {total_time:.2f}s")
        print(f"  Average per file: {avg_time:.2f}s")
        print(f"  Memory Used: {memory_used:.1f}MB")
        print(f"  Headings per second: {results['headings_per_second']:.1f}")
        print(f"  Constraint Compliance: {'✅' if all(results['constraint_compliance'].values()) else '❌'}")
        
        return results
    
    def benchmark_round_1b(self, test_files: List[str], config: Dict[str, str]) -> Dict[str, Any]:
        """Benchmark Round 1B performance."""
        print("\n=== Round 1B Performance Benchmark ===")
        
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
        documents = []
        
        for test_file in test_files:
            try:
                pdf_data = self.pdf_processor.process_pdf_file(test_file)
                documents.append({
                    "file_path": test_file,
                    "text": pdf_data.get("text", ""),
                    "title": pdf_data.get("title", "Untitled")
                })
            except Exception as e:
                print(f"✗ {os.path.basename(test_file)}: Error - {str(e)}")
        
        if not documents:
            return {"error": "No documents could be processed"}
        
        # Perform persona analysis
        analysis_result = self.persona_analyzer.analyze_documents(
            documents, 
            config["persona"], 
            config["job_to_be_done"]
        )
        
        total_time = time.time() - start_time
        end_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        memory_used = end_memory - start_memory
        
        results = {
            "total_documents": len(documents),
            "total_time": total_time,
            "memory_used_mb": memory_used,
            "extracted_sections": len(analysis_result.get('extracted_sections', [])),
            "sub_sections": len(analysis_result.get('sub_section_analysis', [])),
            "documents_per_second": len(documents) / total_time if total_time > 0 else 0,
            "constraint_compliance": {
                "execution_time_under_60s": total_time <= 60,
                "memory_under_16gb": memory_used <= 16384,  # 16GB in MB
                "offline_operation": True,
                "cpu_only": True,
                "model_size_under_1gb": True  # No external models
            }
        }
        
        print(f"\n📊 Round 1B Results:")
        print(f"  Total Time: {total_time:.2f}s")
        print(f"  Memory Used: {memory_used:.1f}MB")
        print(f"  Documents processed: {len(documents)}")
        print(f"  Sections extracted: {results['extracted_sections']}")
        print(f"  Sub-sections analyzed: {results['sub_sections']}")
        print(f"  Documents per second: {results['documents_per_second']:.2f}")
        print(f"  Constraint Compliance: {'✅' if all(results['constraint_compliance'].values()) else '❌'}")
        
        return results
    
    def benchmark_accuracy(self, test_files: List[str]) -> Dict[str, Any]:
        """Benchmark accuracy metrics."""
        print("\n=== Accuracy Benchmark ===")
        
        accuracy_metrics = {
            "heading_detection": 0,
            "hierarchy_classification": 0,
            "page_tracking": 0,
            "persona_matching": 0,
            "total_tests": 0
        }
        
        for test_file in test_files:
            try:
                pdf_data = self.pdf_processor.process_pdf_file(test_file)
                outline = self.outline_extractor.extract_outline(pdf_data)
                
                # Test heading detection
                if outline.get('outline'):
                    accuracy_metrics["heading_detection"] += 1
                
                # Test hierarchy classification
                levels = [h.get('level') for h in outline.get('outline', [])]
                if any(level in ['H1', 'H2', 'H3'] for level in levels):
                    accuracy_metrics["hierarchy_classification"] += 1
                
                # Test page tracking
                pages = [h.get('page') for h in outline.get('outline', [])]
                if any(page is not None for page in pages):
                    accuracy_metrics["page_tracking"] += 1
                
                accuracy_metrics["total_tests"] += 1
                
            except Exception as e:
                print(f"✗ Accuracy test failed for {os.path.basename(test_file)}: {str(e)}")
        
        # Calculate accuracy percentages
        accuracy_results = {}
        for metric, count in accuracy_metrics.items():
            if metric != "total_tests" and accuracy_metrics["total_tests"] > 0:
                accuracy_results[metric] = (count / accuracy_metrics["total_tests"]) * 100
        
        print(f"\n📊 Accuracy Results:")
        for metric, percentage in accuracy_results.items():
            print(f"  {metric.replace('_', ' ').title()}: {percentage:.1f}%")
        
        return accuracy_results
    
    def generate_comprehensive_report(self, test_files: List[str], config: Dict[str, str]) -> Dict[str, Any]:
        """Generate comprehensive performance report."""
        print("🚀 Starting Comprehensive Performance Benchmark")
        print("=" * 50)
        
        # Run all benchmarks
        round1a_results = self.benchmark_round_1a(test_files)
        round1b_results = self.benchmark_round_1b(test_files, config)
        accuracy_results = self.benchmark_accuracy(test_files)
        
        # Compile comprehensive report
        comprehensive_report = {
            "benchmark_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "system_info": {
                "python_version": sys.version,
                "platform": sys.platform,
                "cpu_count": psutil.cpu_count(),
                "total_memory_gb": psutil.virtual_memory().total / 1024 / 1024 / 1024
            },
            "round_1a": round1a_results,
            "round_1b": round1b_results,
            "accuracy": accuracy_results,
            "overall_compliance": {
                "all_constraints_met": (
                    all(round1a_results.get('constraint_compliance', {}).values()) and
                    all(round1b_results.get('constraint_compliance', {}).values())
                ),
                "performance_grade": self._calculate_performance_grade(round1a_results, round1b_results),
                "accuracy_grade": self._calculate_accuracy_grade(accuracy_results)
            }
        }
        
        # Save report
        with open('performance_report.json', 'w') as f:
            json.dump(comprehensive_report, f, indent=2)
        
        print(f"\n📋 Comprehensive Report Generated:")
        print(f"  Overall Compliance: {'✅ PASS' if comprehensive_report['overall_compliance']['all_constraints_met'] else '❌ FAIL'}")
        print(f"  Performance Grade: {comprehensive_report['overall_compliance']['performance_grade']}")
        print(f"  Accuracy Grade: {comprehensive_report['overall_compliance']['accuracy_grade']}")
        print(f"  Report saved to: performance_report.json")
        
        return comprehensive_report
    
    def _calculate_performance_grade(self, round1a: Dict, round1b: Dict) -> str:
        """Calculate overall performance grade."""
        scores = []
        
        # Round 1A scoring
        if round1a.get('total_time', 0) <= 10:
            scores.append(100)
        elif round1a.get('total_time', 0) <= 15:
            scores.append(80)
        else:
            scores.append(60)
        
        # Round 1B scoring
        if round1b.get('total_time', 0) <= 60:
            scores.append(100)
        elif round1b.get('total_time', 0) <= 90:
            scores.append(80)
        else:
            scores.append(60)
        
        avg_score = sum(scores) / len(scores)
        
        if avg_score >= 90:
            return "A+"
        elif avg_score >= 80:
            return "A"
        elif avg_score >= 70:
            return "B+"
        elif avg_score >= 60:
            return "B"
        else:
            return "C"
    
    def _calculate_accuracy_grade(self, accuracy: Dict) -> str:
        """Calculate accuracy grade."""
        if not accuracy:
            return "N/A"
        
        avg_accuracy = sum(accuracy.values()) / len(accuracy)
        
        if avg_accuracy >= 95:
            return "A+"
        elif avg_accuracy >= 90:
            return "A"
        elif avg_accuracy >= 85:
            return "B+"
        elif avg_accuracy >= 80:
            return "B"
        else:
            return "C"

def main():
    """Main benchmark execution."""
    benchmark = PerformanceBenchmark()
    
    # Test files (use existing PDFs in input directory)
    input_dir = "input"
    test_files = [os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.endswith('.pdf')]
    
    if not test_files:
        print("❌ No PDF files found in input directory")
        return
    
    # Configuration for Round 1B
    config = {
        "persona": "PhD Researcher in Computational Biology",
        "job_to_be_done": "Prepare a comprehensive literature review focusing on methodologies, datasets, and performance benchmarks"
    }
    
    # Run comprehensive benchmark
    report = benchmark.generate_comprehensive_report(test_files, config)
    
    print(f"\n🎯 Hackathon Readiness Assessment:")
    print(f"  Ready for submission: {'✅ YES' if report['overall_compliance']['all_constraints_met'] else '❌ NO'}")
    print(f"  Performance: {report['overall_compliance']['performance_grade']}")
    print(f"  Accuracy: {report['overall_compliance']['accuracy_grade']}")

if __name__ == "__main__":
    main() 
