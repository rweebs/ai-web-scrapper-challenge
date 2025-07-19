import unittest
import json
import os
from unittest.mock import patch, MagicMock, mock_open
from bs4 import BeautifulSoup
import tempfile
import shutil

# Import the functions to test
from scrape import (
    scrape_website,
    extract_body_content,
    clean_body_content,
    split_dom_content
)
from parse import parse_with_ollama


class TestWebScraper(unittest.TestCase):
    """Test cases for the AI Web Scraper application"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_data_dir = "test"
f test_scrape_website_mock(self, mock_chrome):

    def test_parse_json_structure(self):
        """Test that parsed results have correct JSON structure"""
        # Load test result files
        test_files = [
            "alabama-result.txt",
            "colorado-result.txt",
            "american_boer-result.txt",
            "hollie-result.txt",
            "colorado-julie-result.txt",
            "full-result.txt"
        ]

        for test_file in test_files:
            file_path = os.path.join(self.test_data_dir, test_file)
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Extract JSON from the content
                try:
                    # Find JSON content between curly braces
                    start = content.find('{')
                    end = content.rfind('}') + 1
                    if start != -1 and end != 0:
                        json_content = content[start:end]
                        parsed_json = json.loads(json_content)

                        # Verify JSON structure
                        self.assertIn('headers', parsed_json)
                        self.assertIn('data', parsed_json)
                        self.assertIsInstance(parsed_json['headers'], list)
                        self.assertIsInstance(parsed_json['data'], list)

                        # Verify headers structure
                        expected_headers = ["Action", "State", "Name", "Farm", "Phone", "Website"]
                        self.assertEqual(parsed_json['headers'], expected_headers)

                        # Verify data structure (if not empty)
                        if parsed_json['data']:
                            for row in parsed_json['data']:
                                self.assertIsInstance(row, list)
                                # Allow for flexible row length as some data might be missing
                                self.assertLessEqual(len(row), len(expected_headers))

                except json.JSONDecodeError as e:
                    self.fail(f"Invalid JSON in {test_file}: {e}")

    def test_input_output_consistency(self):
        """Test consistency between input and output files"""
        # Test file pairs
        test_pairs = [
            ("alabama.txt", "alabama-result.txt"),
            ("colorado.txt", "colorado-result.txt"),
            ("american_boer.txt", "american_boer-result.txt"),
            ("hollie.txt", "hollie-result.txt"),
            ("colorado-julir.txt", "colorado-julie-result.txt"),
            ("full.txt", "full-result.txt")
        ]

        for input_file, output_file in test_pairs:
            input_path = os.path.join(self.test_data_dir, input_file)
            output_path = os.path.join(self.test_data_dir, output_file)

            if os.path.exists(input_path) and os.path.exists(output_path):
                # Check that input file contains expected content
                with open(input_path, 'r', encoding='utf-8') as f:
                    input_content = f.read()

                # Should contain navigation elements
                self.assertIn("Directory", input_content)
                self.assertIn("Breeder Directory", input_content)

                # Check that output file contains JSON
                with open(output_path, 'r', encoding='utf-8') as f:
                    output_content = f.read()

                self.assertIn('"headers"', output_content)
                self.assertIn('"data"', output_content)

    @patch('parse.ChatPromptTemplate')
    @patch('parse.model')
    def test_parse_with_ollama_mock(self, mock_model, mock_prompt):
        """Test parsing with mocked Ollama"""
        # Mock the prompt template and chain
        mock_prompt_instance = MagicMock()
        mock_prompt.from_template.return_value = mock_prompt_instance

        # Mock the chain
        mock_chain = MagicMock()
        mock_prompt_instance.__or__ = MagicMock(return_value=mock_chain)

        # Mock the response
        mock_response = MagicMock()
        mock_response.content = '{"headers": ["Action", "State"], "data": [["View", "AL"]]}'
        mock_chain.invoke.return_value = mock_response.content

        # Test parsing
        dom_chunks = ["Test content chunk 1", "Test content chunk 2"]
        parse_description = "Extract test data"

        result = parse_with_ollama(dom_chunks, parse_description)

        # Verify chain was called for each chunk
        self.assertEqual(mock_chain.invoke.call_count, 2)
        self.assertIn('"headers"', result)

    def test_file_encoding_consistency(self):
        """Test that all test files use consistent encoding"""
        test_files = []
        for filename in os.listdir(self.test_data_dir):
            if filename.endswith('.txt'):
                test_files.append(os.path.join(self.test_data_dir, filename))

        for file_path in test_files:
            # Should be readable with UTF-8 encoding
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.assertIsInstance(content, str)
            except UnicodeDecodeError as e:
                self.fail(f"Encoding issue in {file_path}: {e}")

    def test_data_validation(self):
        """Test validation of extracted data"""
        # Load and validate all result files
        result_files = [f for f in os.listdir(self.test_data_dir) if f.endswith('-result.txt')]

        for result_file in result_files:
            file_path = os.path.join(self.test_data_dir, result_file)
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract JSON
            start = content.find('{')
            end = content.rfind('}') + 1
            if start != -1 and end != 0:
                json_content = content[start:end]
                try:
                    data = json.loads(json_content)

                    # Validate data structure
                    if data['data']:
                        for row in data['data']:
                            # Check that Action is always "View"
                            if len(row) > 0 and row[0] != "Showing 1 to 1 of 1 entries":
                                self.assertEqual(row[0], "View")

                            # Check that State is a valid state code (2 letters or full name)
                            if len(row) > 1:
                                state = row[1]
                                self.assertIsInstance(state, str)
                                # Allow for both 2-letter codes and full state names
                                self.assertLessEqual(len(state), 20)

                            # Check that Name is not empty
                            if len(row) > 2:
                                name = row[2]
                                self.assertIsInstance(name, str)
                                self.assertGreater(len(name.strip()), 0)

                except json.JSONDecodeError:
                    # Skip files that don't contain valid JSON
                    pass


if __name__ == '__main__':
    # Create test suite
    test_suite = unittest.TestSuite()

    # Add test cases using TestLoader
    loader = unittest.TestLoader()
    test_suite.addTests(loader.loadTestsFromTestCase(TestWebScraper))
    # test_suite.addTests(loader.loadTestsFromTestCase(TestIntegration))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    # Print summary
    print(f"\n{'='*50}")
    print(f"Test Summary:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"{'='*50}")

    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")

    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
