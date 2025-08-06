"""
Test mobile image upload functionality
"""
import unittest
import os


class TestMobileImageUpload(unittest.TestCase):
    """Test mobile-friendly image upload features"""

    def test_mobile_upload_html_structure(self):
        """Test that mobile image upload elements are present in the generated HTML"""
        socket_handlers_path = os.path.join(
            os.path.dirname(__file__), '..', '..',
            'static', 'js', 'socket-handlers.js'
        )
        
        with open(socket_handlers_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check for mobile-specific elements in the innerHTML template
        assert 'file-input-${target.id}' in content
        assert 'upload-btn-${target.id}' in content
        assert 'image-upload-btn' in content
        assert 'capture="environment"' in content
        assert 'accept="image/*,image/gif"' in content

    def test_mobile_upload_function_exists(self):
        """Test that setupMobileImageUpload function exists"""
        ui_handlers_path = os.path.join(
            os.path.dirname(__file__), '..', '..',
            'static', 'js', 'ui-handlers.js'
        )
        
        with open(ui_handlers_path, 'r', encoding='utf-8') as f:
            content = f.read()

        assert 'function setupMobileImageUpload(targetId)' in content
        assert 'fileInput.click()' in content
        assert 'handleFileUpload(e.target.files[0], targetId)' in content

    def test_mobile_css_responsive_styles(self):
        """Test that mobile-responsive CSS styles exist"""
        css_path = os.path.join(
            os.path.dirname(__file__), '..', '..',
            'static', 'css', 'game.css'
        )
        
        with open(css_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check for mobile-specific styles
        assert '.mobile-upload-text' in content
        assert '.image-upload-btn' in content
        assert '@media (max-width: 768px)' in content
        assert '@media (pointer: coarse)' in content
        assert 'display: none' in content  # For hiding elements on different devices

    def test_mobile_upload_disable_logic(self):
        """Test that mobile upload elements are properly disabled after submission"""
        socket_handlers_path = os.path.join(
            os.path.dirname(__file__), '..', '..',
            'static', 'js', 'socket-handlers.js'
        )
        
        with open(socket_handlers_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Find the bribe_submitted handler
        bribe_submitted_start = content.find("socket.on('bribe_submitted'")
        bribe_submitted_end = content.find("});", bribe_submitted_start)
        bribe_submitted_section = content[bribe_submitted_start:bribe_submitted_end + 3]

        # Check for proper disable logic
        assert 'file-input-${data.target_id}' in bribe_submitted_section
        assert 'upload-btn-${data.target_id}' in bribe_submitted_section
        assert 'fileInput.disabled = true' in bribe_submitted_section
        assert 'uploadBtn.disabled = true' in bribe_submitted_section

    def test_mobile_upload_enable_logic(self):
        """Test that mobile upload elements are re-enabled for new rounds"""
        socket_handlers_path = os.path.join(
            os.path.dirname(__file__), '..', '..',
            'static', 'js', 'socket-handlers.js'
        )
        
        with open(socket_handlers_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Find the round_started handler
        round_started_start = content.find("socket.on('round_started'")
        # Find the end of this handler by looking for the next socket.on
        next_socket_start = content.find("socket.on(", round_started_start + 1)
        if next_socket_start == -1:
            next_socket_start = len(content)
        round_started_section = content[round_started_start:next_socket_start]

        # Check for proper enable logic
        assert 'file-input-' in round_started_section
        assert 'upload-btn-' in round_started_section
        assert 'fileInput.disabled = false' in round_started_section
        assert 'uploadBtn.disabled = false' in round_started_section

    def test_setup_mobile_image_upload_called(self):
        """Test that setupMobileImageUpload is called when targets are created"""
        socket_handlers_path = os.path.join(
            os.path.dirname(__file__), '..', '..',
            'static', 'js', 'socket-handlers.js'
        )
        
        with open(socket_handlers_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Find the your_targets handler
        your_targets_start = content.find("socket.on('your_targets'")
        your_targets_end = content.find("});", your_targets_start)
        your_targets_section = content[your_targets_start:your_targets_end + 3]

        # Check that setupMobileImageUpload is called
        assert 'setupMobileImageUpload(target.id)' in your_targets_section


if __name__ == '__main__':
    unittest.main()
