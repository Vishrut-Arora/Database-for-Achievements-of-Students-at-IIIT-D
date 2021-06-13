from app import app, db
from flask import (
    Flask,
    render_template, 
    url_for, 
    redirect, 
    flash, 
    get_flashed_messages, 
    request,
    session
)
from datetime import datetime
import forms
from modules.db import connect_to_db
from datetime import datetime
import traceback

# user = None

@app.route('/')
@app.route('/index', methods=['GET', ])
def index():
    name = "Sudeeep"
    return render_template('base.html', name=name)


@app.route('/login', methods = ['GET', 'POST'])
def login():
    form = dict(request.form)
    if form:
        designation = form.get('designation')
        email = form.get('email')
        if designation and designation not in [
            "Professor",
            "Student",
            "Recruiter",
            "Parent"
        ]:
            cur = connect_to_db()
            cur.execute(f"""
                select *
                from "User"
                where "Designation" = '{designation}'
            """)
            session['user']={}
            temp = cur.fetchall()[0]
            session["user"]["Name"] = temp[0]
            session["user"]["Age"] = temp[1]
            session["user"]["EmailID"] = temp[2]
            session["user"]["Gender"] = temp[3]
            session["user"]["Designation"] = temp[4]
            session["user"]["Password"] = temp[5]
            session["user"]["LastLogin"] = temp[6]
            session["user"]["Admin"] = temp[7]
            session["user"]["Contact"] = temp[8]
            cur.close()
            return render_template('login.html', user = session['user'])
        
        elif designation: # user email fetch
            cur = connect_to_db()
            try:
                cur.execute(f"""
                    select "EmailID"
                    from "User"
                    where "Designation" = '{designation}'
                """)
                email = [i[0] for i in cur.fetchall()]
            except:
                traceback.print_exc()
            cur.close()
            return render_template('login.html', emails = email)
        elif email:
            cur = connect_to_db()
            try:
                cur.execute(f"""
                    select *
                    from "User"
                    where "EmailID" = '{email}'
                """)
                session['user'] = {}
                temp = cur.fetchall()[0]
                session['user']["Name"] = temp[0]
                session['user']["Age"] = temp[1]
                session['user']["EmailID"] = temp[2]
                session['user']["Gender"] = temp[3]
                session['user']["Designation"] = temp[4]
                session['user']["Password"] = temp[5]
                session['user']["LastLogin"] = temp[6]
                session['user']["Admin"] = temp[7]
                session['user']["Contact"] = temp[8]
                
            except:
                traceback.print_exc()
            cur.close()
            return render_template('login.html', user = session['user'])
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    print("start")
    form = forms.AddUserForm()
    print(request.form)
    # print(request.json.get('na
    # me'))
    for i in request.form:
        print(request.form[i])
    print(request.method)
    try:
        name = request.form['name']
        cur = connect_to_db()
        print("befor")

        cur.execute(f"""
            create user "{name}_{request.form['designation']}" with password '{name}';
            Grant all on "User" to "{name}_{request.form['designation']}";
            INSERT INTO "User" ("Name","Age","EmailID","Gender","Designation","Password","LastLogin","Admin","Contact") 
            VALUES ('{name}', {request.form['age']} ,'{request.form['email']}', {request.form['gender']}, {request.form['designation']}, {request.form['password']}, '{datetime.now()}', false, {request.form['phone']});
        """)
        print("after")
        cur.close()
        return redirect(url_for('index'))
    except Exception as e:
        print(e)
        name = "Sudeep"
    return render_template('signup.html', form=form, name=name)

@app.route('/logout')
def logout():
    return redirect(url_for('login'))

