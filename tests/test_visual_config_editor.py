import unittest
import tkinter as tk
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
from parsercraft.visual_config_editor import VisualConfigEditor, KeywordMapping
from parsercraft.language_config import LanguageConfig

class TestVisualConfigEditor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            cls.root = tk.Tk()
            cls.root.withdraw()
        except Exception:
            # Fallback for headless environments if tk fails
            cls.root = None
    
    @classmethod
    def tearDownClass(cls):
        if cls.root:
            cls.root.destroy()

    def setUp(self):
        if not self.root:
            self.skipTest("No display available for Tkinter")
        
        self.config = LanguageConfig()
        # Pre-populate some data
        self.config.keyword_mappings = {
            "if": KeywordMapping("if", "si", "flow"),
            "function": KeywordMapping("function", "funcion", "decl")
        }
        
        self.editor = VisualConfigEditor(self.root, config=self.config)

    def tearDown(self):
        if hasattr(self, 'editor'):
            self.editor.destroy()

    def test_refresh_keywords(self):
        # Check if listbox is populated
        # Listbox items: "if → si (flow)", "function → funcion (decl)"
        items = self.editor.kw_list.get(0, tk.END)
        self.assertEqual(len(items), 2)
        self.assertIn("if → si (flow)", items)

    def test_remove_keyword(self):
        # Select first item
        self.editor.kw_list.selection_set(0)
        
        # Trigger remove
        # We need to mock messagebox inside _remove_keyword if selection is invalid, 
        # but here selection is valid.
        
        # Note: dict ordering might vary in older python but usually preserved in 3.7+
        # "if" was inserted first.
        
        self.editor._remove_keyword()
        
        self.assertEqual(len(self.config.keyword_mappings), 1)
        self.assertNotIn("if", self.config.keyword_mappings)
        
        # Verify listbox updated
        items = self.editor.kw_list.get(0, tk.END)
        self.assertEqual(len(items), 1)

    @patch('tkinter.simpledialog.askstring')
    def test_add_keyword_dialog(self, mock_ask):
        # _add_keyword calls _keyword_dialog which creates a Toplevel.
        # This is hard to test without blocking or mocking the Toplevel interactions.
        # But _keyword_dialog sets up bound variables and save button.
        
        # We can test logic by invoking _keyword_dialog with a mock context if refactored,
        # but as is, it creates UI.
        # Let's verify _keyword_dialog opens a window.
        
        with patch('tkinter.Toplevel') as mock_toplevel:
            mock_win = MagicMock()
            mock_toplevel.return_value = mock_win
            
            self.editor._add_keyword()
            mock_toplevel.assert_called()

    def test_save_action(self):
        # Mock filedialog.asksaveasfilename
        with patch('tkinter.filedialog.asksaveasfilename', return_value="test_out.yaml"):
            # Mock config.save
            with patch.object(self.config, 'save') as mock_save:
                with patch('tkinter.messagebox.showinfo'):
                    self.editor._save()
                    mock_save.assert_called_with("test_out.yaml")

if __name__ == '__main__':
    unittest.main()
