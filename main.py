from flask import Flask, render_template, session, url_for, redirect, request,flash,make_response,jsonify
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash,check_password_hash
import re,os
from datetime import datetime
import subprocess
import json



class StudySystem:
    def __init__(self,name):
        self.app = Flask(name)
        self.app.secret_key = 'StudiosCodersStudySystem'

        # Database connection   
        self.app.config['MYSQL_HOST'] = "localhost"
        self.app.config['MYSQL_USER'] = "root"
        self.app.config['MYSQL_PASSWORD'] = ""
        self.app.config['MYSQL_DB'] = "studios_coder_database"
        self.mysql = MySQL(self.app) 

        self.app.config["UPLOAD_FOLDER_VIDEOS"] ="static/uploads/videos"
        self.app.config["UPLOAD_FOLDER_IMAGES"] ="static/uploads/images"
        self.app.config["UPLOAD_FOLDER_PDF"] ="static/uploads/pdf"
        

    def define_routes(self):
        
        @self.app.route("/",methods=["POST","GET"])
        def homepage():
                return render_template("testhome.html")

        @self.app.route("/role",methods=["POST","GET"])
        def role():
            return render_template("role.html")
        
        #----------Student Login Route----------

        @self.app.route("/login", methods=["POST", "GET"])
        def login():
                if request.method == "POST":
                    stud_id = request.form.get('stud_id')
                    email = request.form.get('email')
                    password = request.form.get('password')
                    cursor = self.mysql.connection.cursor()
                    cursor.execute("SELECT * FROM student_profile WHERE stud_id = %s AND email = %s AND password = %s", (stud_id, email,password))
                    studAcc_found = cursor.fetchone()
                    
                    if studAcc_found:
                        session['user'] = studAcc_found[0]
                        session['role'] = "Student"
                        flash("Successfully logged in!", "success")
                        return redirect('/Dashboard/Student')

                        
                    else:
                        flash("Sorry, your data cannot be found!", "danger")
                        return redirect("/")
                else:
                    return redirect("/")
                
                
        #----------Student Signup Route----------

        @self.app.route("/signup", methods=["POST", "GET"])
        def signup():
            if request.method == "POST":
                idi = request.form.get('studentId')
                name = request.form.get('name')
                mname = request.form.get('middlename')
                lname = request.form.get('lastname')
                gmail = request.form.get('email')
                password = request.form.get('password')
                kurso = request.form.get('course')
                gndr = request.form.get('gender')
                yrlvl = request.form.get('yearLevel')
                sction = request.form.get('section')
                
               
                profile_pic = "/static/images/Defaul_Image.png"
                
            
                    
               
                name_pattern = re.compile(r'^[A-Za-z\s]+$')
                if not (name_pattern.match(name) and 
                        name_pattern.match(mname) and 
                        name_pattern.match(lname)):
                    flash("Please enter only letters in the name fields.", "warning")
                    return redirect("/signup")
                
                
                id_pattern = re.compile(r'^\d{2}-\d{4}-\d{6}$')

                if not id_pattern.match(idi):
                    flash("The ID should follow the format 04-2324-xxxxxx.","warning")
                    return redirect("/signup")
                
                email_pattern = re.compile(r'^[A-Za-z0-9._%+-]+\.ui@phinmaed\.com$')
                if not email_pattern.match(gmail):
                    flash("Email is Invalid !", "danger")
                    return redirect("/signup")

                cursor = self.mysql.connection.cursor()
                
        
                
                # Check if the student is already exists in the database
                cursor.execute("SELECT * FROM student_profile WHERE stud_id = %s" , (idi,))
                existing_student = cursor.fetchone()
                if existing_student:
                    flash("This ID already exist.", "warning")
                    return redirect("/signup")
                
                cursor.execute("SELECT * FROM student_profile WHERE email= %s" , (gmail,))
                existing_email = cursor.fetchone()
                if existing_email:
                    flash("This email is already been used !.", "warning")
                    return redirect("/signup")
                
                
            
               
                cursor.execute("INSERT INTO student_profile(stud_id, firstname, middlename, lastname, gender, email, password,course, year_level, section, profile_pic) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                            (idi,name,mname,lname,gndr,gmail,password,kurso,yrlvl,sction,profile_pic))
                self.mysql.connection.commit()
                cursor.close()
                flash("You're all set! Your registration was successful!","success")
                return redirect("login")
            else:   
                return redirect("/")
            
            
        #----------Student Dashboard Route----------
        @self.app.route("/Dashboard/Student", methods=["POST", "GET"])
        def dashboard_student():
            if 'user' in session and session['role'] == "Student":
                    cursor = self.mysql.connection.cursor()
                    
                    # Fetch all courses available for the student
                    cursor.execute("SELECT * FROM video_lessons")
                    video_lessons =  cursor.fetchall()
                    
                    student_id = session.get('user')
                    
                    # Getting student records
                    cursor.execute("SELECT * FROM student_profile WHERE stud_id = %s", (student_id,))
                    student_records = cursor.fetchall()
                    
                    #Getting number of enrolled lessons
                    cursor.execute("SELECT COUNT(DISTINCT lesson_group_id) FROM video_lesson_enrollments WHERE stud_id=%s",(student_id,))
                    enrolled_lessons = cursor.fetchone()
                    
                    
                    cursor.execute("SELECT COUNT(DISTINCT lesson_group_id) FROM video_lesson_enrollments WHERE stud_id = %s AND status = 'In Progress'", (student_id,))
                    inprogress_lesson = cursor.fetchone()
                    
                    cursor.execute("SELECT  COUNT(DISTINCT lesson_group_id) FROM video_lesson_enrollments WHERE stud_id = %s AND status = 'Completed'", (student_id,))
                    completed_lessons = cursor.fetchone()
                    
                    
                    # Fetch count of video lessons by category
                    cursor.execute("""
                        SELECT category, COUNT(*) AS total_lessons
                        FROM video_lessons
                        GROUP BY category;
                    """)
                    category_counts = cursor.fetchall()
                    
                    
                    # Query to get video lessons not enrolled by the student and those in the same lesson group
                    recommended = """
                        SELECT vl.*, vl.lesson_id, vl.lesson_group_id, vl.thumbnail, t.first_name, t.middle_name, t.profile_pic
                        FROM video_lessons vl
                        LEFT JOIN video_lesson_enrollments vle ON vl.lesson_group_id = vle.lesson_group_id AND vle.stud_id = %s
                        LEFT JOIN teacher_profile t ON vl.teacher_id = t.teacher_id
                        WHERE vle.lesson_group_id IS NULL;

                    """

                    
                    cursor.execute(recommended, (student_id,))
                    recommended_lessons = cursor.fetchall()
                    
                    limited_recommend_lessons = recommended_lessons[:3]
                                        

                    # Pass data to the donut chart
                    chart_data = [{"value": row[1], "name": row[0]} for row in category_counts]
                                    
                                    
                    my_lessons = """
                            SELECT 
                                vl.*, 
                                t.first_name, 
                                t.last_name, 
                                t.profile_pic,
                                (SELECT COUNT(*)
                                    FROM video_lessons vl2
                                    WHERE vl2.lesson_group_id = vl.lesson_group_id
                                ) AS parts_count,
                                vle.status,
                                vle.last_watched_time,
                                vl.max_time 
                            FROM 
                                video_lessons vl
                            JOIN    
                                video_lesson_enrollments vle ON vle.lesson_id = vl.lesson_id
                            JOIN 
                                teacher_profile t ON vl.teacher_id = t.teacher_id
                            WHERE 
                                vle.stud_id = %s 
                            AND 
                                vl.sequence = 1

                    """
                    cursor.execute(my_lessons, (student_id,))
                    my_lessons_data = cursor.fetchall()
                                
                    return render_template("Student-dashboard-2.html",video_lessons=video_lessons, student_records=student_records,
                                        enrolled_lessons= enrolled_lessons,chart_data=chart_data, 
                                        recommended_lessons=recommended_lessons, limited_recommend_lessons= limited_recommend_lessons, 
                                        my_lessons_data=my_lessons_data,inprogress_lesson=inprogress_lesson,completed_lessons=completed_lessons)
            else:   
                flash("Ensure you are signed in.", "danger")
                return redirect('/login')
                        
        #----------Student Profile Route----------
        @self.app.route('/Profile/Student', methods=["POST","GET"])
        def profile_student():
            if 'user' in session and session['role'] == 'Student':
                cursor = self.mysql.connection.cursor()
                
                student_id = session.get('user')
                
                cursor.execute("SELECT * FROM student_profile WHERE stud_id = %s", (student_id,))
                student_records = cursor.fetchall()
                
                return render_template('Student-profile.html', student_records=student_records)
            else:
                flash("Ensure you are signed in.","danger")
                return redirect('/login')
            
           
            
            #---------- Update Student Profile Route----------
            
        @self.app.route("/studentUpdate_profile", methods=["POST", "GET"])
        def studentprofile_update():
            if 'user' in session and session['role'] == "Student":
                if request.method == "POST":
                    student_id = session.get('user')
                    cursor = self.mysql.connection.cursor()

                    # Step 1: Get existing image
                    cursor.execute("SELECT profile_pic FROM student_profile WHERE stud_id=%s", (student_id,))
                    existing_image = cursor.fetchone()
                    existing_image_path = existing_image[0] if existing_image else None  # Extract path if exists

                    # Step 2: Get form values
                    new_firstname = request.form.get("firstname")
                    new_middlename = request.form.get("middlename")
                    new_lastname = request.form.get("lastname")
                    new_email = request.form.get("email")
                    new_phone = request.form.get("phone")

                    uploads_image = existing_image_path  # Default to existing image

                    # Step 3: Handle file upload
                    if 'file' in request.files:
                        file = request.files['file']

                        if file.filename:  # If a new file is uploaded
                            filename = secure_filename(file.filename)
                            file_path = os.path.join(self.app.config["UPLOAD_FOLDER_IMAGES"], filename)

                            # Save the file to the server
                            file.save(file_path)
                            uploads_image = "/static/uploads/images/" + filename

                    try:
                        # Step 4: Update profile in the database
                        cursor.execute(
                            "UPDATE student_profile SET firstname=%s, middlename=%s, lastname=%s, email=%s,profile_pic=%s, phone_number=%s WHERE stud_id=%s",
                            (new_firstname, new_middlename, new_lastname, new_email, uploads_image, new_phone, student_id)
                        )

                        self.mysql.connection.commit()
                        flash("Profile updated successfully!", "success")

                    except Exception as e:
                        flash(f"An error occurred: {str(e)}", "danger")
                        return redirect("/Profile/Student")

                    finally:
                        cursor.close()

                    return redirect("/Profile/Student")
            else:
                flash("You do not have permission to access this page.", "danger")
                return redirect("/login")  # Redirect to login or another appropriate page
            
            
            
            #---------- Delete Profile Pic Route----------
            
        @self.app.route("/delete_profile_image", methods=["POST"])
        def delete_profile_image():
            if 'user' in session and session['role'] == "Student":
                student_id = request.json.get("student_id")  
                cursor = self.mysql.connection.cursor()

                try:
                
                    cursor.execute("SELECT profile_pic FROM student_profile WHERE stud_id=%s", (student_id,))
                    current_image = cursor.fetchone()

            
                    if current_image and current_image[0] == "/static/images/Defaul_Image.png":
                        flash("No Image Uploaded.", "danger")
                        return jsonify(success=False), 400  
                    
                    if current_image and current_image[0] != "/static/images/Defaul_Image.png":
                        image_path = current_image[0].replace("/static", "static")
                        if os.path.exists(image_path):
                            os.remove(image_path)

                
                    flash("Image Deleted Successfully.", "success")
                    cursor.execute("UPDATE student_profile SET profile_pic='/static/images/Defaul_Image.png' WHERE stud_id=%s", (student_id,))
                    self.mysql.connection.commit()


                    return jsonify(success=True), 200  
                except Exception as e:
                    self.mysql.connection.rollback()  
                    flash("An error occurred while deleting the image.", "danger")
                    return jsonify(success=False, error=str(e)), 500
                finally:
                    cursor.close()

            return jsonify(success=False), 401  




            #---------- Update Student Password Route----------
            

        @self.app.route("/passwordUpdate/student", methods=["POST", "GET"])
        def changepass_student():
            if 'user' in session and session['role'] == "Student":
                if request.method == "POST":
                    # Get form values
                    current_password_input = request.form.get("password")
                    new_password = request.form.get("newpassword")
                    re_new_password = request.form.get("renewpassword")
                    
                    student_id = session.get('user')
                    cursor = self.mysql.connection.cursor()

                    # Fetch the current password from the database
                    cursor.execute("SELECT password FROM student_profile WHERE stud_id = %s", (student_id,))
                    result = cursor.fetchone()

                    if result:
                        stored_password = result[0]  # Assuming password is stored in the first column of the result

                        # Compare the current password input with the stored password
                        if current_password_input == stored_password:
                            if new_password == re_new_password:
                                try:
                                    # Update the password in the database
                                    cursor.execute(
                                        "UPDATE student_profile SET password=%s WHERE stud_id=%s",
                                        (new_password, student_id)
                                    )
                                    self.mysql.connection.commit()
                                    flash("Password updated successfully!", "success")
                                except Exception as e:
                                    flash(f"An error occurred: {str(e)}", "danger")
                            else:
                                flash("New passwords do not match", "danger")
                        else:
                            flash("Current password is incorrect", "danger")
                    else:
                        flash("Student not found", "danger")

                    cursor.close()
                
            return redirect("/Profile/Student")


        @self.app.route('/view_lesson', methods=["POST", "GET"])
        def get_lesson():
            if 'user' in session:
                cursor = self.mysql.connection.cursor()
                student_id = session.get('user')
                lesson_group_id = request.form.get('lesson_group_id')
                selected_lesson_id = request.form.get('lesson_id')
                status = 'In Progress'

                print(selected_lesson_id)
                print(lesson_group_id)


                if not lesson_group_id or not selected_lesson_id:
                    flash("Lesson group or lesson ID is missing", "warning")
                    return redirect('/Dashboard/Student')

                try:
                
                    cursor.execute(""" 
                        SELECT vl.*, t.first_name, t.last_name 
                        FROM video_lessons vl
                        JOIN teacher_profile t ON vl.teacher_id = t.teacher_id
                        WHERE vl.lesson_group_id = %s
                        ORDER BY vl.sequence ASC
                    """, (lesson_group_id,))
                    group_lessons_data = cursor.fetchall()
                    
                    
                    cursor.execute("""
                        SELECT last_watched_time 
                        FROM video_lesson_enrollments 
                        WHERE stud_id = %s AND lesson_id = %s
                    """,(student_id, selected_lesson_id))
                    
                    last_watched_time = cursor.fetchone()
                    last_watched_time = last_watched_time[0] if last_watched_time else 0 

            
                    cursor.execute("SELECT lesson_id FROM video_lessons WHERE lesson_group_id = %s", (lesson_group_id,))
                    lessons = cursor.fetchall()

                    for lesson in lessons:
                        lesson_id = lesson[0]
                        cursor.execute(
                            "SELECT * FROM video_lesson_enrollments WHERE lesson_id = %s AND stud_id = %s", 
                            (lesson_id, student_id)
                        )
                        existing_enrollment = cursor.fetchone()

                        if not existing_enrollment:
                            cursor.execute(
                                "INSERT INTO video_lesson_enrollments (lesson_id, stud_id, status, lesson_group_id) "
                                "VALUES (%s, %s, %s, %s)", 
                                (lesson_id, student_id, status, lesson_group_id)
                            )

                    
                    self.mysql.connection.commit()

                
                    cursor.execute(""" 
                        SELECT 
                            vl.lesson_id, vl.title, vl.filepath, vl.description, 
                            vl.department, vl.category, vl.sequence, 
                            t.first_name AS teacher_first_name, 
                            t.last_name AS teacher_last_name, t.profile_pic
                        FROM 
                            video_lessons vl
                        JOIN 
                            teacher_profile t ON vl.teacher_id = t.teacher_id
                        WHERE 
                            vl.lesson_group_id = %s AND vl.lesson_id = %s
                        ORDER BY 
                            vl.sequence ASC
                    """, (lesson_group_id, selected_lesson_id))
                    lessons_data = cursor.fetchall()

                
                    cursor.execute("SELECT COUNT(*) as total_comments FROM comments WHERE lesson_id = %s", (selected_lesson_id,))
                    comments_count = cursor.fetchone()
                    
                    
                    cursor.execute("""
                            SELECT 
                                vle.last_watched_time,
                                vl.max_time 
                            FROM 
                                video_lessons vl
                            JOIN 
                                video_lesson_enrollments vle ON vle.lesson_id = vl.lesson_id
                            JOIN 
                                teacher_profile t ON vl.teacher_id = t.teacher_id
                            WHERE 
                                vle.stud_id =  %s
                                AND vl.lesson_id = %s
                    """,(student_id,selected_lesson_id))
                    
                    lesson_progress_viewing = cursor.fetchall()
                    
                    cursor.execute("""
                        SELECT status 
                        FROM video_lesson_enrollments 
                        WHERE stud_id = %s AND lesson_id = %s
                    """, (student_id, selected_lesson_id))
                    current_status = cursor.fetchone()
                                        
                    if current_status != "Completed":
                        # Update the enrollment status to 'In Progress'
                        cursor.execute(""" 
                            UPDATE video_lesson_enrollments 
                            SET status = %s
                            WHERE stud_id = %s AND lesson_group_id= %s
                        """, (status, student_id, lesson_group_id))
                        self.mysql.connection.commit()

                    cursor.execute("""
                        SELECT  related_files, related_link 
                        FROM video_lessons 
                        WHERE lesson_id = %s
                    """, (selected_lesson_id,))
                    related_files_vl = cursor.fetchall()
                    

                    # Fetch comments (from both students and teachers)
                    cursor.execute(""" 
                        SELECT 
                            comments.comment_text, comments.created_at, 
                            COALESCE(student_profile.firstname, teacher_profile.first_name) AS firstname, 
                            COALESCE(student_profile.lastname, teacher_profile.last_name) AS lastname,
                            COALESCE(student_profile.profile_pic, teacher_profile.profile_pic) AS profile_pic,
                            comments.comment_id, comments.user_id, comments.user_role
                        FROM 
                            comments
                        LEFT JOIN 
                            student_profile ON comments.user_id = student_profile.stud_id AND comments.user_role = 'Student'
                        LEFT JOIN 
                            teacher_profile ON comments.user_id = teacher_profile.teacher_id AND comments.user_role = 'Teacher'
                        WHERE 
                            comments.lesson_id = %s
                        ORDER BY 
                            comments.created_at DESC
                    """, (selected_lesson_id,))
                    comments = cursor.fetchall()

                    comments_data = []
                    for comment in comments:
                        comment_text, created_at, first_name, last_name, profile_pic, comment_id, user_id, user_role = comment
                        time_difference = datetime.now() - created_at
                        time_ago = calculate_time_ago(time_difference)
                        comments_data.append((comment_text, time_ago, first_name, last_name, profile_pic, comment_id, user_id, user_role))
                    
        
                
                    cursor.execute("SELECT * FROM student_profile WHERE stud_id = %s", (student_id,))
                    student_records = cursor.fetchall()

                
                    return render_template('Student-video_lessons-viewing.html', 
                                        student_records=student_records, 
                                        group_lessons_data=group_lessons_data, 
                                        lessons_data=lessons_data, 
                                        comments_count=comments_count,
                                        comments=  comments ,
                                        last_watched_time=last_watched_time, 
                                        lesson_progress_viewing=lesson_progress_viewing,
                                        related_files_vl =related_files_vl,
                                        comments_data=comments_data)
                except Exception as e:
                    flash(f"An error occurred: {str(e)}", "danger")
                    return redirect('/Dashboard/Student')
            return redirect("/")

        def calculate_time_ago(time_difference):
            if time_difference.days >= 365:
                return f"{time_difference.days // 365} year{'s' if time_difference.days // 365 > 1 else ''} ago"
            elif time_difference.days >= 30:
                return f"{time_difference.days // 30} month{'s' if time_difference.days // 30 > 1 else ''} ago"
            elif time_difference.days >= 7:
                return f"{time_difference.days // 7} week{'s' if time_difference.days // 7 > 1 else ''} ago"
            elif time_difference.days >= 1:
                return f"{time_difference.days} day{'s' if time_difference.days > 1 else ''} ago"
            else:
                hours = time_difference.seconds // 3600
                if hours > 0:
                    return f"{hours} hour{'s' if hours > 1 else ''} ago"
                else:
                    minutes = time_difference.seconds // 60
                    return f"{minutes} minute{'s' if minutes > 1 else ''} ago"

        @self.app.route('/send_comment', methods=["POST", "GET"])
        def send_comment():
            cursor = self.mysql.connection.cursor()
            lesson_id = request.form.get('lesson_id')
            action = request.form.get('action')
            comment_text = request.form.get("comments")
            lesson_group_id = request.form.get('lesson_group_id')
            user_id = session.get('user') 
            user_role = session.get('role')  

            print("Lesson Enrollment Details:")
            print(f"Lesson ID: {lesson_id}")
            print(f"Lesson Group ID: {lesson_group_id}")
            print(f"User ID: {user_id}")
            print(f"Action: {action}")
            print(f"User Role: {user_role}")

            try:
                cursor.execute(
                    "INSERT INTO comments (lesson_id, user_id, user_role, comment_text, created_at) VALUES (%s, %s, %s, %s, NOW())",
                    (lesson_id, user_id, user_role, comment_text)
                )
                self.mysql.connection.commit()

            
                if user_role == 'Student':
                    cursor.execute("SELECT profile_pic, firstname, lastname FROM student_profile WHERE stud_id = %s", (user_id,))
                elif user_role == 'Teacher':
                    cursor.execute("SELECT profile_pic, first_name AS firstname, last_name AS lastname FROM teacher_profile WHERE teacher_id = %s", (user_id,))

                user_data = cursor.fetchone()  
            
                if user_data:
                    profile_pic, firstname, lastname = user_data
                    user_name = f"{firstname} {lastname[0]}." 
                else:
                    profile_pic = '/static/images/Defaul_Image.png' 
                    user_name = 'Anonymous'

                response = {
                    'success': True,
                    'message': 'Your comment has been posted!',
                    'comment': comment_text,
                    'photo_url': profile_pic,
                    'user_name': user_name,
                    'created_at': datetime.now().isoformat()
                }
            except Exception as e:
            
                self.mysql.connection.rollback()
                response = {'success': False, 'message': f'Error: {str(e)}'}
            cursor.close()
            return jsonify(response)


        @self.app.route("/Take_Lesson", methods=["POST", "GET"])
        def take_lesson():
            if request.method == "POST":  
                cursor = self.mysql.connection.cursor()
                lesson_id = request.form.get('lesson_id')
                lesson_group_id = request.form.get('lesson_group_id')
                status = "Not Started"
                student_id = session.get('user')
                
                try:
                    cursor.execute("SELECT lesson_id FROM video_lessons WHERE lesson_group_id = %s", (lesson_group_id,))
                    lessons = cursor.fetchall()  

                    for lesson in lessons:
                        lesson_id = lesson[0]  
                        cursor.execute("SELECT * FROM video_lesson_enrollments WHERE lesson_id = %s AND stud_id = %s", (lesson_id, student_id))
                        existing_enrollment = cursor.fetchone()

                
                        if existing_enrollment is None:
                            cursor.execute(
                                "INSERT INTO video_lesson_enrollments (lesson_id, stud_id, status, lesson_group_id) VALUES (%s, %s, %s, %s)",
                                (lesson_id, student_id, status, lesson_group_id)
                            )
                        elif existing_enrollment is not None:
                            flash("This lesson is already added!", "warning")
                            break

                        self.mysql.connection.commit()
                        flash("Lesson added successfully!", "success")
                    return redirect('/Dashboard/Student') 
                
                except Exception as e:
                    flash(str(e), "danger")
                    return redirect('/Dashboard/Student')
        


        @self.app.route('/delete_comment', methods=["POST"])
        def comment_del():
            comment_id = request.form.get('comment_id')
            
          
            
            if comment_id:
                cursor = self.mysql.connection.cursor()
                cursor.execute("DELETE FROM comments WHERE comment_id = %s", (comment_id,))
                self.mysql.connection.commit()
                cursor.close()
                
                flash(f'Comment Deleted !', 'danger')
                return jsonify(success=True)
            
            return jsonify(success=False, message="Comment ID is required")

        @self.app.route('/save_time', methods=['POST'])
        def save_time():
            data = request.json
            lesson_id = data.get('video_id')
            last_time_watched = float(data.get('current_time'))  
            cursor = self.mysql.connection.cursor()
            student_id = session.get('user')
            
           
            cursor.execute("SELECT max_time FROM video_lessons WHERE lesson_id=%s", (lesson_id,))
            maxtime = cursor.fetchone()

          
            maximum_time = float(maxtime[0]) if maxtime else 0.0

            print(f"Video ID: {lesson_id}, Current Time: {last_time_watched}, Max Time: {maximum_time}")

            
            tolerance = 0.5  
            if abs(last_time_watched - maximum_time) <= tolerance:
                print("True - The lesson is fully watched!")
              
                cursor.execute(
                    "UPDATE video_lesson_enrollments SET status = 'Completed' WHERE stud_id = %s AND lesson_id = %s",
                    (student_id, lesson_id)
                )
            else:
                print("False - The lesson is not yet completed.")
            
           
            cursor.execute(
                "UPDATE video_lesson_enrollments SET last_watched_time = %s WHERE stud_id = %s AND lesson_id = %s",
                (last_time_watched, student_id, lesson_id)
            )
            
            
            self.mysql.connection.commit()
            
            cursor.close()

            return jsonify(success=True)

        @self.app.route('/delete-comment', methods=["POST"])
        def delete_comment():
            cursor = self.mysql.connection.cursor()
            
            comment_id = request.form.get('data-comment-id')
            
            if comment_id:  
                cursor.execute("DELETE FROM comments WHERE comment_id=%s", (comment_id,))
                self.mysql.connection.commit()  
                cursor.close()  
                return jsonify({"status": "success", "message": "Comment deleted successfully."})
            
            return jsonify({"status": "error", "message": "Comment ID not provided."}), 400

            
        @self.app.route("/Unenroll-Lesson", methods=["POST","GET"])
        def unenroll_lesson():
            if 'user' in session and session['role'] == "Student":
                if request.method == "POST":
                    student_id = session.get("user")
                    lesson_id = request.form.get("lesson_id")
                    lesson_group_id= request.form.get('lesson_group_id')
                    
                    cursor = self.mysql.connection.cursor()
                    
                    cursor.execute("DELETE FROM video_lesson_enrollments WHERE lesson_group_id = %s AND stud_id = %s", (lesson_group_id, student_id))

                    
                    print(lesson_group_id)
                    
                    self.mysql.connection.commit()
                    cursor.close()    
                flash("Unenrolled from lesson successfully.", "success")
                return redirect("/Student/My-Lesson")
            else:
                flash("Error: Unauthorized request!", "danger")
                return redirect("/Student/My-Lesson")

        #----------Student My Lesson Route----------    
        @self.app.route('/Student/My-Lesson', methods=["POST","GET"])
        def student_lesson():
            if 'user' in session and session['role'] == 'Student':
                    student_id = session.get('user')
                    lesson_id = request.form.get('lesson_id')
                    cursor = self.mysql.connection.cursor()
                    lesson_group_id = request.form.get('lesson_group_id')
            
                    
                    #Getting number of enrolled lessons
                    cursor.execute("SELECT COUNT( DISTINCT lesson_group_id ) FROM video_lesson_enrollments WHERE stud_id=%s",(student_id,))
                    enrolled_lessons = cursor.fetchone()
                    
                    cursor.execute("SELECT COUNT(DISTINCT lesson_group_id) FROM video_lesson_enrollments WHERE stud_id = %s AND status = 'In Progress'", (student_id,))
                    inprogress_lesson = cursor.fetchone()

                    cursor.execute("SELECT  COUNT(DISTINCT lesson_group_id) FROM video_lesson_enrollments WHERE stud_id = %s AND status = 'Not Started'", (student_id,))
                    notstarted_lesson = cursor.fetchone()
                    
                    cursor.execute("SELECT  COUNT(DISTINCT lesson_group_id) FROM video_lesson_enrollments WHERE stud_id = %s AND status = 'Completed'", (student_id,))
                    completed_lessons = cursor.fetchone()
                    
                    
                    cursor.execute("SELECT * FROM student_profile WHERE stud_id = %s", (student_id,))
                    student_records = cursor.fetchall()
            
                    
                    cursor.execute("""
                            SELECT 
                                vl.lesson_id, 
                                vl.title, 
                                vl.filepath, 
                                vl.description, 
                                vl.department, 
                                vl.category, 
                                vl.sequence, 
                                t.first_name AS teacher_first_name, 
                                t.last_name AS teacher_last_name, 
                                t.profile_pic
                            FROM 
                                video_lessons vl
                            JOIN 
                                teacher_profile t ON vl.teacher_id = t.teacher_id
                            WHERE 
                                vl.lesson_group_id = %s AND vl.lesson_id = %s
                            GROUP BY 
                                vl.sequence, vl.lesson_id, t.first_name, t.last_name, t.profile_pic
                            ORDER BY 
                                vl.sequence ASC
                        """,  (lesson_group_id,lesson_id ))
                    lessons_data = cursor.fetchall()   
                    
                    my_lessons = """
                            SELECT 
                                vl.*, 
                                t.first_name, 
                                t.last_name, 
                                t.profile_pic,
                                (SELECT COUNT(*)
                                    FROM video_lessons vl2
                                    WHERE vl2.lesson_group_id = vl.lesson_group_id
                                ) AS parts_count,
                                vle.status,
                                vle.last_watched_time,
                                vl.max_time 
                            FROM 
                                video_lessons vl
                            JOIN 
                                video_lesson_enrollments vle ON vle.lesson_id = vl.lesson_id
                            JOIN 
                                teacher_profile t ON vl.teacher_id = t.teacher_id
                            WHERE 
                                vle.stud_id = %s 
                    """
                    cursor.execute(my_lessons, (student_id,))
                    my_lessons_data = cursor.fetchall()
                    
                    
                    cursor.execute(
                        """ 
                            SELECT vl.*, 
                                t.first_name, 
                                t.last_name, 
                                t.profile_pic,
                                (SELECT COUNT(*)
                                    FROM video_lessons vl2
                                    WHERE vl2.lesson_group_id = vl.lesson_group_id) AS parts_count,
                                vle.status,
                                vle.last_watched_time,
                                vl.max_time 
                            FROM video_lessons vl
                            JOIN video_lesson_enrollments vle ON vle.lesson_id = vl.lesson_id
                            JOIN teacher_profile t ON vl.teacher_id = t.teacher_id
                            WHERE vle.stud_id = %s
                                AND vle.status = 'In Progress'
                                AND vl.sequence = 1;
            
                        """,(student_id,)
                    )
                    my_lessons_data_inprogress = cursor.fetchall()
                    
                    
                    cursor.execute(
                        """ 
                            SELECT vl.*, 
                                t.first_name, 
                                t.last_name, 
                                t.profile_pic,
                                (SELECT COUNT(*)
                                    FROM video_lessons vl2
                                    WHERE vl2.lesson_group_id = vl.lesson_group_id) AS parts_count,
                                vle.status,
                                vle.last_watched_time,
                                vl.max_time 
                            FROM video_lessons vl
                            JOIN video_lesson_enrollments vle ON vle.lesson_id = vl.lesson_id
                            JOIN teacher_profile t ON vl.teacher_id = t.teacher_id
                            WHERE vle.stud_id = %s 
                                AND vle.status = 'Not Started'
                                AND vl.sequence = 1;
            
                        """,(student_id,)
                    )
                    my_lessons_data_notstarted = cursor.fetchall()
                    
                    
                    
                    cursor.execute(
                        """ 
                            SELECT vl.*, 
                                t.first_name, 
                                t.last_name, 
                                t.profile_pic,
                                (SELECT COUNT(*)
                                    FROM video_lessons vl2
                                    WHERE vl2.lesson_group_id = vl.lesson_group_id) AS parts_count,
                                vle.status,
                                vle.last_watched_time,
                                vl.max_time 
                            FROM video_lessons vl
                            JOIN video_lesson_enrollments vle ON vle.lesson_id = vl.lesson_id
                            JOIN teacher_profile t ON vl.teacher_id = t.teacher_id
                            WHERE vle.stud_id = %s 
                                AND vle.status = 'Completed'
                                AND vl.sequence = 1;
            
                        """,(student_id,)
                    )
                    my_lessons_data_completed = cursor.fetchall()
            
                    
                    return render_template('Student-my_lesson.html',student_records=student_records, enrolled_lessons= enrolled_lessons, 
                    lessons_data=lessons_data,  my_lessons_data= my_lessons_data, inprogress_lesson= inprogress_lesson, 
                    notstarted_lesson=notstarted_lesson,completed_lessons=completed_lessons,my_lessons_data_inprogress=my_lessons_data_inprogress,  my_lessons_data_notstarted= my_lessons_data_notstarted, my_lessons_data_completed= my_lessons_data_completed  )
            else:
                flash("Connection error!","danger")
                return redirect('/')

        #----------Student My Performance Route----------
        @self.app.route('/Explore-New/Lessons', methods=["POST","GET"])
        def explore_mylesson():
            if 'user' in session and session['role'] == 'Student':
             
                    cursor = self.mysql.connection.cursor()
                    
                    student_id = session.get('user')
                    
                    cursor.execute("SELECT * FROM student_profile WHERE stud_id = %s", (student_id,))
                    student_records = cursor.fetchall()
                    
                    cursor.execute("SELECT DISTINCT category FROM video_lessons")
                    categories = cursor.fetchall()
                    
                    
                    cursor.execute( """
                                SELECT 
                                    DISTINCT vl.lesson_group_id,
                                    vl.title,
                                    vl.thumbnail,
                                    tp.first_name, 
                                    tp.middle_name, 
                                    tp.last_name,
                                    tp.profile_pic,
                                    vl.lesson_id
                                FROM 
                                    video_lessons vl
                                JOIN 
                                    teacher_profile tp ON vl.teacher_id = tp.teacher_id
                                ORDER BY 
                                    vl.uploaded_time DESC;
                                
                                
                                """)
                    recent_uploads = cursor.fetchall()
                    
                
                    return render_template('Student-explore-lesson.html',student_records=student_records,recent_uploads=recent_uploads,categories=categories )
            else:
                flash(" Ensure you are signed in.","danger")
                return redirect('/login')
        
        
         #----------Student My Performance Route----------
 
        #---------- Help & Support Route----------
        @self.app.route('/Help-Center', methods=["GET"])
        def Help_Center():
            if 'user' in session and session['role'] == 'Student':
                
                student_id = session.get('user')
                
                cursor = self.mysql.connection.cursor()
                cursor.execute("SELECT * FROM student_profile WHERE stud_id = %s", (student_id,))
                student_records = cursor.fetchall() 
                
                
                return render_template('help-center.html',student_records=student_records)
            else:
                flash(" Ensure you are signed in.","danger")
                return redirect('/login')
            
        # ----------Dashboard Student Contact Route----------
        
        @self.app.route('/Help/Contact', methods=["POST", "GET"])
        def help_contact():
            if 'user' in session and session['role'] == 'Student':
                
                
                student_id = session.get('user')
                
                cursor = self.mysql.connection.cursor()
                cursor.execute("SELECT * FROM student_profile WHERE stud_id = %s", (student_id,))
                student_records = cursor.fetchall()
                
                return render_template('contact-page.html',student_records=student_records )
            else:
                flash(" Ensure you are signed in.","danger")
                return redirect('/login')




        #----------Teacher Login Route----------  
        @self.app.route("/teacher-login", methods=["POST", "GET"])
        def teacher_login():
            if request.method == "POST":
                teacher_id = request.form.get('teacher_id')
                email_add = request.form.get('email_add')
                password = request.form.get('password')
                cursor = self.mysql.connection.cursor()
                cursor.execute("SELECT * FROM teacher_profile WHERE teacher_id = %s AND email_add = %s AND password = %s", (teacher_id, email_add,password))
                teacherAcc_found = cursor.fetchone()
                
                
                if teacherAcc_found:
                    session['user'] = teacherAcc_found[0]
                    session['role'] = 'Teacher'
                    flash("Successfully logged in!", "success")
                    return redirect('/Dashboard-Teacher')   
                else:
                    flash("Sorry, your data cannot be found!", "danger")
                    return redirect("/")
            else:
                return redirect("/")
            

        #----------Teacher Signup Route---------
        @self.app.route('/teacher_signup', methods=["POST", "GET"])
        def teacher_signup():
            if request.method == "POST":
                teacher_id = request.form.get('teacher_id')
                first_name = request.form.get("first_name")
                middle_name = request.form.get("middle_name")
                last_name = request.form.get("last_name")
                email_add = request.form.get("email_add")
                password = request.form.get("password")
                department = request.form.get("department")
                
                default_img = "/static/images/Defaul_Image.png"
                


                # Validate names contain only letters
                name_pattern = re.compile(r'^[A-Za-z\s]+$')
                if not (name_pattern.match(first_name) and 
                        name_pattern.match(middle_name) and 
                        name_pattern.match(last_name)):
                    flash("Please enter only letters in the name fields.", "warning")
                    return redirect("/teacher_signup")
                
                # Regular expression for ID pattern: 04-2324-xxxxxx
                id_pattern = re.compile(r'^\d{2}-\d{4}-\d{6}$')

                if not id_pattern.match(teacher_id):
                    flash("The ID should follow the format 04-2324-xxxxxx.","warning register")
                    return redirect("/teacher_signup")


                cursor = self.mysql.connection.cursor()

                # Check if the teacher is already exists in the database
                cursor.execute("SELECT * FROM teacher_profile WHERE email_add = %s AND teacher_id = %s" , (email_add, teacher_id))
                existing_teacher = cursor.fetchone()

                if existing_teacher:
                    flash("This data is already exist !", "warning")
                    return redirect("/teacher_signup")
                
                # Inserting new teacher data into the database
                cursor.execute("INSERT INTO teacher_profile (teacher_id, first_name, middle_name, last_name, email_add, password, department, profile_pic) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                            (teacher_id, first_name, middle_name, last_name, email_add, password, department, default_img))
                self.mysql.connection.commit()
                cursor.close()
                flash("You're all set! Your registration was successful!","success")
                return redirect('/')
            else:
                return redirect("/")

        #----------Teacher Dashboard Route----------
        @self.app.route("/Dashboard-Teacher", methods=["POST", "GET"])
        def dashboard_teacher():
            if 'user' in session and session['role'] == "Teacher":
                cursor = self.mysql.connection.cursor()
                teacher_id = session.get('user')
                
                cursor.execute("SELECT * FROM teacher_profile WHERE teacher_id=%s", (teacher_id,))
                teacher_records = cursor.fetchall()
                
                # Uploaded Count Lesson Fetch
                cursor.execute("SELECT COUNT(DISTINCT lesson_group_id) FROM video_lessons WHERE teacher_id =%s",(teacher_id,))
                num_lesson = cursor.fetchone()
                
                # Uploaded Lesson Fetch
                cursor.execute("SELECT * FROM video_lessons WHERE teacher_id =%s",(teacher_id,))
                my_uploaded_lessons = cursor.fetchall()
                
                #Count the total enrolees of the teacher uploaded lessons 
                enrollees = (
                    """ 
                    SELECT COUNT(DISTINCT ve.stud_id, vl.lesson_group_id) AS number_of_enrollees
                    FROM video_lesson_enrollments ve
                    JOIN video_lessons vl ON ve.lesson_id = vl.lesson_id
                    WHERE vl.teacher_id = %s;
                    """
                )
                
                cursor.execute(enrollees, (teacher_id,))
                total_enrollees = cursor.fetchone()
                
                # Count the total enrollees based on the year level
                uploaded_enrollees = (
                    """
                    SELECT 
                        sp.year_level, 
                        COUNT(DISTINCT ve.stud_id, vl.lesson_group_id) AS number_of_enrollees
                    FROM 
                        video_lesson_enrollments ve
                    JOIN 
                        video_lessons vl ON ve.lesson_id = vl.lesson_id
                    JOIN 
                        student_profile sp ON ve.stud_id = sp.stud_id
                    WHERE 
                        vl.teacher_id = %s
                    GROUP BY 
                        sp.year_level;
                    """
                )

                cursor.execute(uploaded_enrollees, (teacher_id,))
                total_uploaded_enrollees = cursor.fetchall()
                
                
                # top uploaders
                cursor.execute(
                    """        
                    SELECT 
                        tp.first_name, 
                        tp.last_name, 
                        tp.profile_pic,
                        COUNT(vl.lesson_id) AS total_uploads
                    FROM 
                        video_lessons vl
                    JOIN 
                        teacher_profile tp 
                        ON vl.teacher_id = tp.teacher_id
                    GROUP BY 
                        tp.teacher_id
                    ORDER BY 
                        total_uploads DESC;
                    """
                )                
                
                uploader = cursor.fetchall()
                
                top_uploaders = uploader[:3]
                
                # Prepare data for the ECharts
                chart_data = []
                for year_level, number_of_enrollees in total_uploaded_enrollees:
                    chart_data.append({"value": number_of_enrollees, "name": year_level})

                
                cursor.execute( """
                            SELECT 
                                vl.*, 
                                tp.first_name, 
                                tp.middle_name, 
                                tp.last_name,
                                tp.profile_pic
                            FROM 
                                video_lessons vl
                            JOIN 
                                teacher_profile tp ON vl.teacher_id = tp.teacher_id
                            ORDER BY 
                                vl.uploaded_time DESC 
                            LIMIT 3;
                            """)
                recent_uploads = cursor.fetchall()
                
                    
                cursor.execute("""
                        SELECT 
                    COUNT(vle.lesson_id) AS total_completed_lessons
                FROM 
                    video_lesson_enrollments AS vle
                JOIN 
                    video_lessons AS vl ON vle.lesson_id = vl.lesson_id
                JOIN 
                    teacher_profile AS tp ON vl.teacher_id = tp.teacher_id
                WHERE 
                    vle.status = 'Completed'
                    AND tp.teacher_id = %s  

                """,(teacher_id,))
                
                completers_count = cursor.fetchone()
            
                
                return render_template("Teacher-dashboard-2.html",teacher_records=teacher_records, num_lesson=num_lesson,  total_enrollees= total_enrollees,chart_data=chart_data,  my_uploaded_lessons=  my_uploaded_lessons,  recent_uploads = recent_uploads,top_uploaders=top_uploaders,completers_count=completers_count)
                
            else:
                flash(" Ensure you are signed in.","danger")
                return redirect('/')
    
        #----------Teacher Profile Route----------
        @self.app.route("/Profile/Teacher", methods=["POST", "GET"])
        def profile_teacher():
            if 'user' in session and session['role'] == "Teacher":
                cursor = self.mysql.connection.cursor()
                teacher_id = session.get('user')
                
                
                cursor.execute("SELECT * FROM teacher_profile WHERE teacher_id=%s", (teacher_id,))
                teacher_records = cursor.fetchall()
            
                
                return render_template("Teacher-profile.html", teacher_records=teacher_records)
            else:
                flash(" Ensure you are signed in.","danger")
                return redirect('/')

        @self.app.route("/teacherUpdate_profile", methods=["POST","GET"])
        def teacherprofile_update():
            if 'user' in session and session['role'] == "Teacher":
                if request.method == "POST":
                    cursor = self.mysql.connection.cursor()
                    teacher_id = session.get('user')
                
                    # Step 1: Get existing image
                    cursor.execute("SELECT profile_pic FROM teacher_profile WHERE teacher_id=%s", (teacher_id,))
                    existing_image = cursor.fetchone()
                    existing_image_path = existing_image[0] if existing_image else None  # Extract path if exists
                    
                    # Step 2: Get form values
                    new_firstname = request.form.get("first_name")
                    new_middle = request.form.get("middle_name")
                    new_lastname = request.form.get("last_name")
                    new_email = request.form.get("email")
                    new_phone = request.form.get("phone")
                    
                    uploads_image = existing_image_path
                    
                    if 'file' in request.files:
                        file = request.files['file']
                        
                        if file.filename:
                            filename = secure_filename(file.filename)
                            file_path = os.path.join(self.app.config["UPLOAD_FOLDER_IMAGES"], filename)

                            file.save(file_path)
                            uploads_image = "/static/uploads/images/" + filename
                            
                    try:
                        cursor.execute("UPDATE teacher_profile SET first_name=%s, middle_name=%s, last_name=%s, email_add=%s, profile_pic=%s, phone=%s WHERE teacher_id=%s",
                                    (new_firstname, new_middle, new_lastname, new_email,uploads_image, new_phone, teacher_id))
                                
                        self.mysql.connection.commit()
                        flash("Profile updated successfully!", "success")
                    except Exception as e:
                        flash(f"An error occurred: {str(e)}", "danger")
                        return redirect("/Profile/Teacher")
                    
                    finally:
                        cursor.close()
                    
                    return redirect("/Profile/Teacher")
            else:
                flash("You do not have permission to access this page.", "danger")
                return redirect("/login")  # Redirect to login or another appropriate page
        

        @self.app.route("/delete_profile_image_teacher", methods=["POST"])
        def delete_profile_image_teacher():
            if 'user' in session and session['role'] == "Teacher":
                teacher_id = request.json.get("teacher_id")  # Ensure the student_id is received
                cursor = self.mysql.connection.cursor()

                try:
                    # Get the current profile image from the database
                    cursor.execute("SELECT profile_pic FROM teacher_profile WHERE teacher_id=%s", (teacher_id,))
                    current_image = cursor.fetchone()

                    # Check if the image exists and is the default image
                    if current_image and current_image[0] == "/static/images/Defaul_Image.png":
                        flash("No Image Uploaded.", "danger")
                        return jsonify(success=False), 400  # Respond with error

                    # Optional: Remove the image file from the file system if it's not the default image
                    if current_image and current_image[0] != "/static/images/Defaul_Image.png":
                        image_path = current_image[0].replace("/static", "static")
                        if os.path.exists(image_path):
                            os.remove(image_path)

                    # Update profile_pic field to the default image in the database
                    flash("Image Deleted Successfully.", "success")
                    cursor.execute("UPDATE teacher_profile SET profile_pic='/static/images/Defaul_Image.png' WHERE teacher_id=%s", (teacher_id,))
                    self.mysql.connection.commit()


                    return jsonify(success=True), 200  # Respond with success
                except Exception as e:
                    self.mysql.connection.rollback()  # Rollback in case of error
                    flash("An error occurred while deleting the image.", "danger")
                    return jsonify(success=False, error=str(e)), 500
                finally:
                    cursor.close()

            return jsonify(success=False), 401  # Unauthorized if user is not a student

        #----------Teacher Assignment Route----------
        @self.app.route("/Assignments/Teacher", methods=["POST", "GET"])
        def assignment_teacher():
            if 'user' in session and session['role'] == "Teacher":  
                cursor = self.mysql.connection.cursor()
                teacher_id = session.get('user')
                
                
                cursor.execute("SELECT * FROM teacher_profile WHERE teacher_id=%s", (teacher_id,))
                teacher_records = cursor.fetchall()
                return render_template("Teacher-assignment.html",teacher_records=teacher_records)
            else:
                flash(" Ensure you are signed in.","danger")
                return redirect('/')
    
            
        @self.app.route("/Lesson-Management/Teacher", methods=["POST", "GET"])
        def lesson_manage_teacher():
            if 'user' in session and session['role'] == "Teacher":
                cursor = self.mysql.connection.cursor()
                teacher_id = session.get('user')

                # Uploaded Count Lesson Fetch
                cursor.execute("SELECT COUNT(DISTINCT lesson_group_id) FROM video_lessons WHERE teacher_id = %s", (teacher_id,))
                num_lesson = cursor.fetchone()

                # Uploaded Lesson Fetch
                cursor.execute("""
                    SELECT video_lessons.*,t.first_name, t.last_name
                    FROM video_lessons 
                    JOIN teacher_profile t ON video_lessons.teacher_id = t.teacher_id 
                    WHERE t.teacher_id = %s
                """, (teacher_id,))
                my_uploaded_lessons = cursor.fetchall()

                # Count the total enrollees of the teacher uploaded lessons 
                cursor.execute("""
                    SELECT COUNT(DISTINCT ve.stud_id, vl.lesson_group_id) AS number_of_enrollees
                    FROM video_lesson_enrollments ve
                    JOIN video_lessons vl ON ve.lesson_id = vl.lesson_id
                    WHERE vl.teacher_id = %s;
                """, (teacher_id,))
                total_enrollees = cursor.fetchone()
                
                
                cursor.execute("""
                        SELECT 
                    COUNT(vle.lesson_id) AS total_completed_lessons
                FROM 
                    video_lesson_enrollments AS vle
                JOIN 
                    video_lessons AS vl ON vle.lesson_id = vl.lesson_id
                JOIN 
                    teacher_profile AS tp ON vl.teacher_id = tp.teacher_id
                WHERE 
                    vle.status = 'Completed'
                    AND tp.teacher_id = %s  

                """,(teacher_id,))
                
                completers_count = cursor.fetchone()

                # Fetch teacher records for GET request
                cursor.execute("SELECT * FROM teacher_profile WHERE teacher_id = %s", (teacher_id,))
                teacher_records = cursor.fetchall()

                return render_template("Teacher-manage-lesson.html", teacher_records=teacher_records,
                                    num_lesson=num_lesson, my_uploaded_lessons=my_uploaded_lessons,
                                    total_enrollees=total_enrollees, completers_count=completers_count)

            else:
                flash("Ensure you are signed in.", "danger")
                return redirect('/')

        
        @self.app.route("/Lesson-Management/Upload", methods=["POST"])
        def upload_lesson():
            if 'user' in session and session['role'] == "Teacher":
                cursor = self.mysql.connection.cursor()
                teacher_id = session.get('user')
                department = request.form.get("department")
                category = request.form.get("category")
                title = request.form.get("title")
                description = request.form.get("description")

                # Get the related file type (PDF or Link)
                related_file_type = request.form.get("relatedFileType")
                related_file = request.files.get("relatedFileInput")
                related_link = request.form.get("relatedLinkInput")

                print(teacher_id)
                print(department)
                print(category)
                print(title)
                print(description)

                # Ensure all required inputs are provided
                file = request.files.get("file")
                thumbnail = request.files.get("thumbnail")
                if not title or not description or not file or not thumbnail:
                    flash("Please ensure all fields are filled in, including file uploads.", "danger")
                    return redirect("/Lesson-Management/Teacher")

                # Generate a unique lesson_group_id
                cursor.execute("SELECT MAX(lesson_group_id) FROM video_lessons")
                max_group_id = cursor.fetchone()[0]
                lesson_group_id = max_group_id + 1 if max_group_id else 1

                # Handle video and thumbnail file uploads
                uploads_videos, uploads_thumbnail, status = handle_file_uploads(file, thumbnail)

                # Get the maximum time of the uploaded video using ffprobe
                max_time = get_video_duration(uploads_videos)

                # Handle related files (PDF/Link)
                uploads_pdf, related_link = handle_related_file(related_file_type, related_file, related_link)

                try:
                    cursor.execute("""
                        INSERT INTO video_lessons 
                        (teacher_id, title, filepath, description, department, category, status, lesson_group_id, sequence, thumbnail, max_time, related_files, related_link)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        teacher_id, title, uploads_videos, description, department, category, status, lesson_group_id, 1,
                        uploads_thumbnail, max_time, uploads_pdf, related_link
                    ))

                    self.mysql.connection.commit()
                    flash("New Video Lesson has been successfully added!", "success")

                except Exception as e:
                    flash(f"An error occurred while adding the course: {str(e)}", "danger")

                return redirect("/Lesson-Management/Teacher")

            else:
                flash("Ensure you are signed in.", "danger")
                return redirect('/')


        # Function to handle related files (PDF/Link)
        def handle_related_file(related_file_type, related_file, related_link):
            uploads_pdf = None
            if related_file_type == 'pdf' and related_file and related_file.filename.endswith('.pdf'):
                filename = secure_filename(related_file.filename)
                file_path = os.path.join(self.app.config["UPLOAD_FOLDER_PDF"], filename)
                related_file.save(file_path)
                uploads_pdf = "/static/uploads/pdf/" + filename

            # If it's a link, return the link directly
            if related_file_type == 'link' and related_link:
                return None, related_link

            return uploads_pdf, None


        # Function to handle video and thumbnail file uploads
        def handle_file_uploads(file, thumbnail):
            uploads_videos = uploads_thumbnail = None
            status = "NOT AVAILABLE"

            if file and file.mimetype.startswith('video/'):
                filename = secure_filename(file.filename)
                file_path = os.path.join(self.app.config["UPLOAD_FOLDER_VIDEOS"], filename)
                file.save(file_path)
                uploads_videos = "/static/uploads/videos/" + filename
                status = "AVAILABLE"

            if thumbnail and thumbnail.filename != '':
                thumbnail_filename = secure_filename(thumbnail.filename)
                if thumbnail.mimetype.startswith('image/'):
                    thumbnail_path = os.path.join(self.app.config["UPLOAD_FOLDER_IMAGES"], thumbnail_filename)
                    thumbnail.save(thumbnail_path)
                    uploads_thumbnail = "/static/uploads/images/" + thumbnail_filename

            return uploads_videos, uploads_thumbnail, status

        def get_video_duration(video_path):
            ffprobe_path = "C:/ffmpeg/ffprobe.exe" 

            ffprobe_cmd = [
                    ffprobe_path,  # Use the ffprobe_path variable
                    '-v', 'error',
                    '-select_streams', 'v:0',
                    '-show_entries', 'format=duration',
                    '-of', 'json',
                    os.path.join(self.app.config["UPLOAD_FOLDER_VIDEOS"], video_path.split('/')[-1])  # Get the actual path
                ]

            result = subprocess.run(ffprobe_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            if result.returncode == 0:
                duration_info = json.loads(result.stdout)
                print("FFprobe Output:", duration_info) 
                return float(duration_info['format']['duration'])
            else:
                print("Error retrieving video duration:", result.stderr.decode())
                return None


        @self.app.route("/Update-Lesson/Teacher", methods=["POST", "GET"])
        def update_lesson_teacher():
            if request.method == "POST":
                cursor = self.mysql.connection.cursor()
                teacher_id = session.get('user')
                
                action = request.form.get('action')
                lesson_id = request.form.get('lesson_id')
                lesson_group_id = request.form.get("lesson_group_id")
                
                print(action)
                print(lesson_id)
                print(lesson_group_id)
            
                if action == 'update':
                    new_title = request.form.get("newtitle")
                    new_description = request.form.get("newdescription")
                    
                    file = request.files.get("file")
                    
                    print(new_title)
                    print(new_description)
                    
                    # Fetch the existing title, description, and video file path if new values are not provided
                    if not new_title or not new_description or not file:
                        cursor.execute("SELECT title, description, filepath FROM video_lessons WHERE lesson_id = %s AND lesson_group_id = %s", (lesson_id, lesson_group_id))
                        result = cursor.fetchone()
                        if result:
                            # Use existing values if new ones are not provided
                            if not new_title:
                                new_title = result[0]
                            if not new_description:
                                new_description = result[1]
                            if not file:
                                uploads_videos = result[2]
                    else:
                        # If a new file is provided, save it and update the file path
                        if file and file.mimetype.startswith('video/'):
                            filename = secure_filename(file.filename)
                            file_path = os.path.join(self.app.config["UPLOAD_FOLDER_VIDEOS"], filename)
                            file.save(file_path)
                            uploads_videos = "/static/uploads/videos/" + filename

                    try:
                        # Update lesson in the database
                        cursor.execute(
                            """
                            UPDATE video_lessons
                            SET title = %s, description = %s, filepath = %s
                            WHERE lesson_id = %s AND lesson_group_id = %s
                            """, (new_title, new_description, uploads_videos, lesson_id, lesson_group_id)
                        )

                        self.mysql.connection.commit()
                        flash("Video Lesson has been successfully updated!", "success")
                    except Exception as e:
                        self.mysql.connection.rollback()  # Rollback in case of error
                        flash(f"An error occurred while editing the lesson: {str(e)}", "danger")

                elif action == 'delete':
                    try:
                        # Step 1: Retrieve the file paths from the database
                        cursor.execute("SELECT filepath, related_files FROM video_lessons WHERE lesson_id=%s", (lesson_id,))
                        result = cursor.fetchone()
                        
                        if result:
                            # Main video file path
                            file_path = result[0]  
                            
                            # Related files (assuming it's stored as a comma-separated string)
                            related_files = result[1] if result[1] else ""  
                            related_file_paths = related_files.split(',') if related_files else []

                            # Step 2: Delete the main file from the OS
                            if os.path.exists(file_path):
                                os.remove(file_path)
                            else:
                                print("Main file not found, but lesson deleted from database.", "warning")

                            # Step 3: Delete related files from the OS
                            for related_file in related_file_paths:
                                related_file = related_file.strip()  # Remove any leading/trailing spaces
                                if os.path.exists(related_file):
                                    os.remove(related_file)
                                else:
                                    print(f"Related file {related_file} not found.", "warning")

                            # Step 4: Delete the entry from the database
                            cursor.execute("DELETE FROM video_lessons WHERE lesson_id=%s", (lesson_id,))
                            self.mysql.connection.commit()
                            flash("The lesson and related files have been successfully deleted!", "success")
                        else:
                            flash("Lesson not found in the database.", "danger")

                    except Exception as e:
                        self.mysql.connection.rollback()
                        flash(f"An error occurred while deleting the lesson: {str(e)}", "danger")
            
            # Handle GET request by redirecting to the lesson management page
            return redirect("/Lesson-Management/Teacher")

        @self.app.route("/view_lesson/teacher", methods=["POST", "GET"])
        def view_as_teacher():
            if 'user' in session and session['role'] == "Teacher":
                cursor = self.mysql.connection.cursor()
                teacher_id = session.get('user')
                
                selected_lesson_id = request.form.get('lesson_id')
                lesson_group_id = request.form.get('lesson_group_id')

                print(selected_lesson_id)
                print(lesson_group_id)
                
            
                cursor.execute("SELECT * FROM teacher_profile WHERE teacher_id=%s", (teacher_id,))
                teacher_records = cursor.fetchall()
                
                if request.method == 'POST':
                    cursor.execute(""" 
                            SELECT 
                                vl.*,  
                                t.first_name, 
                                t.last_name
                            FROM 
                                video_lessons vl
                            JOIN 
                                teacher_profile t ON vl.teacher_id = t.teacher_id
                            WHERE 
                                vl.lesson_group_id = %s
                            ORDER BY 
                                vl.sequence ASC
                        """, (lesson_group_id,))
                    group_lessons_data = cursor.fetchall()
                    
                cursor.execute(""" 
                    SELECT 
                        vl.lesson_id, 
                        vl.title, 
                        vl.filepath, 
                        vl.description, 
                        vl.department, 
                        vl.category, 
                        vl.sequence, 
                        t.first_name AS teacher_first_name, 
                        t.last_name AS teacher_last_name, 
                        t.profile_pic
                    FROM 
                        video_lessons vl
                    JOIN 
                        teacher_profile t ON vl.teacher_id = t.teacher_id
                    WHERE 
                        vl.lesson_group_id = %s AND vl.lesson_id = %s
                    GROUP BY 
                        vl.sequence, vl.lesson_id, t.first_name, t.last_name, t.profile_pic
                    ORDER BY 
                        vl.sequence ASC
                """,  (lesson_group_id, selected_lesson_id))
                lessons_data = cursor.fetchall()
                
                cursor.execute("""
                    SELECT  related_files, related_link 
                    FROM video_lessons 
                    WHERE lesson_id = %s
                """, (selected_lesson_id,))
                related_files_vl = cursor.fetchall()
                    
                
            
                # Fetch comments (from both students and teachers)
                cursor.execute(""" 
                    SELECT 
                        comments.comment_text, comments.created_at, 
                        COALESCE(student_profile.firstname, teacher_profile.first_name) AS firstname, 
                        COALESCE(student_profile.lastname, teacher_profile.last_name) AS lastname,
                        COALESCE(student_profile.profile_pic, teacher_profile.profile_pic) AS profile_pic,
                        comments.comment_id, comments.user_id, comments.user_role
                    FROM 
                        comments
                    LEFT JOIN 
                        student_profile ON comments.user_id = student_profile.stud_id AND comments.user_role = 'Student'
                    LEFT JOIN 
                        teacher_profile ON comments.user_id = teacher_profile.teacher_id AND comments.user_role = 'Teacher'
                    WHERE 
                        comments.lesson_id = %s
                    ORDER BY 
                        comments.created_at DESC
                """, (selected_lesson_id,))
                comments = cursor.fetchall()

                cursor.execute("SELECT COUNT(*) FROM comments WHERE lesson_id = %s", (selected_lesson_id,))
                comments_count = cursor.fetchone()
                
                comments_data = []
                for comment in comments:
                    comment_text, created_at, first_name, last_name, profile_pic, comment_id, user_id, user_role = comment
                    time_difference = datetime.now() - created_at
                    # Same time ago logic
                    time_ago = calculate_time_ago(time_difference)
                    comments_data.append((comment_text, time_ago, first_name, last_name, profile_pic, comment_id, user_id, user_role))

                
                return render_template("Teacher-view.html", teacher_records=teacher_records, comments_data=comments_data,
                                    comments_count=comments_count, group_lessons_data=group_lessons_data, lessons_data=lessons_data, comments=comments, related_files_vl= related_files_vl)

        
            flash("An error occurred while retrieving data.", "danger")
            return redirect("/Dashboard-Teacher")


        @self.app.route('/Student-Performance/Teacher',methods=["POST","GET"])
        def teacher_dashboard_studentperformace():
            if 'user' in session and session['role'] == "Teacher":
                cursor = self.mysql.connection.cursor()
                teacher_id = session.get('user')
                
                
                cursor.execute("SELECT * FROM teacher_profile WHERE teacher_id=%s", (teacher_id,))
                teacher_records = cursor.fetchall()
                
                
                my_lesson_enrollees =(""" 
                        SELECT vl.thumbnail, vl.title, 
                        COUNT(vle.enrollment_id) AS total_enrollees
                        FROM video_lessons vl
                        LEFT JOIN video_lesson_enrollments vle ON vl.lesson_id = vle.lesson_id
                        WHERE vl.teacher_id = %s
                        GROUP BY vl.lesson_id;
                    """ )
                
                cursor.execute(my_lesson_enrollees, (teacher_id,))
                myenrollees_perlesson = cursor.fetchall()
    
                
                top_students = ( """
                                SELECT 
                    CONCAT(sp.firstname, ' ', sp.lastname) AS student_name, 
                    sp.profile_pic,
                    COUNT(vle.lesson_id) AS completed_lessons
                FROM 
                    student_profile AS sp
                JOIN 
                    video_lesson_enrollments AS vle ON sp.stud_id = vle.stud_id
                WHERE 
                    vle.status = 'Completed'
                GROUP BY
                    student_name
                ORDER BY 
                    completed_lessons DESC;
                """)
                
                cursor.execute(top_students)
                top_student_viewer = cursor.fetchall()
                
                
                cursor.execute("""
                    SELECT 
                        sp.stud_id, 
                        CONCAT(sp.firstname, ' ', sp.lastname) AS student_name, 
                        sp.profile_pic,
                        SUM(vl.max_time) AS total_duration,
                        COALESCE(SUM(vle.last_watched_time), 0) AS total_last_watched_time,
                        CASE 
                            WHEN SUM(vl.max_time) > 0 THEN 
                                CAST((COALESCE(SUM(vle.last_watched_time), 0) / SUM(vl.max_time)) * 100 AS INT)
                            ELSE 
                                0 
                        END AS overall_completion_percentage
                    FROM 
                        student_profile AS sp
                    JOIN 
                        video_lesson_enrollments AS vle ON sp.stud_id = vle.stud_id
                    JOIN 
                        video_lessons AS vl ON vle.lesson_id = vl.lesson_id
                    WHERE 
                        vl.teacher_id = %s
                    GROUP BY 
                        sp.stud_id;
                """,(teacher_id,))
                
                student_progress = cursor.fetchall()
                        
            
                return render_template('Teacher-studentperformance.html',teacher_records=teacher_records,  myenrollees_perlesson=  myenrollees_perlesson, top_student_viewer= top_student_viewer,student_progress=student_progress)
            else:
                flash(" Ensure you are signed in.","danger")
                return redirect('/teacher-login')
        
        
        @self.app.route('/Help-Center/Teacher',methods=["POST","GET"])
        def teacher_helpcenter():
            if 'user' in session and session['role'] == "Teacher":
                cursor = self.mysql.connection.cursor()
                teacher_id = session.get('user')
                
                
                cursor.execute("SELECT * FROM teacher_profile WHERE teacher_id=%s", (teacher_id,))
                teacher_records = cursor.fetchall()
                return render_template('help-center-teacher.html',teacher_records=teacher_records)
            else:
                flash(" Ensure you are signed in.","danger")
                return redirect('/teacher-login')
            
            
        #----------Teacher Contact----------
        @self.app.route('/Help/Contact/Teacher',methods=["POST","GET"])
        def teacher_contact():
            if 'user' in session and session['role'] == "Teacher":
                cursor = self.mysql.connection.cursor()
                teacher_id = session.get('user')
                
                
                cursor.execute("SELECT * FROM teacher_profile WHERE teacher_id=%s", (teacher_id,))
                teacher_records = cursor.fetchall()
                return render_template('contact-teacher.html',teacher_records=teacher_records)
            else:
                flash(" Ensure you are signed in.","danger")
                return redirect('/teacher-login')

          
        @self.app.route('/Uploaded/Lessons', methods=["POST","GET"])
        def uploaded_lessons_teacher():
            if 'user' in session and session['role'] == 'Teacher':
             
                    cursor = self.mysql.connection.cursor()
                    
                    teacher_id = session.get('user')
                    
                    cursor.execute("SELECT * FROM teacher_profile WHERE teacher_id=%s", (teacher_id,))
                    teacher_records = cursor.fetchall()
                    
                    cursor.execute("SELECT DISTINCT category FROM video_lessons")
                    categories = cursor.fetchall()
                    
                    
                    cursor.execute( """
                                SELECT 
                                    DISTINCT vl.lesson_group_id,
                                    vl.title,
                                    vl.thumbnail,
                                    tp.first_name, 
                                    tp.middle_name, 
                                    tp.last_name,
                                    tp.profile_pic,
                                    vl.lesson_id
                                FROM 
                                    video_lessons vl
                                JOIN 
                                    teacher_profile tp ON vl.teacher_id = tp.teacher_id
                                ORDER BY 
                                    vl.uploaded_time DESC;
                                
                                
                                """)
                    recent_uploads = cursor.fetchall()
                    
                
                    return render_template('Teacher-explore-lessons.html',teacher_records=teacher_records,recent_uploads=recent_uploads,categories=categories )
            else:
                flash(" Ensure you are signed in.","danger")
                return redirect('/login')



        # ----------Admin Login Route----------
        @self.app.route("/admin_login", methods=["POST", "GET"])
        def admin_login():
            if request.method == "POST":
                user_name = request.form.get('user_name')
                password = request.form.get('password')
                cursor = self.mysql.connection.cursor()
                cursor.execute("SELECT * FROM admin_profile WHERE user_name = %s AND password = %s", (user_name, password))
                AdminAcc_found = cursor.fetchone()
                
                if AdminAcc_found:
                    session['user'] = AdminAcc_found[0]  
                    session['role'] = 'Admin'
                    flash("Successfully logged in! ","success")
                    return redirect('/Dashboard-Admin')
                else:   
                    flash("Login failed. Please check your username and password and try again.","danger")
                    return redirect("/")
            else:
                return redirect("/")

        # ----------Admin Signup Route----------
                
        @self.app.route('/admin-signup', methods=["POST", "GET"])
        def admin_signup():
            if request.method == "POST":
                admin_id = request.form.get('admin_id')
                first_name = request.form.get('first_name')
                middle_name = request.form.get('middle_name')
                last_name = request.form.get('last_name')
                user_name = request.form.get('user_name')
                role = request.form.get('role')
                email= request.form.get('email')
                password = request.form.get('password')
                
                
                # default profile
                default_profile = "/static/images/Defaul_Image.png"
                account_status ="Active"

                # Validate names contain only letters
                name_pattern = re.compile(r'^[A-Za-z\s]+$')
                if not (name_pattern.match(first_name) and 
                        name_pattern.match(middle_name) and 
                        name_pattern.match(last_name)):
                    flash("Please enter only letters in the name fields.", "warning")
                    return redirect("/admin-signup")
                
                # Regular expression for ID pattern: 04-2324-xxxxxx
                id_pattern = re.compile(r'^\d{2}-\d{4}-\d{6}$')

                if not id_pattern.match(admin_id):
                    flash("The ID should follow the format 04-2324-xxxxxx.","warning")
                    return redirect("/admin-signup")

                cursor = self.mysql.connection.cursor()

                # Check if the username already exists
                cursor.execute("SELECT * FROM admin_profile WHERE user_name = %s", (user_name,))
                existing_admin = cursor.fetchone()
                if existing_admin:
                    flash("Username already exists. Please choose a different username.", "warning")
                    cursor.close()
                    return redirect("/admin-signup")

                # Check if the admin ID already exists
                cursor.execute("SELECT * FROM admin_profile WHERE admin_id = %s", (admin_id,))
                existing_admin_id = cursor.fetchone()
                if existing_admin_id:
                    flash("This admin ID is already in use. Please choose a different admin ID.", "warning")
                    cursor.close()
                    return redirect("/admin-signup")

                # Insert the new admin into the database
                cursor.execute("INSERT INTO admin_profile (admin_id, first_name, middle_name, last_name, user_name, role, password, profile_pic, email, status) VALUES (%s, %s, %s, %s, %s, %s, %s,%s,%s,%s)",
                                (admin_id, first_name, middle_name, last_name, user_name, role, password,default_profile, email,account_status))
                self.mysql.connection.commit()
                cursor.close()

                flash("You're all set! Your registration was successful!", "success")
                return redirect('/admin_login')
            else:
                return render_template('admin_signup.html')
        
        # ----------Admin Profile Route----------
        
        @self.app.route("/Profile-Admin", methods=["POST", "GET"])
        def profile_admin():
            if 'user' in session and session['role'] == 'Admin':
                user_name = session.get('user_name', 'Not Provided')
                password = session.get('password', 'Not Provided')
                
                cursor = self.mysql.connection.cursor()
                admin_id = session.get('user') 
                
                
               
                cursor.execute("SELECT * FROM admin_profile WHERE admin_id = %s",  (admin_id,))
                admin_records = cursor.fetchall()
                
                

                cursor.close()  # Close the cursor

                return render_template("Admin-profile.html",admin_records=admin_records )
            else:
                flash(" Ensure you are signed in.","danger")
                return redirect('/admin_login')

        # ----------Admin Profile Update Route----------
        
        @self.app.route("/updateAdmin_profile", methods=["POST", "GET"])
        def updateAdmin_profile():
            if "user" in session and session["role"] == "Admin":
                if request.method == "POST":
                    cursor = self.mysql.connection.cursor()
                    admin_id = session.get('user')  # Get admin ID from session
                
                    
                    # Step 1: Get existing image
                    cursor.execute("SELECT profile_pic FROM admin_profile WHERE admin_id=%s",(admin_id,)) 
                    existing_image = cursor.fetchone()
                    existing_image_path = existing_image[0] if existing_image else None  # Extract path if exists

                    # Step 2: Get form values
                    new_firstname = request.form.get("first_name")
                    new_middlename = request.form.get("middle_name")
                    new_lastname = request.form.get("last_name")
                    new_username =request.form.get("user_name")
                    new_email = request.form.get("email")
                    new_phone = request.form.get("phone")

                    
                    uploads_image = existing_image_path 
                    
                    
                    if 'file' in request.files:
                        file = request.files['file']

                        if file.filename:
                            filename = secure_filename(file.filename)
                            file_path = os.path.join(self.app.config["UPLOAD_FOLDER_IMAGES"], filename)

                            
                            # Save the file to the server
                            file.save(file_path)
                            uploads_image = "/static/uploads/images/" + filename
                            
            
                        try:
                            cursor.execute(
                            "UPDATE admin_profile SET first_name=%s, middle_name=%s, last_name=%s, user_name=%s, profile_pic=%s, email=%s, phone_number=%s WHERE admin_id=%s",
                            (new_firstname, new_middlename, new_lastname,new_username, uploads_image, new_email, new_phone, admin_id)
                        )
                            
                            self.mysql.connection.commit()
                            flash("Profile updated successfully!", "success")
                        except Exception as e:
                            flash(f"An error occurred: {str(e)}", "danger")
                            return redirect("/Profile-Admin")
                        
                        finally:
                            cursor.close()

                    return redirect("/Profile-Admin")

            flash("You do not have permission to access this page.", "danger")
            return redirect("/")
        
        @self.app.route("/delete_profile_image_admin", methods=["POST"])
        def delete_profile_image_admin():
            if 'user' in session and session['role'] == "Admin":
                admin_id = request.json.get("admin_id") 
                cursor = self.mysql.connection.cursor()

                try:
                    # Get the current profile image from the database
                    cursor.execute("SELECT profile_pic FROM admin_profile WHERE admin_id=%s", (admin_id,))
                    current_image = cursor.fetchone()

                    # Check if the image exists and is already the default image
                    if current_image and current_image[0] == "/static/images/Defaul_Image.png":
                        flash("No image uploaded.", "danger")
                        return jsonify(success=False), 400  # Respond with error

                    # Optional: Remove the image file from the file system if it's not the default image
                    if current_image and current_image[0] != "/static/images/Defaul_Image.png":
                        image_path = current_image[0].replace("/static", "static")  # Adjust the path to the file system
                        if os.path.exists(image_path):
                            os.remove(image_path)

                    # Update the profile_pic field to the default image in the database
                    cursor.execute("UPDATE admin_profile SET profile_pic='/static/images/Defaul_Image.png' WHERE admin_id=%s", (admin_id,))
                    self.mysql.connection.commit()

                    flash("Image deleted successfully.", "success")
                    return jsonify(success=True), 200  # Respond with success

                except Exception as e:
                    self.mysql.connection.rollback()  # Rollback in case of error
                    flash(f"An error occurred while deleting the image: {str(e)}", "danger")
                    return jsonify(success=False, error=str(e)), 500  # Respond with error

                finally:
                    cursor.close()

            # Unauthorized if the user is not an admin
            return jsonify(success=False), 401

        # ----------Admin Dashboard Route----------

        @self.app.route("/Dashboard-Admin", methods=["POST", "GET"])
        def dashboard_admin():
            if 'user' in session and session['role'] == 'Admin':
                try:
                    cursor = self.mysql.connection.cursor()

                    # Fetch number of students per year level
                    cursor.execute("SELECT year_level, COUNT(*) as student_count FROM student_profile GROUP BY year_level")
                    result = cursor.fetchall()

                    # Handle the result to avoid Undefined issues
                    student_per_year = {row[0] if row[0] else 'Unknown': row[1] if row[1] is not None else 0 for row in result}
                    
                    # Fetch total counts for other entities
                    cursor.execute("SELECT COUNT(*) FROM student_profile")
                    student_count = cursor.fetchone()[0] or 0  # Default to 0 if None

                    cursor.execute("SELECT COUNT(*) FROM teacher_profile")  
                    teacher_count = cursor.fetchone()[0] or 0  # Default to 0 if None
                    
                    # cursor.execute("SELECT COUNT(*) FROM tools")  
                    # tools_count = cursor.fetchone()[0] or 0  # Default to 0 if None

                    cursor.execute("SELECT COUNT(*) FROM video_lessons")
                    lesson_count = cursor.fetchone()[0] or 0  # Default to 0 if None
                                        
                    cursor.execute("""
                        SELECT 
                            v.lesson_id,
                            CONCAT(t.first_name, ' ', t.middle_name, ' ', t.last_name) AS uploader_teacher,
                            v.title, 
                            v.description, 
                            v.department, 
                            v.category, 
                            v.uploaded_time,
                            v.status
                        FROM 
                            video_lessons v
                        JOIN 
                            teacher_profile t ON v.teacher_id = t.teacher_id;
                    """)
                    video_lessons = cursor.fetchall()
                    
                    cursor.execute("SELECT * FROM student_profile")
                    enrolees_list = cursor.fetchall()

                    # Fetch user_name
                    admin_id = session.get('user')
                    # Fetch admin records
                    cursor.execute("SELECT * FROM admin_profile WHERE admin_id = %s",  (admin_id,))
                    admin_records = cursor.fetchall()
                    
                    cursor.close()  


                    # Render the template with data
                    return render_template("Admin-dashboard-2.html",
                                        student_number=student_count,
                                        number_teacher=teacher_count,
                                        number_lessons= lesson_count,
                                        video_lessons=video_lessons,
                                        students_per_year=student_per_year,
                                        admin_records=admin_records,
                                        enrolees_list=enrolees_list 
                                        )

                except Exception as e:
                    print(f"Error retrieving dashboard data: {e}")
                    flash("An error occurred while retrieving data. Please try again later.", "danger")
                    return redirect('/admin_login')
    
                        
            else:
                flash("Ensure you are signed in.", "danger")
                return redirect('/admin_login')

        # ----------Admin ManageStudents Route----------
        @self.app.route("/Manage-Students/Admin", methods=["POST","GET"])
        def managestudents():
            if 'user' in session and session['role'] == "Admin":
                cursor = self.mysql.connection.cursor()
                cursor.execute("SELECT * FROM student_profile")
                students = cursor.fetchall()
                
                # Fetch user_name from the admin_profile table
                admin_id = session.get('user') 
                
                
                # Fetch admin records
                cursor.execute("SELECT * FROM admin_profile WHERE admin_id = %s",  (admin_id,))
                admin_records = cursor.fetchall()
                
                cursor.close()  # Close the cursor

                # Render the template with data
                return render_template('Admin-managestudents.html',students=students, admin_records = admin_records)
            else:
                flash("Ensure you are signed in.", "danger")
                return redirect('/admin-login')
            
        @self.app.route("/addStudent", methods=["POST", "GET"])
        def addStudent():
            if request.method == "POST":
                idi = request.form.get('studentId')
                name = request.form.get('name')
                mname = request.form.get('middlename')
                lname = request.form.get('lastname')
                gmail = request.form.get('email')
                password = request.form.get('password')
                kurso = request.form.get('course')
                gndr = request.form.get('gender')
                yrlvl = request.form.get('yearLevel')
                sction = request.form.get('section')
                    
                # Validate names contain only letters
                name_pattern = re.compile(r'^[A-Za-z\s]+$')
                if not (name_pattern.match(name) and 
                        name_pattern.match(mname) and 
                        name_pattern.match(lname)):
                    flash("Please enter only letters in the name fields.", "warning")
                    return redirect("/signup")
                
                # Regular expression for ID pattern: 04-2324-xxxxxx
                id_pattern = re.compile(r'^\d{2}-\d{4}-\d{6}$')

                if not id_pattern.match(idi):
                    flash("The ID should follow the format 04-2324-xxxxxx.","warning")
                    return redirect("/signup")

                cursor = self.mysql.connection.cursor()
                
                # Check if the teacher is already exists in the database
                cursor.execute("SELECT * FROM student_profile WHERE email = %s AND stud_id = %s" , (gmail, idi))
                existing_teacher = cursor.fetchone()

                if existing_teacher:
                    flash("This data is already exist !", "warning")
                    return redirect("/signup")
                
                #inserting new student data to database
                cursor.execute("INSERT INTO student_profile(stud_id, firstname, middlename, lastname, gender, email, password,course, year_level, section) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                            (idi,name,mname,lname,gndr,gmail,password,kurso,yrlvl,sction))
                self.mysql.connection.commit()
                cursor.close()
                flash("New Student has Successfully Enrolled !","success")
                return redirect("/Manage-Students/Admin")
            else:
                return render_template("signup.html")

        
        @self.app.route("/studentDelete", methods=["POST", "GET"])
        def studentDelete():
            if 'user' in session:
                if request.method == "POST":
                    stud_id = request.form['stud_id']
                    cursor = self.mysql.connection.cursor()
                    cursor.execute("DELETE FROM student_profile WHERE stud_id = %s", (stud_id,))
                    self.mysql.connection.commit()
                    cursor.close()
                    flash("Student records Deleted", 'danger')
                return redirect('/Manage-Students/Admin')
            else:
                flash("Unauthorized Access Detected! Redirecting...", "danger")
                return redirect("/")

        @self.app.route("/studentUpdate_process", methods=["POST","GET"])
        def studentUpdate_Process():
            if 'user' in session:
                if request.method == "POST":
                    stud_id = request.form.get("stud_id")
                    new_name = request.form.get("new_name")
                    new_middlename = request.form.get("new_middlename")
                    new_lastname = request.form.get("new_lastname")
                    new_gender = request.form.get("new_gender")
                    new_email = request.form.get("new_email")
                    new_password = request.form.get("new_password")
                    new_new_coursename = request.form.get("new_course")
                    new_yearLevel = request.form.get("new_yearLevel")
                    new_section = request.form.get("new_section")
                    
            
                    # Updating of Student goes here
                    cursor = self.mysql.connection.cursor()
                    
                    cursor.execute("UPDATE student_profile SET firstname=%s, middlename=%s, lastname=%s, gender=%s, email=%s, password=%s, course=%s, year_level=%s,section=%s WHERE stud_id=%s",
                                    (new_name, new_middlename, new_lastname, new_gender, new_email, new_password,new_new_coursename,new_yearLevel,new_section, stud_id))
                    flash("Data Updated Successfully!", "success")
                    self.mysql.connection.commit()
                    cursor.close()
                return redirect('/Manage-Students/Admin')
        
        
        # ----------Admin ManageFaculty Route----------

        @self.app.route("/Manage-faculty/Admin", methods=["POST","GET"])
        def managefaculty():
            if 'user' in session and session['role'] == "Admin":
                cursor = self.mysql.connection.cursor()
                cursor.execute("SELECT * FROM teacher_profile")
                teachers = cursor.fetchall()
                

                # Fetch user_name from the admin_profile table
                admin_id = session.get('user') 
                
                # Fetch admin records
                cursor.execute("SELECT * FROM admin_profile WHERE admin_id = %s",  (admin_id,))
                admin_records = cursor.fetchall()
                
                cursor.close()  # Close the cursor

                return render_template('Admin-managefaculty.html',teacher=teachers, admin_records=admin_records)
            
            else:
                flash(" Ensure you are signed in.","danger")
                return redirect('/admin-login')
            
        # ----------Admin ManageFaculty Route----------
        
        @self.app.route('/addTeacher', methods=["POST", "GET"])
        def addTeacher():
            if request.method == "POST":
                teacher_id = request.form.get('teacher_id')
                first_name = request.form.get("first_name")
                middle_name = request.form.get("middle_name")
                last_name = request.form.get("last_name")
                email_add = request.form.get("email_add")
                password = request.form.get("password")
                department = request.form.get("department")


                # Validate names contain only letters
                name_pattern = re.compile(r'^[A-Za-z\s]+$')
                if not (name_pattern.match(first_name) and 
                        name_pattern.match(middle_name) and 
                        name_pattern.match(last_name)):
                    flash("Please enter only letters in the name fields.", "warning")
                    return redirect("/Manage-faculty/Admin")
                
                # Regular expression for ID pattern: 04-2324-xxxxxx
                id_pattern = re.compile(r'^\d{2}-\d{4}-\d{6}$')

                if not id_pattern.match(teacher_id):
                    flash("The ID should follow the format 04-2324-xxxxxx.","warning")
                    return redirect("/Manage-faculty/Admin")


                cursor = self.mysql.connection.cursor()

                # Check if the teacher is already exists in the database
                cursor.execute("SELECT * FROM teacher_profile WHERE email_add = %s AND teacher_id = %s" , (email_add, teacher_id))
                existing_teacher = cursor.fetchone()

                if existing_teacher:
                    flash("This data is already exist !", "warning")
                    return redirect("/Manage-faculty/Admin")
                
                # Inserting new teacher data into the database
                cursor.execute("INSERT INTO teacher_profile (teacher_id, first_name, middle_name, last_name, email_add, password, department) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                            (teacher_id, first_name, middle_name, last_name, email_add, password, department))
                self.mysql.connection.commit()
                cursor.close()
                flash("New teacher added successfully!", "success")
                return redirect('/Manage-faculty/Admin')
            else:
                return render_template("Admin-managefaculty.html")
            
        # ----------Admin UpdateFaculty Route----------    
        
        @self.app.route("/teacherDelete", methods=["POST", "GET"])
        def teacherDelete():
            if 'user' in session:
                if request.method == "POST":
                    teacher_id = request.form.get("teacher_id")
                    cursor = self.mysql.connection.cursor()
                    cursor.execute("DELETE FROM teacher_profile WHERE teacher_id = %s", (teacher_id,))
                    self.mysql.connection.commit()
                    flash("Teacher records Deleted!", 'danger')
                return redirect("/Manage-faculty/Admin")
            else:
                flash("Unauthorized Access Detected! Redirecting...", "danger")
                return redirect("/")
        
        # ----------Admin UpdateProcessFaculty Route----------    
        @self.app.route("/teacherUpdate_process", methods=["POST", "GET"])
        def teacherUpdate_Process():
            if 'user' in session:
                if request.method == "POST":
                    new_firstname = request.form.get("new_firstname")
                    new_middlename = request.form.get("new_middlename")
                    new_lastname = request.form.get("new_lastname")
                    new_email = request.form.get("new_emailadd")
                    password = request.form.get("password")
                    new_department = request.form.get("new_department")
                    new_teacherid = request.form.get('new_teacherid')
                    


                    # Update teacher information in the database
                    cursor = self.mysql.connection.cursor()
                    cursor.execute("UPDATE teacher_profile SET first_name=%s, middle_name=%s, last_name=%s, email_add=%s, password=%s, department=%s WHERE teacher_id=%s",
                                (new_firstname, new_middlename, new_lastname, new_email,password, new_department, new_teacherid))
                    
                    flash("Data Updated Successfully!", "success")
                    self.mysql.connection.commit()
                    cursor.close()
                return redirect('/Manage-faculty/Admin')
            else:
                flash("You need to log in first", "error")
                return redirect('/login')

        
        # ----------Admin CourseManagement Route----------
        
        @self.app.route("/Lesson-Management/Admin", methods=["POST","GET"])
        def managelesson_admin():
            if "user" in session and session["role"] == "Admin":
                
                cursor = self.mysql.connection.cursor()
                
                #Fetch teacher records
                cursor.execute("SELECT * FROM teacher_profile")
                teacher_list = cursor.fetchall()
                
                admin_id = session.get('user') 
                
                # Fetch admin records
                cursor.execute("SELECT * FROM admin_profile WHERE admin_id = %s",  (admin_id,))
                admin_records = cursor.fetchall()
                
                
                cursor.execute("""
                    SELECT 
                        v.lesson_id,
                        CONCAT(t.first_name, ' ', t.middle_name, ' ', t.last_name) AS uploader_teacher,
                        v.title, 
                        v.description, 
                        v.department, 
                        v.category, 
                        v.uploaded_time,
                        v.status
                    FROM 
                        video_lessons v
                    JOIN 
                        teacher_profile t ON v.teacher_id = t.teacher_id;
                """)
                video_lessons  = cursor.fetchall()
                
    

                
                return render_template('Admin-managecourse.html',video_lessons=video_lessons ,admin_records=admin_records,teacher_list=teacher_list)
            else:
                flash(" Ensure you are signed in.","danger")
                return redirect('/admin-login')
                    
        @self.app.route("/adminCourse_Upload", methods=["POST", "GET"])
        def adminCourse_upload():
            if "user" in session and session["role"] == "Admin":
                cursor = self.mysql.connection.cursor()

                if request.method == "POST":
                    teacher_id = request.form.get("teacher_id")
                    course_name = request.form.get("course_name")
                    department = request.form.get("department")
                    category = request.form.get("category")
                    titles = request.form.getlist("title[]")
                    descriptions = request.form.getlist("description[]")
                    sequence = request.form.getlist("sequence[]")

                    # Generate a unique lesson_group_id to group the videos together
                    cursor.execute("SELECT MAX(lesson_group_id) FROM video_lessons")
                    max_group_id = cursor.fetchone()[0]
                    lesson_group_id = max_group_id + 1 if max_group_id else 1

                    # Handling multiple file uploads
                    files = request.files.getlist("file[]")
                    thumbnails = request.files.getlist("thumbnail[]")  # Expecting a list of thumbnails

                    if len(files) != len(titles) or len(titles) != len(descriptions) or len(files) != len(thumbnails):
                        flash("Mismatch in the number of files, titles, descriptions, and thumbnails.", "danger")
                        return redirect("/Lesson-Management/Admin")

                    for i in range(len(files)):
                        file = files[i]
                        title = titles[i]
                        description = descriptions[i]
                        thumbnail = thumbnails[i] if thumbnails else None

                        # Handle video file upload
                        if file and file.filename != '':
                            filename = secure_filename(file.filename)

                            if file.mimetype.startswith('video/'):
                                file_path = os.path.join(self.app.config["UPLOAD_FOLDER_VIDEOS"], filename)
                                file.save(file_path)

                                uploads_videos = "/static/videos/" + filename
                                status = "AVAILABLE"
                            else:
                                uploads_videos = None
                                status = "NOT AVAILABLE"
                        
                        # Handle thumbnail image upload
                        if thumbnail and thumbnail.filename != '':
                            thumbnail_filename = secure_filename(thumbnail.filename)

                            if thumbnail.mimetype.startswith('image/'):
                                thumbnail_path = os.path.join(self.app.config["UPLOAD_FOLDER_IMAGES"], thumbnail_filename)
                                thumbnail.save(thumbnail_path)

                                uploads_thumbnail = "/static/uploads/images/" + thumbnail_filename
                            else:
                                uploads_thumbnail = None
                        else:
                            uploads_thumbnail = None  # Set to None if no thumbnail is uploaded

                        try:
                            cursor.execute("""
                                INSERT INTO video_lessons 
                                (lesson_name, teacher_id, title, filepath, description, department, category, status, lesson_group_id, sequence, thumbnail)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """, (course_name, teacher_id, title, uploads_videos, description, department, category, status, lesson_group_id, sequence[i], uploads_thumbnail))

                            self.mysql.connection.commit()

                        except Exception as e:
                            flash(f"An error occurred while adding the course: {str(e)}", "danger")
                            return redirect("/Lesson-Management/Admin")

                    flash("New Video Lesson(s) have been successfully added!", "success")
                    return redirect("/Lesson-Management/Admin")

            else:
                flash("You do not have permission to access this page.", "danger")
                return redirect("/login")
    
        #----------Admin Support & Inquiries Route---------      
        @self.app.route("/Support-Inquiries/Admin", methods=["POST","GET"])
        def supportInquiries_admin():
            if "user" in session and session["role"] == "Admin":
                cursor = self.mysql.connection.cursor()
    
                # Fetch user_name from the admin_profile table
                admin_id = session.get('user') 
                
                # Fetch admin records
                cursor.execute("SELECT * FROM admin_profile WHERE admin_id = %s",  (admin_id,))
                admin_records = cursor.fetchall()


                cursor.close()  # Close the cursor

                
                return render_template('Admin-supportInquiries.html', admin_records =admin_records)
            else:
                flash(" Ensure you are signed in.","danger")
                return redirect('/admin-login')
            

        @self.app.route('/admin_change/password', methods=["POST", "GET"])
        def changepass_admin():
            if 'user' in session and session["role"] == "Admin":
                # Get the form data
                current_password = request.form.get('password')
                new_password = request.form.get('newpassword')
                re_new_password = request.form.get('renewpassword')

                admin_id = session['user']  # Get the admin ID from the session
                cursor = self.mysql.connection.cursor()
                
                # Fetch the stored plain text password from the database
                cursor.execute("SELECT password FROM admin_profile WHERE admin_id = %s", (admin_id,))
                result = cursor.fetchone()
                
                if result:
                    stored_password = result[0]
                    # Check if the current password matches the stored password
                    if stored_password == current_password:
                        if new_password == re_new_password:
                            # Directly update the new password in the database
                            cursor.execute("UPDATE admin_profile SET password = %s WHERE admin_id = %s", (new_password, admin_id))
                            self.mysql.connection.commit()
                            flash("Password changed successfully", "success")
                        else:
                            flash("New passwords do not match", "danger")
                    else:
                        flash("Current password is incorrect", "danger")
                else:
                    flash("Admin not found", "danger")

                cursor.close()
                return redirect('/Profile-Admin')
            
            return redirect('/')
        
        
    
        # ----------HomePage Courses Route----------     
        @self.app.route('/courses', methods=["POST", "GET"])
        def courses():
            cursor = self.mysql.connection.cursor()
            cursor.execute("SELECT * FROM video_lessons")
            courses = cursor.fetchall()
            return render_template('courses.html', show=courses)
        

        # ----------HomePage About Us Route----------   
        @self.app.route('/aboutus', methods=["POST", "GET"])
        def aboutus():
            return render_template('aboutus.html')
        
        # ----------HomePage Blogs Route----------
        @self.app.route('/PhinmaEduHub/Blogs', methods=["POST", "GET"])
        def Blogs():
            return "<h1>file not created <h1>"
        
        # ----------HomePage Contact Route----------
        
        @self.app.route('/contact', methods=["POST", "GET"])
        def contact():
            return render_template('contact.html')
        

        # ----------Logout Process Route----------
        
        @self.app.route('/logout', methods=["POST","GET"])
        def logout():
            session.clear()
            flash("You have been logged out.", "danger")
            return redirect('/')
    
            
    def run(self):
        self.app.run(host='0.0.0.0', port=5000, debug=True)


study_system = StudySystem(__name__)
study_system.define_routes()
study_system.run()