@app.route('/student',methods=['GET', 'POST'])
def student():
    print("session: ",session)
    gpa=0
    rollno=0
    CurrBio=''
    CuuSkills=''
    myProjects = ""
    myEducation = ""
    eligibleCompanies = ""
    result=request.form
    print("Result", result)
    try:
        print("start")
        cur=connect_to_db()
        cur.execute(f""" 
                    Select  "RollNo" from "Student" where "UserId" = '{session['user']['EmailID']}';
                """)
        rollno=cur.fetchall()
        rollno=rollno[0][0]
        print(rollno)
        cur.execute(f"""
        Select  "Bio" from "Student" where "RollNo" = {rollno};
        """)
        CurrBio=cur.fetchall()
        CurrBio=CurrBio[0][0]
        cur.execute(f""" 
                Select  "GPA" from "Student" where "UserId" = '{session['user']['EmailID']}';
            """)
        gpa=cur.fetchall()
        gpa=gpa[0][0]
        cur.execute(f"""
        Select "Title" from "Skill" where "StudentId"={rollno}
        """)
        skills=cur.fetchall()
        cur.execute(f"""
        select "Title" from "Achievement" where "StudentId"={rollno};
        """)
        achievement=cur.fetchall()

        cur.execute(f""" SELECT * FROM "Project"
                WHERE "ProjectId" IN(
                SELECT "ProjectId" FROM "Indulged"
                WHERE "StudentId" = {rollno}
                );
            """)
        myProjects = cur.fetchall()

        cur.execute(f""" SELECT * FROM "Education"
                WHERE "EducationId" IN(
                SELECT "EducationId" FROM "Attended_Student"
                WHERE "StudentId" = {rollno})
            """)
        myEducation = cur.fetchall()

        cur.execute(f""" SELECT * FROM "Recruiter"
                WHERE "EligibleGPA" >= (
                SELECT "GPA" FROM "Student"
                WHERE "RollNo" = {rollno}
                )
            """)

        eligibleCompanies = cur.fetchall()
        
        cur.close()
    except Exception as E:
        print(E)
    ###BIO
    if('UpdateBio' in result):
        try:
            cur=connect_to_db()
            cur.execute(f""" 
                Update "Student" set "Bio"='{result['bio']}' where "RollNo"={rollno};
            """)
            CurrBio=result['bio']
            cur.close()
        except Exception as e:
            print(e)
    if('AddSkill' in result):
        try:
            cur=connect_to_db()
            cur.execute(f""" 
                Insert into "Skill" values ({rollno}, '{result["title"]}', '{result['url']}');
            """)
            cur.close()
        except Exception as e:
            print(e)
    if('AddAch' in result):
        print(result)
        try:
            cur=connect_to_db()
            x=False
            if(result['type']=='tech'):
                x=True
            cur.execute(f""" 
                Insert into "Achievement" values ({rollno}, '{result['title']}', '{x}', '{result['proof']}', '{result['institute']}');
            """)
            cur.close()
        except Exception as e:
            print(e)
    if('addEducation' in result):
        try:
            cur=connect_to_db()
            cur.execute(f""" 
                Insert into "Attended_Student" ("EducationId", "StudentId") values ('{result['educationId']}', '{rollno}');
            """)
            cur.close()
        except Exception as e:
            print(e)
    
    return render_template('student.html',gpa=gpa,bio=CurrBio,skills=skills,Achivements=achievement, myProjects = myProjects, myEducation = myEducation, eligibleCompanies = eligibleCompanies)

@app.route('/parent',methods=['GET', 'POST'])
def parent():
    result=request.form
    x=""
    try:
        print(session)
        cur=connect_to_db()
        cur.execute(f""" 
            select * from "Achievement"
            where "StudentId" in (
            Select "RollNo" from "Student"
	        where "ParentId"='{session['user']['EmailID']}'
        );
        """)
        x=cur.fetchall()
        cur.close()
    except Exception as e:
        print(e)
    return render_template('parents.html',achievements=x, user = session['user'])

@app.route('/professor', methods=['GET', 'POST'])
def professor():
    result = request.form
    mentor=""
    employeeId = ""
    studentWorkingProjects=""
    projectsUnderStudents=""
    professorEducation = ""
    studentGPA=""
    allEducations = ""


    try:
        cur=connect_to_db()

        cur.execute(f""" select "EmployeeId" from "Professor"
                where "UserId" = '{session['user']['EmailID']}'
                 """)
        employeeId = cur.fetchall()[0][0]
        print("employeeID : ", employeeId)

        cur.execute(f""" select * from "Education" """)

        allEducations = cur.fetchall()

        cur.execute(f""" select * from "Education" 
                where "EducationId" in (
                    select "EducationId" from "Attended_Professor"
                    where "ProfessorId" = '{employeeId}'
                )
                """)
        professorEducation = cur.fetchall()
        cur.close()

    except Exception as e:
        print(e)

    if('assignStudent' in result):
        try:
            cur=connect_to_db()
            cur.execute(f""" Insert into "Indulged" ("ProjectId", "StudentId") values ({result['projectID']},{result['rollno']})""")
            cur.close()
        except Exception as e:
            print(e)
    if("project_underStudent" in result):
        print(" inproject_underStudent")
        print(result)
        if(result['rollnoGPA'] != ''):
            try:
                cur = connect_to_db()
                cur.execute(
                    f"""Select  "GPA" from "Student" where "RollNo" = {result['rollnoGPA']};""")
                studentGPA=cur.fetchall()
                # print(cur.fetchall())
                cur.close()
            except Exception as e:
                print(e)
        
        if(result['rollnoPID'] != ''):
            try:
                cur = connect_to_db()
                cur.execute(f"""select * from "Project" 
                    where "ProjectId" in(
                    Select "ProjectId" from "Indulged"
                    Where "StudentId"= {result['rollnoPID']} 
                    );
                """)
                studentWorkingProjects=cur.fetchall()
                
                cur.close()
            except Exception as e:
                print(e)
        try:
            cur = connect_to_db()
            if(result['projectID'] != ''):
                cur.execute(f"""
            select * from "Student"
                Where "RollNo" in (
            Select "StudentId" from "Indulged"
	            Where "ProjectId"={result['projectID']}
                );
                """)
            projectsUnderStudents=cur.fetchall()
            cur.close()
        except Exception as e:
            print(e)
    ##########################Mentor Stuff##################
    if("mentors-submits" in result):
        print("in mentors-submits")
        print(result)
        try:
            cur = connect_to_db()
            print("befor")
            cur.execute(f"""
            Select * from "Professor"
            Where "EmployeeId" In (
            Select "MentorId" from "Project"
	            where "ProjectId"={result['Mentor-Project']}
            );
            """)
            mentor=cur.fetchall()
            print(cur.fetchall())
            print("after")
            cur.close()
        except Exception as e:
            print(e)
    ################################# education related quesries####################
    if("education-submit" in result):
        print("in education-submit")
        print(result)
        educationID = result["educationID"]
        professorID = session['user']["EmailID"]
        if(result["operation"] == "Insert"):
            try:
                cur = connect_to_db()
                cur.execute(f"""
                INSERT INTO "Attended_Professor" ("EducationId","ProfessorId") VALUES ({educationID},{professorID})
                """)

                cur.close()
            except Exception as e:
                print(e)
        if(result["operation"] == "Update"):
            try:
                cur = connect_to_db()
                cur.execute(f"""
                UPDATE "Attended_Professor" 
                SET "EducationId"={educationID}
                Where "ProfessorId"={professorID}

                """)

                cur.close()
            except Exception as e:
                print(e)
        if(result["operation"] == "Delete"):
            try:
                cur = connect_to_db()
                cur.execute(f"""
                Delete from "Attended_Professor" 
                Where "ProfessorId" ={professorID} and "EducationId"={educationID};

                """)

                cur.close()
            except Exception as e:
                print(e)
    ######################################### Adding projects####################################
    if("addProject-submit" in result):
        print("in addProject-submit")
        print(result)
        try:
            cur = connect_to_db()
            print("befor")

            cur.execute(f"""
            INSERT INTO "Project" ("ProjectId","Title","MentorId","Duration","StartDate","EndDate","Field","Domain") VALUES 
	        ({result['AprojectID']},'{result['Title']}',{session['user']["EmailID"]},'{result['Duration']}','{result['StartDate']}',null,'{result['Field']}','{result['Domain']}')
            """)
            cur.execute("""Select * from "Project" """)
            print(cur.fetchall())
            print("after")
            cur.close()
        except Exception as e:
            print(e)
    return render_template('professor.html',mentor=mentor,studentGPA=studentGPA,projectsUnderStudents=projectsUnderStudents,studentWorkingProjects=studentWorkingProjects, professorEducation = professorEducation, allEducations = allEducations)




