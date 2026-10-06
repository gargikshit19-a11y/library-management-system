const API_BASE = 'http://localhost:8000/api';

let currentBookEditId = null;
let currentMemberEditId = null;
let currentLoanView = 'all';

function showMessage(text, type = 'success') {
    const msg = document.getElementById('message');
    msg.textContent = text;
    msg.className = 'message ' + type;
    msg.style.display = 'block';
    setTimeout(() => {
        msg.style.display = 'none';
    }, 3000);
}

async function fetchAPI(endpoint, options = {}) {
    try {
        const response = await fetch(API_BASE + endpoint, options);
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.error || 'API Error');
        }
        return data;
    } catch (error) {
        throw error;
    }
}

// Navigation
document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', () => {
        document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
        document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
        item.classList.add('active');
        document.getElementById(item.dataset.page).classList.add('active');
        if (item.dataset.page === 'dashboard') loadDashboard();
        if (item.dataset.page === 'books') loadBooks();
        if (item.dataset.page === 'members') loadMembers();
        if (item.dataset.page === 'loans') loadLoans('all');
    });
});

// Dashboard
async function loadDashboard() {
    try {
        const data = await fetchAPI('/dashboard');
        document.getElementById('total-books').textContent = data.total_books;
        document.getElementById('available-copies').textContent = data.available_copies;
        document.getElementById('total-members').textContent = data.total_members;
        document.getElementById('issued-books').textContent = data.issued_books;
        document.getElementById('overdue-books').textContent = data.overdue_books;
    } catch (error) {
        showMessage(error.message, 'error');
    }
}

// Books
document.getElementById('add-book-btn').addEventListener('click', () => {
    document.getElementById('modal-title').textContent = 'Add Book';
    document.getElementById('book-form').reset();
    document.getElementById('book-id').value = '';
    currentBookEditId = null;
    document.getElementById('modal').style.display = 'block';
});

document.getElementById('cancel-btn').addEventListener('click', () => {
    document.getElementById('modal').style.display = 'none';
});

document.getElementById('book-search').addEventListener('input', (e) => {
    loadBooks(e.target.value);
});

async function loadBooks(search = '') {
    try {
        const url = search ? `/books?search=${encodeURIComponent(search)}` : '/books';
        const books = await fetchAPI(url);
        const tbody = document.querySelector('#books-table tbody');
        tbody.innerHTML = '';
        books.forEach(book => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${book.book_id}</td>
                <td>${escapeHtml(book.title)}</td>
                <td>${escapeHtml(book.author)}</td>
                <td>${escapeHtml(book.isbn)}</td>
                <td>${escapeHtml(book.category)}</td>
                <td>${book.total_copies}</td>
                <td>${book.available_copies}</td>
                <td>
                    <button class="btn btn-small btn-primary" onclick="editBook(${book.book_id}, '${escapeHtml(book.title).replace(/'/g, "\\'")}', '${escapeHtml(book.author).replace(/'/g, "\\'")}', '${escapeHtml(book.isbn).replace(/'/g, "\\'")}', '${escapeHtml(book.category).replace(/'/g, "\\'")}', ${book.total_copies})">Edit</button>
                    <button class="btn btn-small btn-danger" onclick="deleteBook(${book.book_id})">Delete</button>
                </td>
            `;
            tbody.appendChild(tr);
        });
    } catch (error) {
        showMessage(error.message, 'error');
    }
}

window.editBook = (id, title, author, isbn, category, total) => {
    document.getElementById('modal-title').textContent = 'Edit Book';
    document.getElementById('book-id').value = id;
    document.getElementById('book-title').value = title;
    document.getElementById('book-author').value = author;
    document.getElementById('book-isbn').value = isbn;
    document.getElementById('book-category').value = category;
    document.getElementById('book-total').value = total;
    currentBookEditId = id;
    document.getElementById('modal').style.display = 'block';
};

window.deleteBook = async (id) => {
    if (!confirm('Are you sure you want to delete this book?')) return;
    try {
        await fetchAPI(`/books/${id}`, { method: 'DELETE' });
        showMessage('Book deleted successfully');
        loadBooks(document.getElementById('book-search').value);
    } catch (error) {
        showMessage(error.message, 'error');
    }
};

document.getElementById('book-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const id = document.getElementById('book-id').value;
    const data = {
        title: document.getElementById('book-title').value,
        author: document.getElementById('book-author').value,
        isbn: document.getElementById('book-isbn').value,
        category: document.getElementById('book-category').value,
        total_copies: parseInt(document.getElementById('book-total').value)
    };
    try {
        if (id) {
            await fetchAPI(`/books/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            showMessage('Book updated successfully');
        } else {
            await fetchAPI('/books', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            showMessage('Book added successfully');
        }
        document.getElementById('modal').style.display = 'none';
        loadBooks(document.getElementById('book-search').value);
    } catch (error) {
        showMessage(error.message, 'error');
    }
});

// Members
document.getElementById('add-member-btn').addEventListener('click', () => {
    document.getElementById('member-modal-title').textContent = 'Add Member';
    document.getElementById('member-form').reset();
    document.getElementById('member-id').value = '';
    currentMemberEditId = null;
    document.getElementById('member-modal').style.display = 'block';
});

document.getElementById('cancel-member-btn').addEventListener('click', () => {
    document.getElementById('member-modal').style.display = 'none';
});

