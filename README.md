# Achievements of Students of IIITD - DBMS Project


> Always git pull before starting

## Configuration:
    $ git clone <url>
    $ cd dbms
    $ nano .env
        - PASSWORD = <password_to_postgres_user>
    $ python app.py

## Github commands
    - git add -A
    - git commit -m "<user> <description>"
    - git push -u origin master 
    if want to make a branch
    - git checkout -b <branch_name>
    - git add -A
    - git commit -m "<message>"
    - git push -u origin <branch_name>
The database that we intend to design is meant to aid the placement process both for the students as well as the companies. With this database onboard, an application can be designed over it to store achievements and projects done by a student throughout his/her college life so as to have a track of them throughout their lifetime and have a soft copy of their resume ready. 

Perks of the above application are numerous. One of them being, companies would know when a student is trying to bluff in his/her interview about their GPA, or their college-related achievements like winning a sports tournament, getting a dean’s award, etc. Another being, students at times forget what their achievements were in their college, so this way they won’t ever miss out on any of the achievements in their resume.

There are fields that are editable only by the faculty and not the student, this was the authenticity is retained in the application as well the usage of the database. For example, the GPA is only updated by the Academics, the project is only editable and addable by the professor, etc. 

The parent as an entity comes into play when parents wish to have a look at the achievements of their child. The Sports committee will add the sports-related achievements of the students during their time as part of the institution. The cultural committee will update the cultural achievements made by a student as part of the institution.


With a brownie on the top, this database can be used to design a platform like PhDClinic where students can approach professors for various different projects and get to know the skill set required by the professor.
