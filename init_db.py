import sqlite3

def init_db():
    conn = sqlite3.connect('agency.db')
    c = conn.cursor()
    
    # Create messages table (keep existing)
    c.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Force Reset Clients & Employees as requested
    c.execute('DROP TABLE IF EXISTS clients')
    c.execute('DROP TABLE IF EXISTS employees')

    # Create clients table
    c.execute('''
        CREATE TABLE clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            company TEXT,
            email TEXT,
            phone TEXT,
            status TEXT
        )
    ''')

    # Create employees table
    c.execute('''
        CREATE TABLE employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            role TEXT,
            salary TEXT,
            status TEXT
        )
    ''')

    # Create visits table (Exact request: id, ip_address, timestamp)
    c.execute('''
        CREATE TABLE IF NOT EXISTS visits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip_address TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create projects table (Exact request: id, name, status, value)
    c.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            status TEXT,
            value TEXT
        )
    ''')
    
    # Seed Data for Projects
    c.execute("INSERT INTO projects (name, status, value) VALUES (?, ?, ?)", 
              ('Ravion Official Site', 'Completed', '$2,000'))
    
    # Seed Data for Clients
    c.execute("INSERT INTO clients (name, company, email, phone, status) VALUES (?, ?, ?, ?, ?)",
              ('Ahmet Yilmaz', 'Hotel A', 'ahmet@hotela.com', '555-0101', 'Active'))
              
    # Seed Data for Employees
    c.execute("INSERT INTO employees (name, role, salary, status) VALUES (?, ?, ?, ?)",
              ('Ali Veli', 'Junior Dev', '$1,200', 'Active'))

    print("Seeded database with dummy data.")
    
    conn.commit()
    conn.close()
    print("Database 'agency.db' initialized/updated.")

if __name__ == '__main__':
    init_db()
