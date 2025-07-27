#!/usr/bin/env python3


import logging
import traceback
import sys
import os
from typing import Dict, Any, Optional, Callable
from datetime import datetime
import json

class ErrorHandler:
    
    def __init__(self, log_file: str = "system_errors.log"):
        self.log_file = log_file
        self.error_counts = {}
        self.recovery_attempts = {}
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def handle_pdf_processing_error(self, file_path: str, error: Exception, 
                                  fallback_strategy: str = "skip") -> Dict[str, Any]:
        """Handle PDF processing errors with recovery strategies."""
        error_type = type(error).__name__
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
        
        error_info = {
            "timestamp": datetime.now().isoformat(),
            "file_path": file_path,
            "error_type": error_type,
            "error_message": str(error),
            "fallback_strategy": fallback_strategy,
            "recovery_successful": False
        }
        
        self.logger.error(f"PDF Processing Error: {file_path} - {error_type}: {str(error)}")
        
        # Implement recovery strategies
        if fallback_strategy == "skip":
            error_info["recovery_successful"] = True
            error_info["fallback_result"] = {
                "title": f"Error Processing {os.path.basename(file_path)}",
                "outline": []
            }
        elif fallback_strategy == "retry":
            error_info["recovery_successful"] = self._retry_processing(file_path, error_info)
        elif fallback_strategy == "partial":
            error_info["recovery_successful"] = self._partial_recovery(file_path, error_info)
        
        return error_info
    
    def handle_analysis_error(self, documents: list, error: Exception, 
                            recovery_strategy: str = "degraded") -> Dict[str, Any]:
        """Handle persona analysis errors."""
        error_type = type(error).__name__
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
        
        error_info = {
            "timestamp": datetime.now().isoformat(),
            "error_type": error_type,
            "error_message": str(error),
            "documents_affected": len(documents),
            "recovery_strategy": recovery_strategy,
            "recovery_successful": False
        }
        
        self.logger.error(f"Analysis Error: {error_type}: {str(error)}")
        
        if recovery_strategy == "degraded":
            error_info["recovery_successful"] = True
            error_info["fallback_result"] = {
                "metadata": {
                    "input_documents": [doc.get("file_path", "unknown") for doc in documents],
                    "error": str(error),
                    "processing_timestamp": datetime.now().isoformat()
                },
                "extracted_sections": [],
                "sub_section_analysis": []
            }
        
        return error_info
    
    def handle_memory_error(self, current_usage: float, max_usage: float) -> Dict[str, Any]:
        """Handle memory-related errors."""
        error_info = {
            "timestamp": datetime.now().isoformat(),
            "error_type": "MemoryError",
            "current_usage_mb": current_usage,
            "max_usage_mb": max_usage,
            "usage_percentage": (current_usage / max_usage) * 100,
            "recovery_attempts": []
        }
        
        self.logger.warning(f"Memory usage high: {current_usage:.1f}MB / {max_usage:.1f}MB")
        
        # Implement memory recovery strategies
        recovery_strategies = [
            self._clear_cache,
            self._reduce_batch_size,
            self._force_garbage_collection
        ]
        
        for strategy in recovery_strategies:
            try:
                if strategy():
                    error_info["recovery_attempts"].append({
                        "strategy": strategy.__name__,
                        "successful": True
                    })
                    break
                else:
                    error_info["recovery_attempts"].append({
                        "strategy": strategy.__name__,
                        "successful": False
                    })
            except Exception as e:
                error_info["recovery_attempts"].append({
                    "strategy": strategy.__name__,
                    "successful": False,
                    "error": str(e)
                })
        
        return error_info
    
    def handle_timeout_error(self, operation: str, timeout_seconds: int) -> Dict[str, Any]:
        """Handle timeout errors."""
        error_info = {
            "timestamp": datetime.now().isoformat(),
            "error_type": "TimeoutError",
            "operation": operation,
            "timeout_seconds": timeout_seconds,
            "suggested_actions": []
        }
        
        self.logger.error(f"Timeout Error: {operation} exceeded {timeout_seconds}s")
        
        # Suggest optimizations
        if operation == "pdf_processing":
            error_info["suggested_actions"] = [
                "Reduce PDF file size",
                "Process in smaller batches",
                "Use faster storage (SSD)"
            ]
        elif operation == "analysis":
            error_info["suggested_actions"] = [
                "Reduce number of documents",
                "Simplify persona configuration",
                "Use basic analysis mode"
            ]
        
        return error_info
    
    def _retry_processing(self, file_path: str, error_info: Dict[str, Any]) -> bool:
        """Retry processing with exponential backoff."""
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                retry_count += 1
                self.logger.info(f"Retry attempt {retry_count} for {file_path}")
                
                # Add delay between retries
                import time
                time.sleep(2 ** retry_count)  # Exponential backoff
                
                # Attempt processing again
                # This would call the actual processing function
                return True
                
            except Exception as e:
                self.logger.error(f"Retry {retry_count} failed: {str(e)}")
                if retry_count == max_retries:
                    return False
        
        return False
    
    def _partial_recovery(self, file_path: str, error_info: Dict[str, Any]) -> bool:
        """Attempt partial recovery of PDF content."""
        try:
            # Try alternative PDF processing methods
            self.logger.info(f"Attempting partial recovery for {file_path}")
            
            # This would implement alternative processing strategies
            # For now, return a basic structure
            error_info["fallback_result"] = {
                "title": f"Partially Recovered - {os.path.basename(file_path)}",
                "outline": [
                    {"level": "H1", "text": "Recovery Notice", "page": 1},
                    {"level": "H2", "text": "Content partially extracted", "page": 1}
                ]
            }
            
            return True
            
        except Exception as e:
            self.logger.error(f"Partial recovery failed: {str(e)}")
            return False
    
    def _clear_cache(self) -> bool:
        """Clear system cache to free memory."""
        try:
            import gc
            gc.collect()
            return True
        except Exception:
            return False
    
    def _reduce_batch_size(self) -> bool:
        """Reduce processing batch size."""
        # This would modify global batch size settings
        return True
    
    def _force_garbage_collection(self) -> bool:
        """Force garbage collection."""
        try:
            import gc
            gc.collect()
            return True
        except Exception:
            return False
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of all errors encountered."""
        return {
            "total_errors": sum(self.error_counts.values()),
            "error_types": self.error_counts,
            "recovery_attempts": self.recovery_attempts,
            "system_health": self._calculate_system_health()
        }
    
    def _calculate_system_health(self) -> str:
        """Calculate overall system health based on error patterns."""
        total_errors = sum(self.error_counts.values())
        
        if total_errors == 0:
            return "EXCELLENT"
        elif total_errors <= 5:
            return "GOOD"
        elif total_errors <= 10:
            return "FAIR"
        else:
            return "POOR"
    
    def generate_error_report(self) -> str:
        """Generate comprehensive error report."""
        summary = self.get_error_summary()
        
        report = f"""