######################################################################################
#                                  SPORTS AND CULTURAL
######################################################################################
@app.route('/Sports_Cultural',methods= ['GET', 'POST'])
def Sports_Cultural_Queries():
    achievementDetails = ""
    option=0
    # form=forms.AddUserForm()
    result=request.form
    roll_calls=""
    roll_institution=""
    roll_title=""
####################
    try:
        cur = connect_to_db()
        cur.execute(f"""
            create role Sports_Cultural_role;
            create view Sports_Cultural_view as select * from "Achievement";
            grant select on Sports_Cultural_view to Sports_Cultural_role;
            grant update,select on Achievement to Sports_Cultural_role;
            set role Sports_Cultural_role;
        """)
        roll_calls = cur.fetchall()
        print(roll_calls)
        for aa in range(len(roll_calls)):
            str1=roll_calls[aa][0]
            roll_calls[aa]=str1
            print(str1)
        print(cur.fetchall())
        print("after")
        cur.close()

    except Exception as e:
        print(e)
####################


    try:
        cur = connect_to_db()
        cur.execute(f"""
            Select "StudentId" from "Achievement" Where "Technical"=false;
        """)
        roll_calls = cur.fetchall()
        print(roll_calls)
        for aa in range(len(roll_calls)):
            str1=roll_calls[aa][0]
            roll_calls[aa]=str1
            print(str1)
        print(cur.fetchall())
        print("after")
        cur.close()

    except Exception as e:
        print(e) 

    try:
        cur = connect_to_db()
        cur.execute(f"""
        Select "Institution" from "Achievement" Where "Technical"=false ;
        """)
        roll_institution = cur.fetchall()
        print(roll_institution)
        for aa in range(len(roll_institution)):
            str1=roll_institution[aa][0]
            roll_institution[aa]=str1
            print(str1)
        print(cur.fetchall())
        print("after")
        cur.close()

    except Exception as e:
        print(e) 

    try:
        cur = connect_to_db()
        cur.execute(f"""
            Select "Title" from "Achievement" Where "Technical"=false ;
        """)
        roll_title = cur.fetchall()
        print(roll_title)
        for aa in range(len(roll_title)):
            str1=roll_title[aa][0]
            roll_title[aa]=str1
            print(str1)
        print(cur.fetchall())
        print("after")
        cur.close()

    except Exception as e:
        print(e)

    if("Achievement-submit" in result):
        print("in Achievement-submit")
        print(result)
        print("ohh acha")
        studentID=result["studentID"]
        title=result["title"]
        proof=result["proof"]
