import unittest
import tkinter as tk
from tkinter import ttk
from unittest.mock import MagicMock, patch, mock_open
import sys
import os
import json
import shutil
import tempfile
from pathlib import Path

# Add src to path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

# Import the class to test
# We need to mock some things if they are not available, but let's try direct import
try:
    from parsercraft.ide import AdvancedIDE
    from parsercraft.language_config import LanguageConfig
except ImportError:
    # If standard import fails, try relative to script location
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/parsercraft')))
    from ide import AdvancedIDE
    from language_config import LanguageConfig

class TestAdvancedIDE(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create a root window for all tests
        cls.root = tk.Tk()
        cls.root.withdraw() # Hide it

    @classmethod
    def tearDownClass(cls):
        cls.root.destroy()

    def setUp(self):
        # Create a temporary directory for file ops
        self.test_dir = tempfile.mkdtemp()
        self.ide = AdvancedIDE(master=self.root)
        
        # Redirect file operations to test_dir where possible or mock them
        self.ide.current_project = self.test_dir
        
    def tearDown(self):
        self.ide.destroy()
        shutil.rmtree(self.test_dir)

    def test_initial_state(self):
        """Verify the IDE initializes with correct defaults."""
        self.assertIsNotNone(self.ide.editor)
        self.assertIsNotNone(self.ide.console)
        self.assertEqual(self.ide.settings['theme'], 'light')

    def test_zoom_features(self):
        """Test Zoom In/Out/Reset functionality."""
        original_size = self.ide.settings['editor_font_size']
        
        # Test Zoom In
        self.ide._zoom_in()
        self.assertEqual(self.ide.settings['editor_font_size'], original_size + 1)
        
        # Test Zoom Out
        self.ide._zoom_out()
        self.assertEqual(self.ide.settings['editor_font_size'], original_size)
        
        # Test Reset
        self.ide._zoom_in()
        self.ide._reset_zoom()
        self.assertEqual(self.ide.settings['editor_font_size'], 11) # Default is 11

    def test_console_operations(self):
        """Test Clear, Copy, Save console operations."""
        # Setup console text
        self.ide.console.configure(state='normal')
        self.ide.console.insert('1.0', "Test Output")
        self.ide.console.configure(state='disabled')
        
        # Test Clear
        self.ide._clear_console()
        self.assertEqual(self.ide.console.get('1.0', 'end-1c'), "")

        # Test Save (Mock filedialog)
        self.ide.console.configure(state='normal')
        self.ide.console.insert('1.0', "Log Data")
        
        with patch('tkinter.filedialog.asksaveasfilename', return_value=os.path.join(self.test_dir, 'log.txt')):
            self.ide._save_console_output()
            
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, 'log.txt')))
        # Newline handling might vary, just check content presence
        with open(os.path.join(self.test_dir, 'log.txt'), 'r') as f:
            self.assertIn("Log Data", f.read())

    @patch('subprocess.run')
    def test_git_operations(self, mock_run):
        """Test Git Wrappers."""
        # Test Git Init
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "Initialized empty Git repository"
        
        with patch('tkinter.messagebox.showinfo') as mock_info:
            self.ide._git_init()
            # _git_init also calls _update_git_status, so we check for any call, not the last call
            mock_run.assert_any_call(['git', 'init'], cwd=self.test_dir, capture_output=True, text=True)
            mock_info.assert_called()

        # Test Git Status
        mock_run.return_value.stdout = "On branch main"
        self.ide._git_status()
        self.assertIn("On branch main", self.ide.console.get('1.0', 'end'))

    def test_config_formatting(self):
        """Test JSON formatting."""
        bad_json = '{"key": "value"}' # Compact
        self.ide.editor.delete('1.0', 'end')
        self.ide.editor.insert('1.0', bad_json)
        self.ide.current_file = "test.json"
        
        self.ide._format_document()
        
        content = self.ide.editor.get('1.0', 'end-1c')
        self.assertIn('\n', content) # Should be pretty-printed
        self.assertIn('    "key"', content) # Should have indentation

    def test_minimap_toggle(self):
        """Test Minimap toggle."""
        initial_state = self.ide.show_minimap_var.get()
        self.ide._toggle_minimap()
        self.assertNotEqual(self.ide.show_minimap_var.get(), initial_state)
        
        # Toggle back
        self.ide._toggle_minimap()
        self.assertEqual(self.ide.show_minimap_var.get(), initial_state)

    @patch('tkinter.filedialog.asksaveasfilename')
    def test_save_config_as(self, mock_ask_save):
        """Test Save Config As."""
        target_file = os.path.join(self.test_dir, 'new_config.json')
        mock_ask_save.return_value = target_file
        
        # Setup editor content
        config_content = '{"name": "NewLang"}'
        self.ide.editor.delete('1.0', 'end')
        self.ide.editor.insert('1.0', config_content)
        
        # Mock LanguageConfig validation/loading
        # We need self.ide.current_config set for save logic?
        # No, save_as loads from text or current config?
        # Implementation uses self.current_config.save. So we need current_config set.
        self.ide.current_config = MagicMock()
        
        self.ide._save_config_as()
             
        # self.ide.current_config.save should be called
        self.ide.current_config.save.assert_called_with(target_file)
        self.assertEqual(self.ide.current_config_path, target_file)

    def test_find_replace(self):
        """Test Search functionality."""
        self.ide.editor.delete('1.0', 'end')
        self.ide.editor.insert('1.0', "line1\nline2\nline3\nline2")
        
        # Test Find Text
        self.ide._find_text(query="line2", case_sensitive=False)
        
        # Check for tags
        ranges = self.ide.editor.tag_ranges('find_match')
        # Should match two times. Each match has start and end, so 4 indices.
        self.assertEqual(len(ranges), 4)

    def test_build_workflow(self):
        """Test Build and Clean simulation."""
        # Create a fake build artifact to clean
        dist_dir = os.path.join(self.test_dir, 'dist')
        os.makedirs(dist_dir)
        with open(os.path.join(dist_dir, 'artifact.bin'), 'w') as f:
            f.write("data")
            
        with patch('tkinter.messagebox.askyesno', return_value=True):
            self.ide._clean_project()
            
        # Dist should be gone or empty
        self.assertFalse(os.path.exists(dist_dir))

    def test_docs_generation(self):
        """Test Documentation Generation."""
        # Need a config
        self.ide.current_config = MagicMock()
        self.ide.current_config.name = "TestLang"
        self.ide.current_config.keyword_mappings = {"if": MagicMock(custom="si", description="desc")}
        self.ide.current_config.builtin_functions = {}
        
        self.ide._generate_docs()
            
        # Check if LANGUAGE_DOCS.md was created in current_project (test_dir)
        expected_file = os.path.join(self.test_dir, "LANGUAGE_DOCS.md")
        self.assertTrue(os.path.exists(expected_file))

    @patch('shutil.which')
    @patch('subprocess.Popen')
    def test_open_terminal(self, mock_popen, mock_which):
        """Test Terminal Launching logic."""
        # 1. Test with TERMINAL env var
        with patch.dict(os.environ, {"TERMINAL": "my-custom-term"}):
            mock_which.side_effect = lambda x: x == "my-custom-term"
            self.ide._open_terminal()
            mock_popen.assert_called_with(["my-custom-term"], cwd=self.test_dir)
            
        # 2. Test fallback list
        mock_popen.reset_mock()
        with patch.dict(os.environ, {}, clear=True): # No TERMINAL var
            # Make 'kitty' the only installed one
            mock_which.side_effect = lambda x: x == "kitty"
            self.ide._open_terminal()
            mock_popen.assert_called_with(["kitty"], cwd=self.test_dir)
            
    def test_teardown_safety(self):
        """Ensure teardown doesn't crash."""
        self.ide.destroy()

    @patch('tkinter.Toplevel')
    def test_tutorials(self, mock_toplevel):
        """Test that all tutorial categories launch a window."""
        # We need to mock the Toplevel because validation creates a window
        
        # Test basics (mapped from "first_language" menu concept)
        self.ide._tutorial("basics")
        mock_toplevel.assert_called()
        
        # Test new extensions tutorial
        mock_toplevel.reset_mock()
        self.ide._tutorial("extensions")
        mock_toplevel.assert_called()
        
        # Test invalid
        with patch('tkinter.messagebox.showwarning') as mock_warn:
            self.ide._tutorial("non_existent_topic")
            mock_warn.assert_called()

    def test_split_view(self):
        """Test Split Editor functionality."""
        # Ensure we start with no split
        self.assertFalse(hasattr(self.ide, "split_container") and self.ide.split_container)
        
        # Split
        self.ide._split_editor()
        self.assertTrue(hasattr(self.ide, "split_container"))
        self.assertIsNotNone(self.ide.split_container)
        self.assertTrue(hasattr(self.ide, "split_editor_text"))
        
        # Check content sync (initial copy)
        self.ide.editor.delete("1.0", "end")
        self.ide.editor.insert("1.0", "Test Content")
        self.ide._close_split()
        self.ide._split_editor()
        self.assertEqual(self.ide.split_editor_text.get("1.0", "end-1c"), "Test Content")
        
        # Close
        self.ide._close_split()
        self.assertIsNone(self.ide.split_container)

    def test_cursor_word_extraction(self):
        """Test getting the word under cursor."""
        # Insert "def myFunc"
        self.ide.editor.delete("1.0", "end")
        self.ide.editor.insert("1.0", "def myFunc")
        
        # Place cursor at start of "myFunc" (char 4)
        self.ide.editor.mark_set("insert", "1.4")
        
        word = self.ide._get_word_under_cursor()
        self.assertEqual(word, "myFunc")

    @patch('re.search')
    def test_goto_definition_searches(self, mock_search):
        """Test that Goto Definition attempts to find valid pattern."""
        self.ide.editor.delete("1.0", "end")
        self.ide.editor.insert("1.0", "call(x)")
        self.ide.editor.mark_set("insert", "1.5") # on 'x'
        
        with patch('tkinter.messagebox.showinfo'):
             # Try to go to definition of 'x'
             self.ide._goto_definition()
             
        # Mock search should be called at least once
        mock_search.assert_called()

if __name__ == '__main__':
    unittest.main()
