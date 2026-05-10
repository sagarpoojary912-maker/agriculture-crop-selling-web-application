from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3, os
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = 'agri_secret_key_2024'
DB = 'agri.db'

# ─── DB Setup ───────────────────────────────────────────────────────────────
def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'buyer',
            phone TEXT,
            location TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            is_active INTEGER DEFAULT 1
        );
        CREATE TABLE IF NOT EXISTS crops (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            seller_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            quantity REAL NOT NULL,
            unit TEXT NOT NULL,
            description TEXT,
            image_url TEXT DEFAULT '/static/images/crop_default.svg',
            is_available INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (seller_id) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            buyer_id INTEGER NOT NULL,
            crop_id INTEGER NOT NULL,
            quantity REAL NOT NULL,
            total_price REAL NOT NULL,
            status TEXT DEFAULT 'pending',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (buyer_id) REFERENCES users(id),
            FOREIGN KEY (crop_id) REFERENCES crops(id)
        );
    ''')
    # Seed admin
    admin_pw = generate_password_hash('admin123')
    c.execute("INSERT OR IGNORE INTO users (name,email,password,role,phone,location) VALUES (?,?,?,?,?,?)",
              ('Admin','admin@agrimarket.com', admin_pw,'admin','9999999999','HQ'))
    conn.commit()
    conn.close()

# ─── Auth Decorators ─────────────────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def dec(*a, **kw):
        if 'user_id' not in session:
            flash('Please login first.','warning')
            return redirect(url_for('login'))
        return f(*a, **kw)
    return dec

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def dec(*a, **kw):
            if session.get('role') not in roles:
                flash('Access denied.','danger')
                return redirect(url_for('home'))
            return f(*a, **kw)
        return dec
    return decorator

# ─── Routes ──────────────────────────────────────────────────────────────────
@app.route('/')
def home():
    conn = get_db()
    crops = conn.execute('''SELECT c.*,u.name as seller_name,u.location as seller_loc
                            FROM crops c JOIN users u ON c.seller_id=u.id
                            WHERE c.is_available=1 ORDER BY c.created_at DESC LIMIT 8''').fetchall()
    categories = conn.execute('SELECT DISTINCT category FROM crops WHERE is_available=1').fetchall()
    conn.close()
    return render_template('home.html', crops=crops, categories=categories)

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method=='POST':
        name=request.form['name']; email=request.form['email']
        password=request.form['password']; role=request.form['role']
        phone=request.form.get('phone',''); location=request.form.get('location','')
        conn=get_db()
        existing=conn.execute('SELECT id FROM users WHERE email=?',(email,)).fetchone()
        if existing:
            flash('Email already registered.','danger')
            conn.close()
            return redirect(url_for('register'))
        hashed=generate_password_hash(password)
        conn.execute('INSERT INTO users (name,email,password,role,phone,location) VALUES (?,?,?,?,?,?)',
                     (name,email,hashed,role,phone,location))
        conn.commit(); conn.close()
        flash('Registration successful! Please login.','success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        email=request.form['email']; password=request.form['password']
        conn=get_db()
        user=conn.execute('SELECT * FROM users WHERE email=? AND is_active=1',(email,)).fetchone()
        conn.close()
        if user and check_password_hash(user['password'],password):
            session['user_id']=user['id']; session['name']=user['name']
            session['role']=user['role']; session['email']=user['email']
            flash(f"Welcome back, {user['name']}!",'success')
            if user['role']=='admin': return redirect(url_for('admin_dashboard'))
            if user['role']=='seller': return redirect(url_for('seller_dashboard'))
            return redirect(url_for('buyer_dashboard'))
        flash('Invalid credentials.','danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.','info')
    return redirect(url_for('home'))

# ─── Buyer ───────────────────────────────────────────────────────────────────
@app.route('/buyer')
@login_required
@role_required('buyer')
def buyer_dashboard():
    conn=get_db()
    crops=conn.execute('''SELECT c.*,u.name as seller_name,u.location as seller_loc,u.phone as seller_phone
                          FROM crops c JOIN users u ON c.seller_id=u.id WHERE c.is_available=1 ORDER BY c.created_at DESC''').fetchall()
    orders=conn.execute('''SELECT o.*,c.name as crop_name,c.unit FROM orders o JOIN crops c ON o.crop_id=c.id
                           WHERE o.buyer_id=? ORDER BY o.created_at DESC''',(session['user_id'],)).fetchall()
    categories=conn.execute('SELECT DISTINCT category FROM crops WHERE is_available=1').fetchall()
    conn.close()
    return render_template('buyer_dashboard.html', crops=crops, orders=orders, categories=categories)

@app.route('/buyer/order', methods=['POST'])
@login_required
@role_required('buyer')
def place_order():
    crop_id=request.form['crop_id']; qty=float(request.form['quantity'])
    conn=get_db()
    crop=conn.execute('SELECT * FROM crops WHERE id=? AND is_available=1',(crop_id,)).fetchone()
    if not crop:
        flash('Crop not available.','danger')
        conn.close()
        return redirect(url_for('buyer_dashboard'))
    total=crop['price']*qty
    conn.execute('INSERT INTO orders (buyer_id,crop_id,quantity,total_price) VALUES (?,?,?,?)',
                 (session['user_id'],crop_id,qty,total))
    conn.commit(); conn.close()
    flash(f'Order placed! Total: ₹{total:.2f}','success')
    return redirect(url_for('buyer_dashboard'))

# ─── Seller ───────────────────────────────────────────────────────────────────
@app.route('/seller')
@login_required
@role_required('seller')
def seller_dashboard():
    conn=get_db()
    crops=conn.execute('SELECT * FROM crops WHERE seller_id=? ORDER BY created_at DESC',(session['user_id'],)).fetchall()
    orders=conn.execute('''SELECT o.*,c.name as crop_name,c.unit,u.name as buyer_name,u.phone as buyer_phone
                           FROM orders o JOIN crops c ON o.crop_id=c.id JOIN users u ON o.buyer_id=u.id
                           WHERE c.seller_id=? ORDER BY o.created_at DESC''',(session['user_id'],)).fetchall()
    stats={
        'total_crops':len(crops),
        'total_orders':len(orders),
        'revenue':sum(o['total_price'] for o in orders if o['status']=='confirmed')
    }
    conn.close()
    return render_template('seller_dashboard.html', crops=crops, orders=orders, stats=stats)

@app.route('/seller/crop/add', methods=['POST'])
@login_required
@role_required('seller')
def add_crop():
    data=request.form
    conn=get_db()
    conn.execute('INSERT INTO crops (seller_id,name,category,price,quantity,unit,description) VALUES (?,?,?,?,?,?,?)',
                 (session['user_id'],data['name'],data['category'],float(data['price']),
                  float(data['quantity']),data['unit'],data.get('description','')))
    conn.commit(); conn.close()
    flash('Crop listed successfully!','success')
    return redirect(url_for('seller_dashboard'))

@app.route('/seller/crop/delete/<int:cid>')
@login_required
@role_required('seller')
def delete_crop(cid):
    conn=get_db()
    conn.execute('UPDATE crops SET is_available=0 WHERE id=? AND seller_id=?',(cid,session['user_id']))
    conn.commit(); conn.close()
    flash('Crop removed.','info')
    return redirect(url_for('seller_dashboard'))

@app.route('/seller/order/update/<int:oid>/<status>')
@login_required
@role_required('seller')
def update_order(oid,status):
    conn=get_db()
    conn.execute('UPDATE orders SET status=? WHERE id=?',(status,oid))
    conn.commit(); conn.close()
    flash(f'Order {status}.','success')
    return redirect(url_for('seller_dashboard'))

# ─── Admin ────────────────────────────────────────────────────────────────────
@app.route('/admin')
@login_required
@role_required('admin')
def admin_dashboard():
    conn=get_db()
    users=conn.execute('SELECT * FROM users WHERE role!="admin" ORDER BY created_at DESC').fetchall()
    crops=conn.execute('''SELECT c.*,u.name as seller_name FROM crops c JOIN users u ON c.seller_id=u.id
                          ORDER BY c.created_at DESC''').fetchall()
    orders=conn.execute('''SELECT o.*,c.name as crop_name,ub.name as buyer_name,us.name as seller_name
                           FROM orders o JOIN crops c ON o.crop_id=c.id JOIN users ub ON o.buyer_id=ub.id
                           JOIN users us ON c.seller_id=us.id ORDER BY o.created_at DESC''').fetchall()
    stats={
        'users':conn.execute('SELECT COUNT(*) FROM users WHERE role!="admin"').fetchone()[0],
        'sellers':conn.execute('SELECT COUNT(*) FROM users WHERE role="seller"').fetchone()[0],
        'buyers':conn.execute('SELECT COUNT(*) FROM users WHERE role="buyer"').fetchone()[0],
        'crops':conn.execute('SELECT COUNT(*) FROM crops WHERE is_available=1').fetchone()[0],
        'orders':conn.execute('SELECT COUNT(*) FROM orders').fetchone()[0],
        'revenue':conn.execute('SELECT SUM(total_price) FROM orders WHERE status="confirmed"').fetchone()[0] or 0
    }
    conn.close()
    return render_template('admin_dashboard.html', users=users, crops=crops, orders=orders, stats=stats)

@app.route('/admin/user/toggle/<int:uid>')
@login_required
@role_required('admin')
def toggle_user(uid):
    conn=get_db()
    user=conn.execute('SELECT is_active FROM users WHERE id=?',(uid,)).fetchone()
    new_status=0 if user['is_active'] else 1
    conn.execute('UPDATE users SET is_active=? WHERE id=?',(new_status,uid))
    conn.commit(); conn.close()
    flash('User status updated.','success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/crop/remove/<int:cid>')
@login_required
@role_required('admin')
def admin_remove_crop(cid):
    conn=get_db()
    conn.execute('UPDATE crops SET is_available=0 WHERE id=?',(cid,))
    conn.commit(); conn.close()
    flash('Crop removed.','success')
    return redirect(url_for('admin_dashboard'))

@app.route('/api/crops')
def api_crops():
    category=request.args.get('category','')
    search=request.args.get('search','')
    conn=get_db()
    q='SELECT c.*,u.name as seller_name,u.location FROM crops c JOIN users u ON c.seller_id=u.id WHERE c.is_available=1'
    params=[]
    if category: q+=' AND c.category=?'; params.append(category)
    if search: q+=' AND c.name LIKE ?'; params.append(f'%{search}%')
    crops=conn.execute(q,params).fetchall()
    conn.close()
    return jsonify([dict(c) for c in crops])

if __name__=='__main__':
    init_db()
    app.run(debug=True, port=5000)