#################################################################################
## UPDATE SPORTS ACHIEVEMENTS 
#################################################################################
        if(result["operation"]=="Update"):
          
            if(studentID=="RollNo"):
                if(title!="Title" and proof!="Verification"):
                    try:
                        cur = connect_to_db()
                        cur.execute(f"""
                            UPDATE "Achievement"  
                            SET "Proof"='{proof}'
                            Where "Title" LIKE '%{title}%' AND "Technical"=false;

                        """)
                        print(cur.fetchall())
                        cur.close()
                    except Exception as e:
                        print(e)
            else:
                if(title=="Title"):
                    if(proof!="Verification"):
                        try:
                            cur = connect_to_db()
                            cur.execute(f"""
                            UPDATE "Achievement"  
                            SET "Proof"='{proof}'
                            Where "StudentId"={studentID} AND "Technical"=false;
                            """)
                            print(cur.fetchall())
                           # print("Hello1", cur.fetchall())     
                            cur.close()
                        except Exception as e:
                            print(e)
                else:
                    if(proof=="Verification"):
                        try:
                            cur = connect_to_db()
                            cur.execute(f"""
                            UPDATE "Achievement"  
                            SET "Title"='{title}'
                            Where "StudentId"={studentID} AND "Technical"=false;

                            """)
                            print(cur.fetchall())
                            cur.close()
                        except Exception as e:
                            print(e)
                    else:
                        try:
                            cur = connect_to_db()
                            cur.execute(f"""
                            UPDATE "Achievement"  
                            SET "Proof"='{proof}'
                            Where "StudentId"={studentID} AND "Title" LIKE '%{title}%' AND "Technical"=false;
                            """)
                            print("Pakode")
                            print(cur.fetchall())
                           # print("Hello2", cur.fetchall())
                            cur.close()
                        except Exception as e:
                            print(e)

# ################################################################################
# Delete Sports and Achievements
# ################################################################################
        if(result["operation"]=="Delete"):    
            if(studentID=="RollNo"):
                if(title!="Title" and proof!="Verification"):
                    try:
                        cur = connect_to_db()
                        cur.execute(f"""
                            Delete from "Achievement"
                            Where "Proof" LIKE '%{proof}%' AND "Title" LIKE '%{title}%' AND "Technical"=false;
                        """)
                        print("Pakoda2")
                        print(cur.fetchall())
                        cur.close()
                    except Exception as e:
                        print(e)

                elif(title!="Title"):
                    try:
                        cur = connect_to_db()
                        cur.execute(f"""
                            Delete from "Achievement" 
                            Where "Title" LIKE '%{title}%' AND "Technical"=false;
                        """)
                        print(cur.fetchall())
                        cur.close()
                    except Exception as e:
                        print(e)
                elif(proof!="Verification"):
                    try:
                        cur = connect_to_db()
                        cur.execute(f"""
                            Delete from "Achievement" 
                            Where "Proof" LIKE '%{proof}%' AND "Technical"=false;
                        """)
                        print(cur.fetchall())
                        cur.close()
                    except Exception as e:
                        print(e)
            else:
                if(title=="Title"):
                    if(proof!="Verification"):
                        try:
                            cur = connect_to_db()
                            cur.execute(f"""
                            Delete from "Achievement" 
                            Where "Proof" LIKE '%{proof}%' AND "StudentId"={studentID} AND "Technical"=false;

                            """)
                            print(cur.fetchall())
                            cur.close()
                        except Exception as e:
                            print(e)
                    else:
                        try:
                            cur = connect_to_db()
                            cur.execute(f"""
                            Delete from "Achievement" 
                            Where "StudentId"={studentID} AND "Technical"=false;

                            """)
                            print(cur.fetchall())
                            cur.close()
                        except Exception as e:
                            print(e)

                else:
                    if(proof=="Verification"):
                        try:
                            cur = connect_to_db()
                            cur.execute(f"""
                            Delete from "Achievement" 
                            Where "Title" LIKE '%{title}%' AND "StudentId"={studentID} AND "Technical"=false;

                            """)
                            print(cur.fetchall())
                            cur.close()
                        except Exception as e:
                            print(e)
                    else:
                        try:
                            cur = connect_to_db()
                            cur.execute(f"""
                            Delete from "Achievement"  
                            Where "Proof" LIKE '%{proof}%' AND "StudentId"={studentID} AND "Title" LIKE '%{title}%' AND "Technical"=false;
                            """)
                            print("Pakoda3")
                            print(cur.fetchall())
                            cur.close()
                        except Exception as e:
                            print(e)            
