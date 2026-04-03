import unittest

from flask import json

from openapi_server.models.book import Book  # noqa: E501
from openapi_server.models.loan import Loan  # noqa: E501
from openapi_server.test import BaseTestCase


class TestDefaultController(BaseTestCase):
    """DefaultController integration test stubs"""

    def test_books_get(self):
        """Test case for books_get

        Get all books
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/books',
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_books_id_get(self):
        """Test case for books_id_get

        Get book by ID
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/books/{id}'.format(id=56),
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_books_post(self):
        """Test case for books_post

        Add a new book
        """
        book = {"author":"author","available":True,"id":0,"title":"title"}
        headers = { 
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/books',
            method='POST',
            headers=headers,
            data=json.dumps(book),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_loans_id_return_post(self):
        """Test case for loans_id_return_post

        Return a book
        """
        headers = { 
        }
        response = self.client.open(
            '/loans/{id}/return'.format(id=56),
            method='POST',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_loans_post(self):
        """Test case for loans_post

        Borrow a book
        """
        loan = {"dueDate":"2000-01-23","id":0,"memberId":6,"bookId":1,"status":"status"}
        headers = { 
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/loans',
            method='POST',
            headers=headers,
            data=json.dumps(loan),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