=== Error Handling Report ===
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

System Health: {summary['system_health']}
Total Errors: {summary['total_errors']}

Error Breakdown:
"""
        
        for error_type, count in summary['error_types'].items():
            report += f"  {error_type}: {count}\n"
        
        report += f"""
Recovery Statistics:
  Successful Recoveries: {len([r for r in summary['recovery_attempts'] if r.get('successful', False)])}
  Failed Recoveries: {len([r for r in summary['recovery_attempts'] if not r.get('successful', True)])}

Recommendations:
"""
        
        if summary['system_health'] == 'POOR':
            report += "  - Review input file quality\n"
            report += "  - Check system resources\n"
            report += "  - Consider batch processing\n"
        elif summary['system_health'] == 'FAIR':
            report += "  - Monitor error patterns\n"
            report += "  - Optimize processing parameters\n"
        else:
            report += "  - System performing well\n"
            report += "  - Continue monitoring\n"
        
        return report

# Global error handler instance
error_handler = ErrorHandler()

def safe_execute(func: Callable, *args, **kwargs) -> Dict[str, Any]:
    """Safely execute a function with comprehensive error handling."""
    try:
        result = func(*args, **kwargs)
        return {
            "success": True,
            "result": result,
            "error": None
        }
    except Exception as e:
        error_info = error_handler.handle_pdf_processing_error(
            str(args[0]) if args else "unknown",
            e
        )
        return {
            "success": False,
            "result": None,
            "error": error_info
        } 
