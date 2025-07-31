# -*- coding: utf-8 -*-
"""
File downloader tool for downloading PDF files and calculating MD5
"""

import os
import hashlib
import requests
import tempfile
from pathlib import Path
from typing import Optional


class FileDownloaderTool:
    """Tool for downloading files and calculating MD5 hashes"""
    
    def __init__(self, download_dir: Optional[str] = None):
        """
        Initialize the file downloader tool
        
        Args:
            download_dir: Directory to store downloaded files
        """
        self.download_dir = download_dir or tempfile.gettempdir()
    
    def download_pdf(self, pdf_url: str, filename: Optional[str] = None) -> str:
        """
        Download PDF file from URL
        
        Args:
            pdf_url: URL of the PDF file
            filename: Optional filename for the downloaded file
            
        Returns:
            Path to the downloaded PDF file
            
        Raises:
            Exception: If download fails
        """
        try:
            # Create download directory if it doesn't exist
            os.makedirs(self.download_dir, exist_ok=True)
            
            # Generate filename if not provided
            if filename is None:
                filename = f"downloaded_pdf_{hashlib.md5(pdf_url.encode()).hexdigest()[:8]}.pdf"
            
            pdf_path = os.path.join(self.download_dir, filename)
            
            # Download the file
            response = requests.get(pdf_url, stream=True)
            response.raise_for_status()
            
            with open(pdf_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            
            return pdf_path
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to download PDF from {pdf_url}: {e}")
        except Exception as e:
            raise Exception(f"Error downloading PDF: {e}")
    
    def calculate_file_md5(self, file_path: str) -> str:
        """
        Calculate MD5 hash of a file
        
        Args:
            file_path: Path to the file
            
        Returns:
            MD5 hash string
            
        Raises:
            Exception: If file doesn't exist or can't be read
        """
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            
            return hash_md5.hexdigest()
            
        except Exception as e:
            raise Exception(f"Error calculating MD5 for {file_path}: {e}")
    
    def download_and_verify_pdf(self, pdf_url: str, expected_md5: Optional[str] = None) -> tuple[str, str]:
        """
        Download PDF and optionally verify its MD5 hash
        
        Args:
            pdf_url: URL of the PDF file
            expected_md5: Expected MD5 hash for verification
            
        Returns:
            Tuple of (file_path, actual_md5)
            
        Raises:
            Exception: If download fails or MD5 verification fails
        """
        pdf_path = self.download_pdf(pdf_url)
        actual_md5 = self.calculate_file_md5(pdf_path)
        
        if expected_md5 and actual_md5 != expected_md5:
            raise Exception(f"MD5 verification failed. Expected: {expected_md5}, Got: {actual_md5}")
        
        return pdf_path, actual_md5 