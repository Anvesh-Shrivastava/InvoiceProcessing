import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import json

# Add current directory to path so we can import extract_invoice
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import extract_invoice

class TestInvoiceProcessing(unittest.TestCase):

    @patch('psycopg2.connect')
    def test_get_db_connection_success(self, mock_connect):
        """Test successful database connection."""
        with patch.dict(os.environ, {"DATABASE_URL": "postgres://test_url"}):
            extract_invoice.DATABASE_URL = "postgres://test_url"
            conn = extract_invoice.get_db_connection()
            self.assertIsNotNone(conn)
            mock_connect.assert_called_with("postgres://test_url")

    @patch('extract_invoice.get_db_connection')
    def test_create_table(self, mock_get_conn):
        """Test table creation logic."""
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cur
        
        extract_invoice.create_table()
        
        mock_cur.execute.assert_called()
        self.assertIn("CREATE TABLE IF NOT EXISTS invoices", mock_cur.execute.call_args[0][0])
        mock_conn.commit.assert_called_once()

    @patch('extract_invoice.get_db_connection')
    def test_insert_invoice(self, mock_get_conn):
        """Test invoice insertion logic."""
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cur
        
        extract_invoice.insert_invoice("INV-999", "$99.99")
        
        mock_cur.execute.assert_called_with(
            "INSERT INTO invoices (invoice_number, amount) VALUES (%s, %s)",
            ("INV-999", "$99.99")
        )
        mock_conn.commit.assert_called_once()

    @patch('extract_invoice.client')
    @patch('os.path.exists')
    @patch('PIL.Image.open')
    def test_extract_invoice_data_success(self, mock_img_open, mock_exists, mock_client):
        """Test successful Gemini extraction."""
        mock_exists.return_value = True
        
        # Mock the response from client.models.generate_content
        mock_response = MagicMock()
        mock_response.text = json.dumps({"invoice_number": "TEST-123", "amount": "$500.00"})
        mock_client.models.generate_content.return_value = mock_response
        
        result = extract_invoice.extract_invoice_data("dummy.png")
        
        self.assertEqual(result["invoice_number"], "TEST-123")
        self.assertEqual(result["amount"], "$500.00")
        mock_client.models.generate_content.assert_called_once()

if __name__ == '__main__':
    unittest.main()