##################################################################################

    if("Search-submit" in result):
        if(result["operation2"]=="Any"):
            studentID=result["operation2"]
        else:    
            studentID=int(result["operation2"])
        title=result["operation3"]
        institution=result["operation4"]
        #print(institution)
        print(title,institution,studentID)
        if(institution=="Any" and studentID=="Any" and title=="Any"):
            try:
                cur = connect_to_db()
                print("befor")
                cur.execute(f"""
                    Select * from "Achievement"
                    Where "Technical"=false
                """)
                achievementDetails = cur.fetchall()
                option=1
                print("after")
                cur.close()
            except Exception as e:
                print(e)            
        elif(studentID=="Any"):
            if(title=="Any"):
                try:
                    cur = connect_to_db()
                    print("befor")
                    cur.execute(f"""
                    Select * from "Achievement"
                    Where "Institution" LIKE '%{institution}%' AND "Technical"=false 
                    """)
                    achievementDetails = cur.fetchall()
                    option=1
                    print("after")
                    cur.close()
                except Exception as e:
                    print(e)  
            elif(institution=="Any"):
                try:
                    cur = connect_to_db()
                    print("befor")
                    cur.execute(f"""
                    Select * from "Achievement"
                    Where "Title" LIKE '%{title}%' AND "Technical"=false 
                    """)
                    achievementDetails = cur.fetchall()
                    option=1
                    print("after")
                    cur.close()
                except Exception as e:
                    print(e)                
            else:
                try:
                    cur = connect_to_db()
                    print("befor")
                    cur.execute(f"""
                    Select * from "Achievement"
                    Where "Title" LIKE '%{title}%' AND "Institution" LIKE '%{institution}%' AND "Technical"=false 
                    """)
                    achievementDetails = cur.fetchall()
                    option=1
                    print("after ok")
                    cur.close()
                except Exception as e:
                    print(e)
        elif(title=="Any"):
            if(institution=="Any"):
                try:
                    cur = connect_to_db()
                    print("befor")
                    cur.execute(f"""
                    Select * from "Achievement"
                    Where "StudentId"={studentID} AND "Technical"=false
                    """)
                    achievementDetails = cur.fetchall()
                    option=1
                    print(cur.fetchall())
                    print("after")
                    cur.close()
                except Exception as e:
                    print(e)  
            else:
                try:
                    cur = connect_to_db()
                    print("befor")
                    cur.execute(f"""
                    Select * from "Achievement"
                    Where "StudentId"={studentID} AND "Institution" LIKE '%{institution}%' AND "Technical"=false 
                    """)
                    achievementDetails = cur.fetchall()
                    option=1
                    print(cur.fetchall())
                    print("after")
                    cur.close()
                except Exception as e:
                    print(e)
        elif(institution=="Any"):
            if(studentID=="Any"):
                try:
                    cur = connect_to_db()
                    print("befor")
                    cur.execute(f"""
                    Select * from "Achievement"
                    Where "Title" LIKE '%{title}%' AND "Technical"=false 
                    """)
                    achievementDetails = cur.fetchall()
                    option=1
                    print(cur.fetchall())
                    print("after")
                    cur.close()
                except Exception as e:
                    print(e)  
            else:
                try:
                    cur = connect_to_db()
                    print("befor")
                    cur.execute(f"""
                    Select * from "Achievement"
                    Where "StudentId"={studentID} AND "Title" LIKE '%{title}%' AND "Technical"=false 
                    """)
                    print("Pakoda4")
                    achievementDetails = cur.fetchall()
                    option=1
                    print(cur.fetchall())
                    print("after")
                    cur.close()
                except Exception as e:
                    print(e)
        else:
            try:
                cur = connect_to_db()
                print("befor")
                cur.execute(f"""
                Select * from "Achievement"
                Where "StudentId"={studentID} AND "Title" LIKE '%{title}%' AND "Institution" LIKE '%{institution}%' AND "Technical"=false 
                """)
                print("Pakoda5")
                achievementDetails = cur.fetchall()
                option=1
                print(cur.fetchall())
                print("after")
                cur.close()
            except Exception as e:
                print(e)





        # try:
        #     cur = connect_to_db()
        #     print("befor")
        #     cur.execute(f"""
        #     Select * from "Achievement"
        #     Where "StudentId"={studentID} AND "Technical"=false 
        #     """)
        #     achievementDetails = cur.fetchall()
        #     option=1
        #     print(cur.fetchall())
        #     print("after")
        #     cur.close()
        # except Exception as e:
        #     print(e)


        # title=result["operation3"]
        # try:
        #     cur = connect_to_db()
        #     print("befor")
        #     cur.execute(f"""
        #     Select * from "Achievement"
        #     Where "Title" LIKE '%{title}%' AND "Technical"=false 
        #     """)
        #     achievementDetails = cur.fetchall()
        #     option=2
        #     print(cur.fetchall())
        #     print("after")
        #     cur.close()
        # except Exception as e:
        #     print(e)

        # if(result["operation2"]=="By Institution"):
        #     institution=result["operation4"]
        #     try:
        #         cur = connect_to_db()
        #         print("befor")
        #         cur.execute(f"""
        #         Select * from "Achievement"
        #         Where "Institution" LIKE '%{institution}%' AND "Technical"=false 
        #         """)
        #         achievementDetails = cur.fetchall()
        #         option=3
        #         print(cur.fetchall())
        #         print("after")
        #         cur.close()
        #     except Exception as e:
        #         print(e)
    print(roll_title,roll_institution)
    return render_template('Sports_Cultural.html', 
        achievementDetails = achievementDetails,
        option=option,
        roll_calls=roll_calls,
        roll_institution=roll_institution,
        roll_title=roll_title,
        user = session['user'])
