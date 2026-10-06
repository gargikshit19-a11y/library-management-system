import http.server
import socketserver
import json
import os
import urllib.parse
from database import get_connection
from books import get_all_books, add_book, update_book, delete_book
from members import get_all_members, add_member, update_member, delete_member
from loans import issue_book, return_book, get_all_loans, get_overdue_loans

PORT = 8000
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'frontend')

class Handler(http.server.BaseHTTPRequestHandler):
    def _set_headers(self, status=200, content_type='application/json'):
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers(200)

    def serve_static(self):
        path = self.path
        if path == '/':
            path = '/index.html'
        file_path = os.path.join(FRONTEND_DIR, path.lstrip('/'))
        if os.path.exists(file_path) and os.path.isfile(file_path):
            ext = os.path.splitext(file_path)[1]
            if ext == '.html':
                content_type = 'text/html'
            elif ext == '.css':
                content_type = 'text/css'
            elif ext == '.js':
                content_type = 'application/javascript'
            elif ext == '.png':
                content_type = 'image/png'
            else:
                content_type = 'text/plain'
            try:
                with open(file_path, 'rb') as f:
                    self.send_response(200)
                    self.send_header('Content-Type', content_type)
                    self.end_headers()
                    self.wfile.write(f.read())
                return True
            except:
                return False
        return False

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path.startswith('/api/'):
            if parsed.path == '/api/dashboard':
                self.handle_dashboard()
                return
            if parsed.path == '/api/books':
                search = urllib.parse.parse_qs(parsed.query).get('search', [None])[0]
                self.handle_get_books(search)
                return
            if parsed.path == '/api/members':
                search = urllib.parse.parse_qs(parsed.query).get('search', [None])[0]
                self.handle_get_members(search)
                return
            if parsed.path == '/api/loans':
                self.handle_get_loans()
                return
            if parsed.path == '/api/loans/overdue':
                self.handle_get_overdue_loans()
                return
        if self.serve_static():
            return
        self._set_headers(404)
        self.wfile.write(json.dumps({'error': 'Not found'}).encode())

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path.startswith('/api/'):
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length) if content_length > 0 else b'{}'
            try:
                data = json.loads(body.decode('utf-8')) if body else {}
            except:
                data = {}
            if parsed.path == '/api/books':
                self.handle_add_book(data)
                return
            if parsed.path == '/api/members':
                self.handle_add_member(data)
                return
            if parsed.path == '/api/loans/issue':
                self.handle_issue_book(data)
                return
            if parsed.path == '/api/loans/return':
                self.handle_return_book(data)
                return
        self._set_headers(404)
        self.wfile.write(json.dumps({'error': 'Not found'}).encode())

    def do_PUT(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path.startswith('/api/books/'):
            book_id = parsed.path.split('/')[-1]
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length) if content_length > 0 else b'{}'
            try:
                data = json.loads(body.decode('utf-8'))
            except:
                data = {}
            self.handle_update_book(book_id, data)
            return
        if parsed.path.startswith('/api/members/'):
            member_id = parsed.path.split('/')[-1]
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length) if content_length > 0 else b'{}'
            try:
                data = json.loads(body.decode('utf-8'))
            except:
                data = {}
            self.handle_update_member(member_id, data)
            return
        self._set_headers(404)
        self.wfile.write(json.dumps({'error': 'Not found'}).encode())

    def do_DELETE(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path.startswith('/api/books/'):
            book_id = parsed.path.split('/')[-1]
            self.handle_delete_book(book_id)
            return
        if parsed.path.startswith('/api/members/'):
            member_id = parsed.path.split('/')[-1]
            self.handle_delete_member(member_id)
            return
        self._set_headers(404)
        self.wfile.write(json.dumps({'error': 'Not found'}).encode())

    def handle_dashboard(self):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM books")
            total_books = cursor.fetchone()[0]
            cursor.execute("SELECT SUM(available_copies) FROM books")
            available_copies = cursor.fetchone()[0] or 0
            cursor.execute("SELECT COUNT(*) FROM members")
            total_members = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM loans WHERE return_date IS NULL")
            issued_books = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM loans WHERE return_date IS NULL AND due_date < CURDATE()")
            overdue_books = cursor.fetchone()[0]
            cursor.close()
            conn.close()
            self._set_headers(200)
            self.wfile.write(json.dumps({
                'total_books': total_books,
                'available_copies': int(available_copies),
                'total_members': total_members,
                'issued_books': issued_books,
                'overdue_books': overdue_books
            }).encode())
        except Exception as e:
            self._set_headers(500)
            self.wfile.write(json.dumps({'error': str(e)}).encode())

    def handle_get_books(self, search):
        books, err = get_all_books(search)
        if err:
            self._set_headers(500)
            self.wfile.write(json.dumps({'error': err}).encode())
            return
        self._set_headers(200)
        self.wfile.write(json.dumps(books).encode())

    def handle_add_book(self, data):
        required = ['title', 'author', 'isbn', 'category', 'total_copies']
        for r in required:
            if not data.get(r):
                self._set_headers(400)
                self.wfile.write(json.dumps({'error': f'{r} is required'}).encode())
                return
        book_id, err = add_book(data['title'], data['author'], data['isbn'], data['category'], data['total_copies'])
        if err:
            self._set_headers(500)
            self.wfile.write(json.dumps({'error': err}).encode())
            return
        self._set_headers(201)
        self.wfile.write(json.dumps({'message': 'Book added successfully', 'book_id': book_id}).encode())

    def handle_update_book(self, book_id, data):
        required = ['title', 'author', 'isbn', 'category', 'total_copies']
        for r in required:
            if not data.get(r):
                self._set_headers(400)
                self.wfile.write(json.dumps({'error': f'{r} is required'}).encode())
                return
        success, err = update_book(book_id, data['title'], data['author'], data['isbn'], data['category'], data['total_copies'])
        if not success:
            status = 404 if err == 'Book not found' else 400
            self._set_headers(status)
            self.wfile.write(json.dumps({'error': err}).encode())
            return
        self._set_headers(200)
        self.wfile.write(json.dumps({'message': 'Book updated successfully'}).encode())

    def handle_delete_book(self, book_id):
        success, err = delete_book(book_id)
        if not success:
            self._set_headers(400)
            self.wfile.write(json.dumps({'error': err or 'Delete failed'}).encode())
            return
        self._set_headers(200)
        self.wfile.write(json.dumps({'message': 'Book deleted successfully'}).encode())

    def handle_get_members(self, search):
        members, err = get_all_members(search)
        if err:
            self._set_headers(500)
            self.wfile.write(json.dumps({'error': err}).encode())
            return
        self._set_headers(200)
        self.wfile.write(json.dumps(members).encode())

    def handle_add_member(self, data):
        required = ['name', 'email', 'phone', 'join_date']
        for r in required:
            if not data.get(r):
                self._set_headers(400)
                self.wfile.write(json.dumps({'error': f'{r} is required'}).encode())
                return
        member_id, err = add_member(data['name'], data['email'], data['phone'], data['join_date'])
        if err:
            self._set_headers(500)
            self.wfile.write(json.dumps({'error': err}).encode())
            return
        self._set_headers(201)
        self.wfile.write(json.dumps({'message': 'Member added successfully', 'member_id': member_id}).encode())

    def handle_update_member(self, member_id, data):
        success, err = update_member(member_id, data['name'], data['email'], data['phone'], data['join_date'])
        if err:
            self._set_headers(500)
            self.wfile.write(json.dumps({'error': err}).encode())
            return
        self._set_headers(200)
        self.wfile.write(json.dumps({'message': 'Member updated successfully'}).encode())

    def handle_delete_member(self, member_id):
        success, err = delete_member(member_id)
        if not success:
            self._set_headers(400)
            self.wfile.write(json.dumps({'error': err or 'Delete failed'}).encode())
            return
        self._set_headers(200)
        self.wfile.write(json.dumps({'message': 'Member deleted successfully'}).encode())

    def handle_get_loans(self):
        loans, err = get_all_loans()
        if err:
            self._set_headers(500)
            self.wfile.write(json.dumps({'error': err}).encode())
            return
        self._set_headers(200)
        self.wfile.write(json.dumps(loans).encode())

    def handle_get_overdue_loans(self):
        loans, err = get_overdue_loans()
        if err:
            self._set_headers(500)
            self.wfile.write(json.dumps({'error': err}).encode())
            return
        self._set_headers(200)
        self.wfile.write(json.dumps(loans).encode())

    def handle_issue_book(self, data):
        required = ['book_id', 'member_id', 'issue_date', 'due_date']
        for r in required:
            if not data.get(r):
                self._set_headers(400)
                self.wfile.write(json.dumps({'error': f'{r} is required'}).encode())
                return
        success, err = issue_book(data['book_id'], data['member_id'], data['issue_date'], data['due_date'])
        if not success:
            self._set_headers(400)
            self.wfile.write(json.dumps({'error': err}).encode())
            return
        self._set_headers(200)
        self.wfile.write(json.dumps({'message': 'Book issued successfully'}).encode())

    def handle_return_book(self, data):
        required = ['loan_id']
        for r in required:
            if not data.get(r):
                self._set_headers(400)
                self.wfile.write(json.dumps({'error': f'{r} is required'}).encode())
                return
        success, err = return_book(data['loan_id'])
        if not success:
            self._set_headers(400)
            self.wfile.write(json.dumps({'error': err}).encode())
            return
        self._set_headers(200)
        self.wfile.write(json.dumps({'message': 'Book returned successfully'}).encode())

if __name__ == '__main__':
    with socketserver.TCPServer(('', PORT), Handler) as httpd:
        print(f'Server running at http://localhost:{PORT}')
        httpd.serve_forever()
