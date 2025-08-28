import unittest
from pathlib import Path


class TestImageOptimization(unittest.TestCase):
    """Test case to ensure image optimization files are properly implemented"""

    def test_image_loading_files_exist(self):
        """Verify that all image loading optimization files exist"""
        # CSS file
        css_path = Path("static/css/components/image-loading.css")
        self.assertTrue(css_path.exists(), "Image loading CSS file should exist")
        
        # JS file
        js_path = Path("static/js/image-loading-optimizer.js")
        self.assertTrue(js_path.exists(), "Image loading optimizer JS file should exist")
        
    def test_logo_files_exist(self):
        """Verify that logo files exist"""
        logo_dir = Path("static/images/logo")
        self.assertTrue((logo_dir / "logo-full.png").exists(), "Full logo image should exist")
        
        
if __name__ == "__main__":
    unittest.main()