document.getElementById('member-search').addEventListener('input', (e) => {
    loadMembers(e.target.value);
});

async function loadMembers(search = '') {
    try {
        const url = search ? `/members?search=${encodeURIComponent(search)}` : '/members';
        const members = await fetchAPI(url);
        const tbody = document.querySelector('#members-table tbody');
        tbody.innerHTML = '';
        members.forEach(member => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${member.member_id}</td>
                <td>${escapeHtml(member.name)}</td>
                <td>${escapeHtml(member.email)}</td>
                <td>${escapeHtml(member.phone)}</td>
                <td>${member.join_date}</td>
                <td>
                    <button class="btn btn-small btn-primary" onclick="editMember(${member.member_id}, '${escapeHtml(member.name).replace(/'/g, "\\'")}', '${escapeHtml(member.email).replace(/'/g, "\\'")}', '${escapeHtml(member.phone).replace(/'/g, "\\'")}', '${member.join_date}')">Edit</button>
                    <button class="btn btn-small btn-danger" onclick="deleteMember(${member.member_id})">Delete</button>
                </td>
            `;
            tbody.appendChild(tr);
        });
    } catch (error) {
        showMessage(error.message, 'error');
    }
}

window.editMember = (id, name, email, phone, join) => {
    document.getElementById('member-modal-title').textContent = 'Edit Member';
    document.getElementById('member-id').value = id;
    document.getElementById('member-name').value = name;
    document.getElementById('member-email').value = email;
    document.getElementById('member-phone').value = phone;
    document.getElementById('member-join').value = join;
    currentMemberEditId = id;
    document.getElementById('member-modal').style.display = 'block';
};

window.deleteMember = async (id) => {
    if (!confirm('Are you sure you want to delete this member?')) return;
    try {
        await fetchAPI(`/members/${id}`, { method: 'DELETE' });
        showMessage('Member deleted successfully');
        loadMembers(document.getElementById('member-search').value);
    } catch (error) {
        showMessage(error.message, 'error');
    }
};

document.getElementById('member-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const id = document.getElementById('member-id').value;
    const data = {
        name: document.getElementById('member-name').value,
        email: document.getElementById('member-email').value,
        phone: document.getElementById('member-phone').value,
        join_date: document.getElementById('member-join').value
    };
    try {
        if (id) {
            await fetchAPI(`/members/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            showMessage('Member updated successfully');
        } else {
            await fetchAPI('/members', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            showMessage('Member added successfully');
        }
        document.getElementById('member-modal').style.display = 'none';
        loadMembers(document.getElementById('member-search').value);
    } catch (error) {
        showMessage(error.message, 'error');
    }
});

// Issue Book
document.getElementById('issue-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const data = {
        book_id: parseInt(document.getElementById('issue-book-id').value),
        member_id: parseInt(document.getElementById('issue-member-id').value),
        issue_date: document.getElementById('issue-date').value,
        due_date: document.getElementById('due-date').value
    };
    try {
        await fetchAPI('/loans/issue', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        showMessage('Book issued successfully');
        e.target.reset();
    } catch (error) {
        showMessage(error.message, 'error');
    }
});

// Return Book
document.getElementById('return-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const data = {
        loan_id: parseInt(document.getElementById('loan-id').value)
    };
    try {
        await fetchAPI('/loans/return', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        showMessage('Book returned successfully');
        e.target.reset();
    } catch (error) {
        showMessage(error.message, 'error');
    }
});

// Loans
document.getElementById('all-loans-btn').addEventListener('click', () => {
    currentLoanView = 'all';
    loadLoans('all');
});
document.getElementById('overdue-loans-btn').addEventListener('click', () => {
    currentLoanView = 'overdue';
    loadLoans('overdue');
});

async function loadLoans(view = 'all') {
    try {
        const endpoint = view === 'overdue' ? '/loans/overdue' : '/loans';
        const loans = await fetchAPI(endpoint);
        const tbody = document.querySelector('#loans-table tbody');
        tbody.innerHTML = '';
        loans.forEach(loan => {
            const isReturned = loan.return_date !== null;
            const isOverdue = !isReturned && loan.due_date < getToday();
            let status = '';
            if (isReturned) status = '<span class="badge badge-returned">Returned</span>';
            else if (isOverdue) status = '<span class="badge badge-overdue">Overdue</span>';
            else status = '<span class="badge badge-active">Active</span>';
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${loan.loan_id}</td>
                <td>${escapeHtml(loan.title)}</td>
                <td>${escapeHtml(loan.isbn)}</td>
                <td>${escapeHtml(loan.name)}</td>
                <td>${escapeHtml(loan.email)}</td>
                <td>${loan.issue_date}</td>
                <td>${loan.due_date}</td>
                <td>${loan.return_date || '-'}</td>
                <td>${status}</td>
            `;
            tbody.appendChild(tr);
        });
    } catch (error) {
        showMessage(error.message, 'error');
    }
}

function getToday() {
    const d = new Date();
    return d.toISOString().split('T')[0];
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadDashboard();
    const today = getToday();
    document.getElementById('issue-date').value = today;
    // Set default due date to 15 days from today
    const due = new Date();
    due.setDate(due.getDate() + 15);
    document.getElementById('due-date').value = due.toISOString().split('T')[0];
    document.getElementById('member-join').value = today;
});
