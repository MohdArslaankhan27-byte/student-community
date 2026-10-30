import profile

from flask import Flask, jsonify, render_template,request, redirect, url_for,flash , session
import sqlite3
from Database.db import db, get_cursor
from Database.function import is_valid_email, email_exists, hash_password,get_user_by_email,get_peers,check_password,get_user_by_id,login_required,delete_old_messages,admin_required
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "your-secret-key"

@app.route("/")
def index():
    # If user is already logged in
    if 'user_id' in session:
        return redirect(url_for('home'))
    return render_template("index.html")

@app.route("/home")
@login_required
def home():
    return render_template("home.html")


@app.route('/peer_profile/<int:user_id>')
@login_required
def peer_profile(user_id):

    cursor = get_cursor()

    cursor.execute(
        "SELECT * FROM users WHERE id = %s",
        (user_id,)
    )

    peer = cursor.fetchone()

    cursor.close()

    if not peer:
        flash("Profile not found.", "error")
        return redirect(url_for('peers'))

    return render_template('profiles/peer_profile.html', peer=peer)




@app.route('/register', methods=['GET', 'POST'])
def register():

    # If user is already logged in
    if 'user_id' in session:
        return redirect(url_for('home'))

    if request.method == 'POST':

        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Check empty fields
        if not name or not email or not password or not confirm_password:
            flash('All fields are required.', 'danger')
            return redirect(url_for('register'))

        # Check email format
        if not is_valid_email(email):
            flash('Please enter a valid email address.', 'danger')
            return redirect(url_for('register'))

        # Check duplicate email
        if email_exists(email):
            flash('This email is already registered.', 'danger')
            return redirect(url_for('register'))

        # Check password confirmation
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('register'))

        # Hash password
        hashed_password = hash_password(password)

        # Insert user
        cursor = get_cursor()

        cursor.execute(
            """
            INSERT INTO users (name, email, password)
            VALUES (%s, %s, %s)
            """,
            (name, email, hashed_password)
        )

        db.commit()

        # Get newly created user ID
        user_id = cursor.lastrowid

        cursor.close()

        # Create session
        session['user_id'] = user_id
        session['user_name'] = name
        session['user_email'] = email

        flash('Registration successful. Welcome!', 'success')

        # Redirect to home
        return redirect(url_for('home'))

    return render_template('register.html')



@app.route('/login', methods=['GET', 'POST'])
def login():

    # If user is already logged in
    if 'user_id' in session:
        return redirect(url_for('home'))

    if request.method == 'POST':

        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = request.form.get('remember')

        # Check required fields
        if not email or not password:
            flash('Email and password are required.', 'danger')
            return redirect(url_for('login'))

        # Get user by email
        user = get_user_by_email(email)

        if not user:
            flash('Invalid email or password.', 'danger')
            return redirect(url_for('login'))

        # Check password
        if not check_password(password, user['password']):
            flash('Invalid email or password.', 'danger')
            return redirect(url_for('login'))

        # Store user information in session
        session['user_id'] = user['id']
        session['user_name'] = user['name']
        session['user_email'] = user['email']

        # Remember me
        if remember:
            session.permanent = True
        else:
            session.permanent = False

        flash('Login successful.', 'success')
        return redirect(url_for('home'))

    return render_template('login.html')

@app.route('/logout')
def logout():

    session.clear()

    flash('You have been logged out.', 'success')

    return redirect(url_for('login'))


@app.route('/basic-info')
@login_required
def basic_info():

    # Send user data to HTML
    return render_template(
        'profiles/basic_info.html'
    )


@app.route('/acad-info')
@login_required
def acad_info():

    # Get logged-in user's data
    user = get_user_by_id(session['user_id'])

    # User not found
    if not user:
        session.clear()
        return redirect(url_for('login'))

    return render_template(
        'profiles/acad_info.html',
        user=user
    )


@app.route('/peers')
@login_required
def peers():

    query = request.args.get('q', '').strip()
    course = request.args.get('course', '').strip()
    semester = request.args.get('semester', '').strip()

    peers = get_peers(
        user_id=session['user_id'],
        query=query,
        course=course,
        semester=semester
    )

    return render_template(
        'peers.html',
        peers=peers
    )