######################################################################################
#                                  ACADEMIC
######################################################################################
@app.route('/Academic',methods= ['GET', 'POST'])
def Academic():
    studentDetails = ""
    div1=0
    div2=0
    div3=0
    roll_calls=""
    result=request.form
    try:
        cur = connect_to_db()
        cur.execute(f"""
        Select "RollNo" from "Student";
        """)
        roll_calls = cur.fetchall()
        print(roll_calls)
        for aa in range(len(roll_calls)):
            str1=roll_calls[aa][0]
            roll_calls[aa]=str1
            print(str1)
        print(cur.fetchall())
        print("after")
        cur.close()

    except Exception as e:
        print(e) 

    try:
        cur = connect_to_db()
        cur.execute(f"""
        Select count(*) from "Student" where "GPA">=9;
        """)
        div1 = cur.fetchall()
        print(cur.fetchall())
        print("after")
        cur.close()
    except Exception as e:
        print(e)
    try:
        cur = connect_to_db()
        cur.execute(f"""
        Select count(*) from "Student" where "GPA">=7.5 and "GPA"<9;
        """)
        div2 = cur.fetchall()
        print(cur.fetchall())
        print("after")
        cur.close()
    except Exception as e:
        print(e)

    try:
        cur = connect_to_db()
        cur.execute(f"""
        Select count(*) from "Student" where "GPA"<7.5;
        """)
        div3 = cur.fetchall()
        print(cur.fetchall())
        print("after")
        cur.close()
    except Exception as e:
        print(e)

    if("Academic-submit" in result):
        print("in Academic-submit")
        print(result)
        rollno=result["rollno"]
        gpa=result["gpa"]
        if(result["operation"]=="Update"):
            if(gpa!="GPA" and rollno!="RollNo"):
                try:
                    cur = connect_to_db()
                    cur.execute(f"""
                    UPDATE "Student"  
                    SET "GPA"={gpa}
                    Where "RollNo"={rollno} 

                    """)
                    cur.close()
                except Exception as e:
                    print(e)
        if(result["operation"]=="Delete"):
            if(rollno!="RollNo"):
                try:
                    cur = connect_to_db()
                    cur.execute(f"""
                    UPDATE "Student"  
                    SET "GPA"={0}
                    Where "RollNo"={rollno}

                    """)
                    
                    cur.close()
                except Exception as e:
                    print(e)
    if("Search-submit" in result):
        if(result["operation2"]=="Any"):
            try:
                cur = connect_to_db()
                print("befor")
                cur.execute(f"""
                Select * from "Student" 
                """)
                studentDetails = cur.fetchall()
                print(cur.fetchall())
                print("after")
                cur.close()
            except Exception as e:
                print(e)
        else:
            rollno=result["operation2"]
            try:
                cur = connect_to_db()
                print("befor")
                cur.execute(f"""
                Select * from "Student"
                Where "RollNo"={rollno} 
                """)
                studentDetails = cur.fetchall()
                print(cur.fetchall())
                print("after")
                cur.close()
            except Exception as e:
                print(e)

    return render_template(
        'Academic.html',
        studentDetails = studentDetails,
        div1=div1,
        div2=div2,
        div3=div3,
        roll_calls=roll_calls,
        user = session['user'])

#######################################################################################################################################
#                             RECRUITER
#######################################################################################################################################

