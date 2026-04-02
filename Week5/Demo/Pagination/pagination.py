from flask import Flask, request, jsonify

app = Flask(__name__)

books = [
    {"id": 1, "title": "Clean Code", "author": "Robert C. Martin"},
    {"id": 2, "title": "The Pragmatic Programmer", "author": "Andrew Hunt"},
    {"id": 3, "title": "Design Patterns", "author": "Erich Gamma"},
    {"id": 4, "title": "Refactoring", "author": "Martin Fowler"},
    {"id": 5, "title": "Head First Java", "author": "Kathy Sierra"},
    {"id": 6, "title": "Code Complete", "author": "Steve McConnell"},
    {"id": 7, "title": "Effective C++", "author": "Scott Meyers"},
    {"id": 8, "title": "Python Crash Course", "author": "Eric Matthes"},
    {"id": 9, "title": "Grokking Algorithms", "author": "Aditya Bhargava"},
    {"id": 10, "title": "Domain-Driven Design", "author": "Eric Evans"}
]

# OFFSET-LIMIT PAGINATION
@app.route("/books/offset-limit", methods=["GET"])
def get_books_offset_limit():
    offset = int(request.args.get("offset", 0))
    limit = int(request.args.get("limit", 5))
    
    result = books[offset : offset + limit]
    
    return jsonify({
        "data": result,
        "metadata": {
            "type": "offset-limit",
            "offset": offset,
            "limit": limit,
            "totalItems": len(books),
            "hasNext": (offset + limit) < len(books)
        }
    })

# PAGE-BASED PAGINATION
@app.route("/books/page-based", methods=["GET"])
def get_books_page_based():
    page = int(request.args.get("page", 1))
    page_size = int(request.args.get("pageSize", 5))
    
    total_items = len(books)
    total_pages = (total_items + page_size - 1) // page_size
    start = (page - 1) * page_size
    end = start + page_size
    
    result = books[start:end]
    
    return jsonify({
        "data": result,
        "metadata": {
            "type": "page-based",
            "page": page,
            "pageSize": page_size,
            "totalPages": total_pages
        }
    })

# CURSOR-BASED PAGINATION
@app.route("/books/cursor", methods=["GET"])
def get_books_cursor():
    cursor = request.args.get("cursor", type=int)
    limit = int(request.args.get("limit", 5))
    
    if cursor is None:
        result = books[:limit]
    else:
        result = [book for book in books if book["id"] > cursor][:limit]
        
    next_cursor = result[-1]["id"] if result else None
    
    return jsonify({
        "data": result,
        "metadata": {
            "type": "cursor",
            "currentCursor": cursor,
            "nextCursor": next_cursor,
            "limit": limit
        }
    })

if __name__ == "__main__":
    app.run(port=5002, debug=True)