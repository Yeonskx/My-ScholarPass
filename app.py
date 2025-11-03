from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import sqlite3
import os

app = Flask(__name__, template_folder='.')

# --- Database connection ---
def get_db_connection():
    os.makedirs('database', exist_ok=True)
    conn = sqlite3.connect('database/app.db')
    conn.row_factory = sqlite3.Row
    return conn

# --- Initialize DB ---
def init_db():
    conn = get_db_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT DEFAULT 'student'
    )''')
    conn.commit()
    conn.close()

# --- ROUTES ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signin')
def signin():
    return render_template('accountsignin.html')

@app.route('/students')
def students():
    return render_template('students.html')

@app.route('/providers')
def providers():
    return render_template('providers.html')

@app.route('/questions')
def questions():
    return render_template('questions.html')

@app.route('/myscholarpass')
def myscholarpass():
    return render_template('scholarpass.html')

# --- SIGNUP ---
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        try:
            conn.execute(
                "INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, 'student')",
                (name, email, password)
            )
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            return "⚠️ Email already registered. Try logging in."
        conn.close()

        return redirect(url_for('questions'))
    
    return render_template('accountsignin.html')

# --- LOGIN ---
@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']

    conn = get_db_connection()
    user = conn.execute(
        "SELECT * FROM users WHERE email=? AND password=?",
        (email, password)
    ).fetchone()
    conn.close()

    if user:
        return redirect(url_for('questions'))
    else:
        return "❌ Invalid email or password. Please try again."

# --- RECOMMENDATION ---
@app.route('/recommend', methods=['POST'])
def recommend():
    # --- Collect answers from form ---
    answers = {
        'school_type': request.form.get('school_type', '').lower().strip(),
        'average': request.form.get('average', '').lower().strip(),
        'financial_need': request.form.get('financial_need', '').lower().strip(),
        'talent': request.form.get('talent', '').lower().strip(),
        'university': request.form.get('university', '').lower().strip()
    }

    # --- Expanded Scholarship Dataset with detailed info ---
    scholarships = [
        {
            "name": "Ateneo Freshmen Merit Scholarship",
            "university": "Ateneo de Manila University",
            "description": "Top 50 applicants based on academic ranking and ACET scores get free tuition and ₱50,000 annual allowance.",
            "tags": ["Merit-based", "Full Tuition", "Allowance"],
            "criteria": {"university": ["ateneo"], "average": ["95", "top", "excellent"]},
            "weight": {"university": 3, "average": 2}
        },
        {
            "name": "Director's List Scholarship",
            "university": "Ateneo de Manila University",
            "description": "150 applicants with outstanding high school averages and extracurricular activities receive a ₱100,000 grant.",
            "tags": ["Academic Excellence", "₱100,000 Grant"],
            "criteria": {"university": ["ateneo"], "average": ["90", "high"], "talent": ["extra", "arts", "sports"]},
            "weight": {"university": 3, "average": 2, "talent": 1}
        },
        {
            "name": "DLSU Archer Achiever Scholarship",
            "university": "De La Salle University",
            "description": "Top students from science or public high schools get a full waiver of tuition and other fees.",
            "tags": ["Full Tuition Waiver", "Entrance Exam"],
            "criteria": {"university": ["dlsu"], "average": ["90", "high"], "school_type": ["science", "public"]},
            "weight": {"university": 3, "average": 2}
        },
        {
            "name": "Star Scholars Program",
            "university": "De La Salle University",
            "description": "Integrated scholarship covering college and postgraduate programs such as master's, law, or medicine.",
            "tags": ["Integrated", "Graduate", "Full Scholarship"],
            "criteria": {"university": ["dlsu"], "average": ["95"], "financial_need": ["no"]},
            "weight": {"university": 3, "average": 2}
        },
        {
            "name": "UST Santo Tomas College Scholarship",
            "university": "University of Santo Tomas",
            "description": "For students with excellent academic performance.",
            "tags": ["Academic Excellence", "Merit-based"],
            "criteria": {"university": ["ust"], "average": ["high", "90", "95"]},
            "weight": {"university": 3, "average": 2}
        },
        {
            "name": "San Lorenzo Ruiz Student Assistance",
            "university": "University of Santo Tomas",
            "description": "For students in need of financial aid who can work 20–30 hours a week at the university.",
            "tags": ["Financial Aid", "Work-study"],
            "criteria": {"university": ["ust"], "financial_need": ["yes"], "talent": ["work", "volunteer"]},
            "weight": {"university": 2, "financial_need": 3}
        },
        {
            "name": "Vaugirard Scholarship Program",
            "university": "De La Salle University",
            "description": "50 public high school graduates get free tuition and living allowances.",
            "tags": ["Public School", "Full Tuition", "Allowance"],
            "criteria": {"school_type": ["public"], "financial_need": ["yes", "need"]},
            "weight": {"school_type": 2, "financial_need": 3}
        },
        {
            "name": "Don Tomas Mapua Scholarship",
            "university": "Mapúa University",
            "description": "Mapúa students with an average of 1.5 to 1.0 receive 100% tuition discount.",
            "tags": ["Academic Excellence", "Full Tuition"],
            "criteria": {"university": ["mapua"], "average": ["95"], "school_type": ["science", "public"]},
            "weight": {"university": 3, "average": 2}
        },
        {
            "name": "Financial Aid Grant",
            "university": "Various Universities",
            "description": "Provides tuition discounts, dormitory assistance, and allowances for books, food, and transportation.",
            "tags": ["Financial Aid", "Assistance", "Allowance"],
            "criteria": {"financial_need": ["yes", "need"], "school_type": ["public", "private"]},
            "weight": {"financial_need": 3}
        },
        {
            "name": "Athletic or Arts Scholarship",
            "university": "Various Universities",
            "description": "Full or partial scholarships for one year, renewable based on performance.",
            "tags": ["Athletic", "Arts", "Renewable"],
            "criteria": {"talent": ["arts", "sports"]},
            "weight": {"talent": 3}
        }
    ]

    # --- Matching Logic ---
    results = []
    for s in scholarships:
        score = 0
        matched_criteria = []

        for key, user_value in answers.items():
            if not user_value:
                continue

            for keyword in s["criteria"].get(key, []):
                if keyword in user_value or user_value in keyword:
                    score += s["weight"].get(key, 1)
                    matched_criteria.append(key)
                    break

        # Bonus scoring
        if answers['financial_need'] == "yes" and "need" in s["criteria"].get("financial_need", []):
            score += 1
        if answers['average'] in ["95", "90"] and "average" in s["criteria"]:
            score += 1

        if score > 0:
            results.append({
                "name": s["name"],
                "university": s["university"],
                "description": s["description"],
                "tags": s["tags"],
                "score": score,
                "matched": ", ".join(set(matched_criteria))
            })

    results.sort(key=lambda x: x["score"], reverse=True)

    # --- Generate Simplified HTML Output ---
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ScholarPass - Your Recommendations</title>
        <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap" rel="stylesheet">
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }

            body {
                font-family: 'Poppins', sans-serif;
                background-color: #f5f1e8;
                min-height: 100vh;
            }

            /* Navigation */
            nav {
                background: white;
                padding: 1rem 3rem;
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            }

            .logo {
                font-size: 24px;
                font-weight: 700;
                color: #b8883b;
            }

            /* Header */
            .header {
                text-align: center;
                padding: 3rem 2rem 2rem;
                max-width: 1200px;
                margin: 0 auto;
            }

            .header h1 {
                font-size: 2.5rem;
                color: #2c2c2c;
                margin-bottom: 0.5rem;
            }

            .header p {
                font-size: 1.1rem;
                color: #666;
                margin-bottom: 1.5rem;
            }

            .count-badge {
                display: inline-block;
                padding: 8px 20px;
                background-color: #b8883b;
                color: white;
                border-radius: 20px;
                font-weight: 600;
            }

            /* Container */
            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 2rem;
            }

            .scholarships-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
                gap: 20px;
            }

            /* Scholarship Card */
            .scholarship-card {
                background: white;
                border-radius: 12px;
                padding: 24px;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
                transition: all 0.3s ease;
            }

            .scholarship-card:hover {
                transform: translateY(-4px);
                box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
            }

            .card-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 12px;
            }

            .match-score {
                background-color: #b8883b;
                color: white;
                padding: 4px 12px;
                border-radius: 12px;
                font-size: 12px;
                font-weight: 700;
            }

            .scholarship-title {
                font-size: 18px;
                font-weight: 700;
                color: #1a1a1a;
                margin-bottom: 6px;
            }

            .university-name {
                font-size: 13px;
                color: #b8883b;
                font-weight: 600;
                margin-bottom: 12px;
            }

            .scholarship-description {
                font-size: 14px;
                color: #666;
                line-height: 1.6;
                margin-bottom: 14px;
            }

            .tags {
                display: flex;
                flex-wrap: wrap;
                gap: 6px;
                margin-bottom: 14px;
            }

            .tag {
                padding: 5px 12px;
                border-radius: 12px;
                font-size: 11px;
                font-weight: 600;
                background-color: #b8883b;
                color: white;
            }

            .tag:nth-child(2) {
                background-color: #d4a54a;
            }

            .tag:nth-child(3) {
                background-color: #e8c176;
            }

            .matched-criteria {
                padding: 10px;
                background-color: #f0f9f4;
                border-radius: 8px;
                border-left: 3px solid #2d5f3f;
                font-size: 12px;
                color: #2d5f3f;
                font-weight: 500;
            }

            /* No Results */
            .no-results {
                text-align: center;
                padding: 4rem 2rem;
                background: white;
                border-radius: 12px;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
            }

            .no-results h2 {
                font-size: 1.8rem;
                color: #2c2c2c;
                margin-bottom: 1rem;
            }

            .no-results p {
                font-size: 1rem;
                color: #666;
                margin-bottom: 1.5rem;
            }

            .btn {
                padding: 12px 24px;
                background-color: #b8883b;
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: 600;
                font-size: 14px;
                cursor: pointer;
                transition: all 0.3s ease;
            }

            .btn:hover {
                background-color: #9a7030;
                transform: translateY(-2px);
            }

            .btn-myscholarpass {
                display: inline-block;
                padding: 12px 32px;
                background-color: #b8883b;
                color: white;
                text-decoration: none;
                border-radius: 8px;
                font-weight: 600;
                font-size: 14px;
                transition: all 0.3s ease;
                margin-top: 1rem;
            }

            .btn-myscholarpass:hover {
                background-color: #9a7030;
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(184, 136, 59, 0.3);
            }

            /* Responsive */
            @media (max-width: 768px) {
                .header h1 {
                    font-size: 2rem;
                }

                .scholarships-grid {
                    grid-template-columns: 1fr;
                }

                nav, .container {
                    padding: 1rem 1.5rem;
                }
            }
        </style>
    </head>
    <body>
        <nav>
            <div class="logo">ScholarPass</div>
        </nav>

        <div class="header">
            <h1>🎓 Your Scholarship Matches</h1>
            <p>Based on your profile and preferences</p>
    """

    if results:
        html += f'<div class="count-badge">{len(results)} Scholarships Found</div>'
        html += '<br><br><a href="/myscholarpass" class="btn-myscholarpass">Go to My ScholarPass</a>'
    
    html += """
        </div>

        <div class="container">
    """

    if not results:
        html += """
            <div class="no-results">
                <h2>No Matches Found</h2>
                <p>Try adjusting your answers to find more scholarship opportunities</p>
                <button class="btn" onclick="window.history.back()">Try Again</button>
            </div>
        """
    else:
        html += '<div class="scholarships-grid">'
        
        for r in results[:10]:
            html += f"""
                <div class="scholarship-card">
                    <div class="card-header">
                        <div class="match-score">
                            {r['score']} Match Points
                        </div>
                    </div>
                    
                    <div class="scholarship-title">{r['name']}</div>
                    <div class="university-name">{r['university']}</div>
                    <div class="scholarship-description">{r['description']}</div>
                    
                    <div class="tags">
            """
            
            for tag in r['tags']:
                html += f'<span class="tag">{tag}</span>'
            
            html += f"""
                    </div>
                    
                    <div class="matched-criteria">
                        ✓ Matched: {r['matched'].replace('_', ' ').title()}
                    </div>
                </div>
            """
        
        html += '</div>'

    html += """
        </div>
    </body>
    </html>
    """
    
    return html

# --- Serve CSS & JS directly ---
@app.route('/<path:filename>')
def serve_file(filename):
    return send_from_directory('.', filename)

# --- Run ---
if __name__ == '__main__':
    init_db()
    app.run(debug=True)