@app.route('/Recruiter',methods=['GET', 'POST'])
def RecruiterQueries():
    result=request.form
    x=""
    y=""
    z=""
    u=""
    v=""
    a=""
    b=""
    d=""
    g=""
    f=""
    ##Finding GPA of particular student Query
    print(result)
    if("GPA" in result):
        try:
            print("before")
            cur=connect_to_db()
            cur.execute(f""" select u."Name" ,s."RollNo", s."GPA" from "Student" as "s" , "User" as "u" where    s."RollNo" = '{result['RollNo']}' 
            and s."UserId" = u."EmailID" ; 
            """)
            x=cur.fetchall()
            print(cur.fetchall())
            print("after")
            cur.close()
        except Exception as e:
            print(e)
    ##Skills query
    if("Skills" in result):
        try:
            print("before")
            cur=connect_to_db()
            cur.execute(f""" select "StudentId" from "Skill" where "Title" = '{result['Skill']}';
            """)
            y=cur.fetchall()
            print(cur.fetchall())
            print("after")
            cur.close()
        except Exception as e:
            print(e)

    ##Range of GPA with degree
    if("Student_under_Degree" in result):
        try:
            print("before")
            cur=connect_to_db()
            cur.execute(f""" select u."Name", s."RollNo", s."Batch" from "Student" as "s","User" as "u" where s."GPA" >= '{result['GPAA']}' and s."UserId" = u."EmailID" and s."Degree" = '{result['Degree']}';
            """)
            z=cur.fetchall()
            u=cur.fetchall()
            print(cur.fetchall())
            print("after")
            cur.close()
        except Exception as e:
            print(e)

    if("Student_under_Degree" in result):
        print("before")
        print(result)
        if(result["Degree_Req1"] == "Bachelors"):
            try:
                cur=connect_to_db()
                cur.execute(f""" select u."Name", s."RollNo", s."Batch" from "Student" as "s","User" as "u" where s."GPA" >= '{result['GPAA']}' and s."UserId" = u."EmailID" and s."Degree" = 'Bachelors';
                """)
                
                u=cur.fetchall()
                print(cur.fetchall())
                print("after")
                cur.close()
            except Exception as e:
                print(e)            
        if(result["Degree_Req1"] == "Masters"):
            try:
                cur=connect_to_db()
                cur.execute(f""" select u."Name", s."RollNo", s."Batch" from "Student" as "s","User" as "u" where s."GPA" >= '{result['GPAA']}' and s."UserId" = u."EmailID" and s."Degree" = 'Masters';
                """)
                
                u=cur.fetchall()
                print(cur.fetchall())
                print("after")
                cur.close()
            except Exception as e:
                print(e)    
        if(result["Degree_Req1"] == "PHD"):
            try:
                cur=connect_to_db()
                cur.execute(f""" select u."Name", s."RollNo", s."Batch" from "Student" as "s","User" as "u" where s."GPA" >= '{result['GPAA']}' and s."UserId" = u."EmailID" and s."Degree" = 'PHD';
                """)
                u=cur.fetchall()
                print(cur.fetchall())
                print("after")
                cur.close()
            except Exception as e:
                print(e)            
        

        



    if("Skillset_Proof" in result):
        try:
            print("before")
            cur=connect_to_db()
            cur.execute(f""" select * from "Skill" where "StudentId" = '{result['RollNo1']}';

            """)
            v=cur.fetchall()
            print(cur.fetchall())
            print("after")
            cur.close()
        except Exception as e:
            print(e)


    if("Verification_Proof" in result):
        try:
            print("before")
            cur=connect_to_db()
            cur.execute(f""" select "StudentId","Title","Institution" from "Achievement" where "Proof" ='{result['Proof_Req']}' and "StudentId" = '{result['RollNo2']}';
            """)
            a=cur.fetchall()
            b=cur.fetchall()
            print(cur.fetchall())
            print("after")
            cur.close()
        except Exception as e:
            print(e)
    
    

    
    if("Project_under_Field" in result):
        print("before")
        print(result)
        
        if(result["Degree_Req"] == "Bachelors"):
            try:
                print("before")
                cur=connect_to_db()
                cur.execute(f""" select  u."Name" , s."RollNo" from "Student" as "s", "Indulged" as "i" ,"User" as "u", "Project" as "p" where p."Field" = '{result['Field1']}' and p."ProjectId" = i."ProjectId" and i."StudentId" = s."RollNo" and s."Degree" = 'Bachelors' and s."UserId" = u."EmailID";
                """)
                d=cur.fetchall()
                print(cur.fetchall())
                print("after")
                cur.close()
            except Exception as e:
                print(e)


        if(result["Degree_Req"] == "Masters"):
            try:
                print("before")
                cur=connect_to_db()
                cur.execute(f""" select  u."Name" , s."RollNo" from "Student" as "s", "Indulged" as "i" ,"User" as "u", "Project" as "p" where p."Field" = '{result['Field1']}' and p."ProjectId" = i."ProjectId" and i."StudentId" = s."RollNo" and s."Degree" = 'Masters' and s."UserId" = u."EmailID";
                """)
                d=cur.fetchall()
                print(cur.fetchall())
                print("after")
                cur.close()
            except Exception as e:
                print(e)
        
        if(result["Degree_Req"] == "PHD"):
            try:
                print("before")
                cur=connect_to_db()
                cur.execute(f""" select  u."Name" , s."RollNo" from "Student" as "s", "Indulged" as "i" ,"User" as "u", "Project" as "p" where p."Field" = '{result['Field1']}' and p."ProjectId" = i."ProjectId" and i."StudentId" = s."RollNo" and s."Degree" = 'PHD' and s."UserId" = u."EmailID";
                """)
                d=cur.fetchall()
                print(cur.fetchall())
                print("after")
                cur.close()
            except Exception as e:
                print(e)



    if("Project_under_Proof" in result):
        print("before")
        print(result)
        
        if(result["Proof_Req"] == "Verified"):
            try:
                cur = connect_to_db()
                cur.execute(f""" select "StudentId","Title","Institution" from "Achievement" where "Proof" =  
                'Verified' and "StudentId" = '{result['RollNo3']}';                
                """)
                f = cur.fetchall()
                print(cur.fetchall())

                cur.close()
            except Exception as e:
                print(e)
        if(result["Proof_Req"] == "File Uploaded"):
            try:
                cur = connect_to_db()
                cur.execute(f""" select "StudentId","Title","Institution" from "Achievement" where "Proof" =  
                'File Uploaded' and "StudentId" = '{result['RollNo3']}';                
                """)
                f = cur.fetchall()
                print(cur.fetchall())
                cur.close()
            except Exception as e:
                print(e)
        if(result["Proof_Req"] == "Pending"):
            try:
                cur = connect_to_db()
                cur.execute(f""" select "StudentId","Title","Institution" from "Achievement" where "Proof" =  
                'Pending' and "StudentId" = '{result['RollNo3']}';                
                """)
                f = cur.fetchall()
                print(cur.fetchall())

                cur.close()
            except Exception as e:
                print(e)

    # if("Profile" in result):
    try:
        cur=connect_to_db()
        cur.execute(f""" select * from "Recruiter" where "UserId"='{session['user']['EmailID']}';
        """)
        g=cur.fetchall()[0]
        g_headers = [h[0] for h in cur.description]
        cur.close()
    except Exception as e:
        print(e)

    if("Show_Details" in result):
        try:
            print("before")
            cur=connect_to_db()
            cur.execute(f""" select a."EducationId",d."Institution",d."Degree" from "Education" as "d" , "Attended_Student" as "a" where a."StudentId" = '{result['RollNo5']}' and a."EducationId" = d."EducationId";
            """)
            z=cur.fetchall()
            print(cur.fetchall())
            print("after")
            cur.close()
        except Exception as e:
            print(e)
    
    



    return render_template('Recruiter.html',
        x=x,
        y=y,
        z=z,
        u=u,
        v=v,
        a=a,
        b=b,
        d=d,
        g=list(zip(g_headers,g)),
        f=f,
        user = session['user'])