@app.route('/edit-profile', methods=['POST'])
@login_required
def edit_profile():

    field = request.form.get('field')
    value = request.form.get('value', '').strip()

    # Photo update
    if field == 'photo':

        photo = request.files.get('photo')

        if not photo or photo.filename == '':
            flash('Please select a photo.', 'danger')
            return redirect(url_for('more'))

        filename = secure_filename(photo.filename)

        upload_folder = os.path.join(
            app.root_path,
            'static',
            'uploads'
        )

        os.makedirs(upload_folder, exist_ok=True)

        photo.save(os.path.join(upload_folder, filename))

        cursor = get_cursor()

        cursor.execute(
            """
            UPDATE users
            SET photo = %s
            WHERE id = %s
            """,
            (filename, session['user_id'])
        )

        db.commit()
        cursor.close()

        flash('Profile photo updated successfully.', 'success')

        return redirect(url_for('home'))


    # Normal text fields
    allowed_fields = [
        'name',
        'phone',
        'email',
        'dob',
        'gender',
        'address',
        'college',
        'course',
        'branch',
        'semester',
        'roll_number',
        'enrollment_number',
        'academic_year',
        'cgpa',
        'percentage',
        'attendance',
        'subjects',
        'marks',
        'grades',
        'backlogs'
    ]

    if field not in allowed_fields:
        flash('Invalid information selected.', 'danger')
        return redirect(url_for('home'))

    if not value:
        flash('Please enter a value.', 'danger')
        return redirect(url_for('home'))

    cursor = get_cursor()

    sql = f"""
        UPDATE users
        SET {field} = %s
        WHERE id = %s
    """

    cursor.execute(sql, (value, session['user_id']))

    db.commit()
    cursor.close()

    flash('Profile updated successfully.', 'success')

    return redirect(url_for('home'))


@app.route('/send-friend-request/<int:friend_id>', methods=['POST'])
@login_required
def send_friend_request(friend_id):

    user_id = session['user_id']

    cursor = get_cursor()

    cursor.execute("""
        SELECT id
        FROM friends
        WHERE user_id = %s AND friend_id = %s
    """, (user_id, friend_id))

    existing_request = cursor.fetchone()

    if existing_request:
        cursor.close()
        return redirect(url_for('peers'))

    cursor.execute("""
        INSERT INTO friends (user_id, friend_id, status)
        VALUES (%s, %s, 'pending')
    """, (user_id, friend_id))

    db.commit()
    cursor.close()

    return redirect(url_for('peers'))

@app.route('/friend-requests')
@login_required
def friend_requests():

    user_id = session['user_id']

    cursor = get_cursor()

    cursor.execute("""
        SELECT f.id, f.created_at, u.id AS user_id, u.name
        FROM friends f
        JOIN users u ON f.user_id = u.id
        WHERE f.friend_id = %s
        AND f.status = 'pending'
        ORDER BY f.created_at DESC
    """, (user_id,))

    requests = cursor.fetchall()
    cursor.close()

    return render_template('friend_requests.html', requests=requests)


@app.route('/accept-friend-request/<int:request_id>', methods=['POST'])
@login_required
def accept_friend_request(request_id):

    user_id = session['user_id']

    cursor = get_cursor()

    cursor.execute("""
        UPDATE friends
        SET status = 'accepted'
        WHERE id = %s
        AND friend_id = %s
        AND status = 'pending'
    """, (request_id, user_id))

    db.commit()
    cursor.close()

    return redirect(url_for('friend_requests'))

@app.route('/reject-friend-request/<int:request_id>', methods=['POST'])
@login_required
def reject_friend_request(request_id):

    user_id = session['user_id']

    cursor = get_cursor()

    cursor.execute("""
        UPDATE friends
        SET status = 'rejected'
        WHERE id = %s
        AND friend_id = %s
        AND status = 'pending'
    """, (request_id, user_id))

    db.commit()
    cursor.close()

    return redirect(url_for('friend_requests'))


@app.route('/friends')
@login_required
def friends():

    user_id = session['user_id']

    cursor = get_cursor()

    cursor.execute("""
        SELECT u.id, u.name, u.email
        FROM users u
        JOIN friends f
            ON (
                (f.user_id = %s AND f.friend_id = u.id)
                OR
                (f.friend_id = %s AND f.user_id = u.id)
            )
        WHERE f.status = 'accepted'
    """, (user_id, user_id))

    friends_list = cursor.fetchall()
    cursor.close()

    return render_template('friends.html', friends=friends_list)




@app.route('/chat/<int:friend_id>')
@login_required
def chat(friend_id):

    delete_old_messages()

    user_id = session['user_id']

    cursor = get_cursor()


    # =================================
    # GET SELECTED FRIEND
    # =================================

    cursor.execute("""
        SELECT id, name, email
        FROM users
        WHERE id = %s
    """, (friend_id,))

    friend = cursor.fetchone()

    if not friend:
        return "Friend not found", 404


    # =================================
    # GET MY FRIENDS
    # =================================

    cursor.execute("""
        SELECT u.id, u.name, u.email
        FROM users u
        JOIN friends f
            ON (
                (f.user_id = %s AND f.friend_id = u.id)
                OR
                (f.friend_id = %s AND f.user_id = u.id)
            )
        WHERE u.id != %s
    """, (user_id, user_id, user_id))

    friends = cursor.fetchall()


    # =================================
    # GET CHAT MESSAGES
    # =================================

    cursor.execute("""
        SELECT
            id,
            sender_id,
            receiver_id,
            message,
            created_at
        FROM messages
        WHERE
            (sender_id = %s AND receiver_id = %s)
            OR
            (sender_id = %s AND receiver_id = %s)
        ORDER BY created_at ASC
    """, (
        user_id,
        friend_id,
        friend_id,
        user_id
    ))

    messages = cursor.fetchall()


    # =================================
    # OPEN CHAT PAGE
    # =================================

    return render_template(
        'chat.html',
        friend=friend,
        friends=friends,
        messages=messages,
        user_id=user_id
    )