@app.route('/admin', methods = ['GET', 'POST'])
def admin():
    StudentDetails=""
    AchievementDetails=""
############################################################################
#                               UPDATE ADMIN
############################################################################
    if 'Batch' in request.form:
        batch = request.form['batch']
        rollNo = request.form['rollNo']
        if(rollNo!="RollNo" and batch!="Batch"):
            try:
                cur = connect_to_db()
                cur.execute(f"""
                    UPDATE "Student"
                    SET "Batch" = {batch}
                    WHERE "RollNo" = {rollNo};
                """)
                cur.close()
            except Exception as e:
                print(e)

    if 'ParentId' in request.form:
        parentId = request.form['parentId']
        rollNo = request.form['rollNo']
        if(rollNo!="RollNo" and parentId!="Parent EmailId"):
            try:
                cur = connect_to_db()
                cur.execute(f"""
                    UPDATE "Student"
                    SET "ParentId" = '{parentId}'
                    WHERE "RollNo" = {rollNo};

                """)
            except Exception as e:
                print(e)
            cur.close()

    if 'Password' in request.form:
        EmailId = request.form['EmailID']
        Password = request.form['password']
        if(EmailId!="EmailId" and len(Password)>=4):
            try:
                cur = connect_to_db()
                cur.execute(f"""
                    UPDATE "User"
                    SET "Password" = '{Password}'
                    WHERE "EmailID" = '{EmailId}';
                """)
            except Exception as e:
                print(e)
            cur.close()

    if 'Award' in request.form:
        rollNo = request.form['rollNo']
        Award = request.form['proof']
        
        if(rollNo!="RollNo" and Award!="Verification"):
            try:
                cur = connect_to_db()
                print(Award)    
                cur.execute(f"""
                    UPDATE "Achievement"
                    SET "Proof" = '{Award}'
                    WHERE "StudentId" = {rollNo} AND "Title" LIKE 'Dean List of Awardee';
                """)
                print(cur.fetchall())
            except Exception as e:
                print(e)
            cur.close()
        # print(request.form)
############################################################################
#                              SEARCH ADMIN
############################################################################
    if 'Batch1' in request.form:
        batch = request.form['batch']
        rollNo = request.form['rollNo']
        if(rollNo!="RollNo" and batch!="Batch"):
            try:
                cur = connect_to_db()
                cur.execute(f"""
                    Select * from "Student" Where "Batch"={batch} and "RollNo"={rollNo};
                """)
                StudentDetails=cur.fetchall()
                print(batch,rollNo,"ok",StudentDetails)
                cur.close()
            except Exception as e:
                print(e)

    if 'ParentId1' in request.form:
        parentId = request.form['parentId']
        rollNo = request.form['rollNo']
        if(rollNo!="RollNo" and parentId!="Parent EmailId"):
            try:
                cur = connect_to_db()
                cur.execute(f"""
                    Select * from "Student" where "ParentId" LIKE '%{parentId}%' AND "RollNo"={rollNo};

                """)
                StudentDeatils=cur.fetchall()
            except Exception as e:
                print(e)
            cur.close()

    if 'Award1' in request.form:
        rollNo = request.form['rollNo']
        Award = request.form['proof']
        
        if(rollNo!="RollNo" and Award!="Verification"):
            try:
                cur = connect_to_db()
                print(Award)    
                cur.execute(f"""
                    Select * from Achievement where "Proof" LIKE '%{Award}%' AND "StudentId"={rollNo} AND "Title" LIKE 'Dean List of Awardee';

                """)
                AchievementDetails=cur.fetchall()
            except Exception as e:
                print(e)
            cur.close()
        elif(rollNo!="RollNo"):
            try:
                cur = connect_to_db()
                print(Award)    
                cur.execute(f"""
                    Select * from Achievement where "StudentId"={rollNo} AND "Title" LIKE 'Dean List of Awardee';

                """)
                AchievementDetails=cur.fetchall()
            except Exception as e:
                print(e)
            cur.close()            
#################################
    cur = connect_to_db()
    cur.execute(f"""
        select "RollNo"
        from "Student";
    
    """)
    roll_numbers = [i[0] for i in cur.fetchall()]
    cur.close()
    
    cur = connect_to_db()
    cur.execute(f"""
        select "EmailID"
        from "User"
        where "Designation" = 'Parent';
    """)
    parentIds = [i[0] for i in cur.fetchall()]
    cur.close()

    cur = connect_to_db()
    cur.execute(f"""
        select *
        from "Student";
    """)
    students = cur.fetchall()
    students_headers = [h[0] for h in cur.description]
    cur.close()
    
    cur = connect_to_db()
    cur.execute(f"""
        select "EmailID"
        from "User";
    """)
    emailids = [i[0] for i in cur.fetchall()]
    # students_headers = [h[0] for h in cur.description]
    cur.close()

    return render_template('admin.html', 
        roll_numbers = roll_numbers,
        students = students,
        students_headers = students_headers,
        parentIds = parentIds,
        emailids = emailids,
        StudentDetails=StudentDetails,
        AchievementDetails=AchievementDetails
    )