@app.route('/get-messages/<int:friend_id>')
@login_required
def get_messages(friend_id):

    user_id = session['user_id']

    cursor = get_cursor()

    cursor.execute("""
        SELECT
            id,
            sender_id,
            receiver_id,
            message,
            created_at
        FROM messages
        WHERE
            (sender_id = %s AND receiver_id = %s)
            OR
            (sender_id = %s AND receiver_id = %s)
        ORDER BY created_at ASC
    """, (
        user_id,
        friend_id,
        friend_id,
        user_id
    ))

    messages = cursor.fetchall()

    return jsonify({
        'success': True,
        'messages': messages
    })


@app.route('/send-message/<int:friend_id>', methods=['POST'])
@login_required
def send_message(friend_id):

    user_id = session['user_id']

    data = request.get_json()
    message = data.get('message', '').strip() if data else ''

    if not message:
        return jsonify({
            'success': False,
            'error': 'Message cannot be empty'
        }), 400

    cursor = get_cursor()

    cursor.execute("""
        INSERT INTO messages
        (sender_id, receiver_id, message)
        VALUES (%s, %s, %s)
    """, (
        user_id,
        friend_id,
        message
    ))

    db.commit()

    message_id = cursor.lastrowid

    return jsonify({
        'success': True,
        'message': message,
        'message_id': message_id
    })



@app.route('/adminpage', methods=['GET', 'POST'])
@login_required
@admin_required('admin')
def adminpage():

    cursor = get_cursor()

    # -------------------------
    # Upload Student Marks
    # -------------------------

    if request.method == 'POST':

        roll_number = request.form.get('roll_number')
        subject_id = request.form.get('subject_id')
        sessional_1 = request.form.get('sessional_1')
        sessional_2 = request.form.get('sessional_2')
        semester_exam = request.form.get('semester_exam')

        # Find student using roll number
        cursor.execute(
            "SELECT id FROM users WHERE roll_number = %s",
            (roll_number,)
        )

        student = cursor.fetchone()

        if not student:
            cursor.close()

            return jsonify({
                "success": False,
                "message": "Student not found."
            }), 404

        student_id = student['id']

        # Insert / Update marks
        cursor.execute("""
            INSERT INTO student_marks
            (student_id, subject_id, sessional_1, sessional_2, semester_exam)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                sessional_1 = VALUES(sessional_1),
                sessional_2 = VALUES(sessional_2),
                semester_exam = VALUES(semester_exam)
        """, (
            student_id,
            subject_id,
            sessional_1,
            sessional_2,
            semester_exam
        ))

        db.commit()
        cursor.close()

        return jsonify({
            "success": True,
            "message": "Marks uploaded successfully."
        })


    # -------------------------
    # Total Students
    # -------------------------

    cursor.execute(
        "SELECT COUNT(*) AS total FROM users"
    )

    result = cursor.fetchone()
    total_students = result['total']


    # -------------------------
    # Get Subjects
    # -------------------------

    cursor.execute("""
        SELECT id, subject_code, subject_name, semester
        FROM subjects
        ORDER BY semester, subject_name
    """)

    subjects = cursor.fetchall()

    cursor.close()

    return render_template(
    'admin/adminpage.html',
    total_students=total_students,
    active_notices=0,
    pending_results=0,
    system_alerts=0,
    subjects=subjects,
)



# API: Get Marks by Roll Number

@app.route('/api/marks/<roll_no>', methods=['GET'])
def get_marks(roll_no):
    cursor = get_cursor()

    query = """
        SELECT
            u.name AS student_name,
            m.id AS mark_id,
            s.semester,
            s.subject_code AS subcode,
            s.subject_name,
            m.sessional_1,
            m.sessional_2,
            m.semester_exam
        FROM student_marks m
        JOIN users u ON m.student_id = u.id
        JOIN subjects s ON m.subject_id = s.id
        WHERE u.roll_number = %s
        ORDER BY s.semester, s.subject_code
    """

    try:
        cursor.execute(query, (roll_no,))
        records = cursor.fetchall()

        if not records:
            return jsonify({
                "error": "No records found for this Roll Number."
            }), 404

        semesters_data = {}

        for record in records:
            semester = record['semester']

            if semester not in semesters_data:
                semesters_data[semester] = []

            semesters_data[semester].append({
                "id": record['mark_id'],
                "subcode": record['subcode'],
                "subject": record['subject_name'],
                "sessional_1": record['sessional_1'],
                "sessional_2": record['sessional_2'],
                "semExam": record['semester_exam']
            })

        return jsonify({
            "name": records[0]['student_name'],
            "semesters": semesters_data
        })

    except Exception:
        app.logger.exception("Error fetching student marks")
        return jsonify({"error": "Failed to fetch marks."}), 500

    finally:
        cursor.close()




@app.route('/api/marks/update/<int:mark_id>', methods=['PUT'])
@login_required
@admin_required('admin')
def update_student_marks(mark_id):
    cursor = get_cursor()

    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "message": "No data received."
            }), 400

        allowed_fields = {
            'sessional_1',
            'sessional_2',
            'semester_exam'
        }

        if len(data) != 1 or not set(data.keys()).issubset(allowed_fields):
            return jsonify({
                "success": False,
                "message": "Update exactly one valid marks field."
            }), 400

        field, value = next(iter(data.items()))

        try:
            value = float(value)
            if not 0 <= value <= 100:
                raise ValueError
        except (TypeError, ValueError):
            return jsonify({
                "success": False,
                "message": "Marks must be between 0 and 100."
            }), 400

        cursor.execute(
            f"UPDATE student_marks SET {field} = %s WHERE id = %s",
            (value, mark_id)
        )

        if cursor.rowcount == 0:
            cursor.execute(
                "SELECT id FROM student_marks WHERE id = %s",
                (mark_id,)
            )

            if not cursor.fetchone():
                db.rollback()
                return jsonify({
                    "success": False,
                    "message": "Marks record not found."
                }), 404

        db.commit()

        return jsonify({
            "success": True,
            "message": f"{field.replace('_', ' ').title()} updated successfully."
        })

    except Exception:
        db.rollback()
        app.logger.exception("Error updating student marks")

        return jsonify({
            "success": False,
            "message": "Failed to update marks."
        }), 500

    finally:
        cursor.close()




@app.route('/api/marks/delete/<int:mark_id>', methods=['DELETE'])
@login_required
@admin_required('admin')
def delete_student_marks(mark_id):
    cursor = get_cursor()

    try:
        cursor.execute(
            "DELETE FROM student_marks WHERE id = %s",
            (mark_id,)
        )

        if cursor.rowcount == 0:
            return jsonify({
                "success": False,
                "message": "Marks record not found."
            }), 404

        db.commit()

        return jsonify({
            "success": True,
            "message": "Marks deleted successfully."
        })

    except Exception:
        db.rollback()
        app.logger.exception("Error deleting student marks")

        return jsonify({
            "success": False,
            "message": "Failed to delete marks."
        }), 500

    finally:
        cursor.close()


@app.route('/admin/create-coordinator', methods=['POST'])
def create_coordinator():
    if 'user_id' not in session:
        return jsonify({
            'success': False,
            'message': 'Please log in.'
        }), 401

    cursor = get_cursor()

    try:
        # Verify that the logged-in user is an admin
        cursor.execute(
            "SELECT role FROM users WHERE id = %s",
            (session['user_id'],)
        )
        admin = cursor.fetchone()

        if not admin or admin['role'] != 'admin':
            return jsonify({
                'success': False,
                'message': 'Admin access required.'
            }), 403

        email = request.form.get('email', '').strip()

        if not email:
            return jsonify({
                'success': False,
                'message': 'Please enter an email.'
            }), 400

        cursor.execute(
            "SELECT id, role FROM users WHERE email = %s",
            (email,)
        )
        user = cursor.fetchone()

        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found.'
            }), 404

        if user['role'] == 'admin':
            return jsonify({
                'success': False,
                'message': 'An admin cannot be changed to coordinator.'
            }), 400

        if user['role'] == 'coordinator':
            return jsonify({
                'success': False,
                'message': 'This user is already a coordinator.'
            }), 400

        cursor.execute(
            "UPDATE users SET role = %s WHERE id = %s",
            ('coordinator', user['id'])
        )

        cursor.connection.commit()

        return jsonify({
            'success': True,
            'message': 'Coordinator role assigned successfully.'
        })

    except Exception:
        cursor.connection.rollback()
        app.logger.exception("Failed to assign coordinator role")

        return jsonify({
            'success': False,
            'message': 'An unexpected error occurred.'
        }), 500

    finally:
        cursor.close()



@app.context_processor
def inject_user():
    user = None

    if 'user_id' in session:
        user = get_user_by_id(session['user_id'])

    return {
        'user': user
    }


if __name__ == "__main__":
    app.run(debug=True)
