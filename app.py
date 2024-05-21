from flask import Flask, render_template, request, Response
from utils import create_question_object, create_score_object, get_field
from answers import my_list
import json
import pandas as pd
import dropbox
import functools
from flask import request, abort
from apscheduler.schedulers.background import BackgroundScheduler



app = Flask(__name__, template_folder="templates")

ADMIN_EMAIL = "admin@host.local"
ADMIN_PASSWORD = "12789"

email_list = []
password_list = []
wholeCredentials = []
email = ""
password = ""
name = ""
authentic = ""
global score_list, maxmarks, numqs
score_list = []
maxmarks = 4
numqs = 20

# BROWSERS = ['Mozilla', 'Gecko', 'Chrome', 'Safari']
# def no_browsers(f):
#     @functools.wraps(f)
#     def wrapper(*args, **kwargs):
#         user_agent = request.headers.get('User-Agent', '')
#         if any(agent in user_agent for agent in BROWSERS):
#             return abort(400)
#         return f(*args, **kwargs)
#     return wrapper

@app.route("/quiz", methods=["POST", "GET"])
def quiz():
    qno = 0
    quiz = []
    questions = []

    questions_file = open("questions.txt", "r")
    questions = questions_file.read().splitlines()
    questions_file.close()

    for question in questions:
        qno += 1
        question_object = create_question_object(question, qno)
        quiz.append(question_object)

    qno = 0
    return render_template("quiz.html", array=quiz)


@app.route("/input_check_result", methods=["POST", "GET"])
def input_check_result():
    return render_template("input_check_result.html")

def isExist(email = '', name = ''):
    exist = False
    rec = []
    # df = pd.read_csv('scoreboard.csv')
    df1 = pd.read_csv('https://www.dropbox.com/scl/fi/v28h3jutezqgs13ewlo7u/scoreboard.csv?rlkey=eyojnz0anyt5rpr2s3wft8ojg&st=ijejyxw0&dl=1', sep = ',')
    df2 = pd.read_csv('scoreboard.csv')
    result = pd.concat([df1, df2])
    outlist = result.values.tolist()


    for idx in range(len(outlist)):
        idx_email = outlist[idx][0]
        if idx_email == email:
            rec = outlist[idx]
            exist = True

    if (name != ''):
        for idx in range(len(outlist)):
            idx_name = outlist[idx][1]
            if idx_name == name:
                exist = True

    return (rec, exist)


@app.route("/check_result", methods=["POST", "GET"])
def check_result():
    ckemail = request.form.get("ckemail").strip()

    print("-" * 100)
    ls = isExist(ckemail)
    rec = ls[0]
    exist = ls[1]
    rec.append(exist)    
    print(rec)

    # return render_template("user.html")
    return render_template("check_result.html", contents=rec)

#@no_browsers
@app.route("/submit", methods=["POST", "GET"])
def submit_quiz():
    try:
        attempts = []
        score = 0
        percent_score = 0
        quiz = []

        questions_file = open("questions.txt", "r")
        questions = questions_file.read().splitlines()
        questions_file.close()
        number = 0

        for question in questions:
            question_object = create_question_object(question, number)
            quiz.append(question_object)

        for idx in range(0, len(quiz)):
            mcq = "mcq" + str(idx + 1)
            attempts.append(request.form.get(mcq))

        for idx in range(0, len(attempts)):
            # if quiz[idx].correct == attempts[idx]:
            #     score += 1
            qs_index = my_list[idx]
            print("*" * 100)
            print(attempts[idx])
            print(qs_index)

            for value, option in enumerate(qs_index, 1):
                if option[:-1] == attempts[idx]:
                    print("Matched", value)
                    point = int(option[-1])
                    score += point

        flname = request.form.get("flname").strip()
        flemail = request.form.get("email").strip()

        exist = isExist(flemail, flname)[1]

        if not exist:
            with open("attempts.csv", "a") as file:
                save_attempts = attempts
                print("-" * 100)
                print(flname, flemail)
                percent_score = score / (maxmarks*numqs) * 100.0
                percent_score = round(percent_score, 2)

                attempts.insert(0, flname)
                attempts.insert(1, flemail)
                attempts.append(str(score))
                attempts.append(str(percent_score))

                file.write(",".join(map(str, attempts)))
                file.write("\n")

                score_list.append((flemail, flname, score, percent_score))
                print("~" * 100)
                print(score_list)

            with open("scoreboard.csv", "a") as file:
                file.write(",".join(map(str, (flemail, flname, score, percent_score))))
                file.write("\n")

        #upload files to dropbox
        return render_template(
            "result.html", contents=[str(flname), str(score), str(percent_score), exist]
        )
    except Exception as e: 
        print(e)
        return abort(400)


@app.route("/upload", methods=["POST", "GET"])
def upload():
    try:
        dbx = dropbox.Dropbox(oauth2_refresh_token="8eo5uhh8gyMAAAAAAAAAAdQi_KyQORu0H1M-Uz6RzB6fZnvsSmmpjFDLHHdphFYl", app_key= '8acxm40niuruxve', app_secret = '2m1n6svs3oecqvq')

        print("enter")
        df1 = pd.read_csv('https://www.dropbox.com/scl/fi/v28h3jutezqgs13ewlo7u/scoreboard.csv?rlkey=eyojnz0anyt5rpr2s3wft8ojg&st=ijejyxw0&dl=1', sep = ',')
        print("exist")
        df2 = pd.read_csv('scoreboard.csv')
        result = pd.concat([df1, df2])
        result = result.drop_duplicates(keep=False, inplace=False)
        result.to_csv('scoreboard2.csv', header=True, index=False)
        f = open("scoreboard2.csv", 'rb')
        print(dbx.files_upload(f.read(), "/scoreboard.csv", mode=dropbox.files.WriteMode("overwrite")))
        print(result)

        df1 = pd.read_csv('https://www.dropbox.com/scl/fi/wud60y2pc5lao9h5995jf/attempts.csv?rlkey=i9y75we1jze1744s9gzscr27m&st=x9uezkki&dl=1', sep = ',')
        df2 = pd.read_csv('attempts.csv')
        result = pd.concat([df1, df2])
        result = result.drop_duplicates(keep=False, inplace=False)
        result.to_csv('attempts2.csv', header=True, index=False)
        f = open("attempts2.csv", 'rb')
        print(dbx.files_upload(f.read(), "/attempts.csv", mode=dropbox.files.WriteMode("overwrite")))
        print(result)

        return Response("Done Uploading", mimetype="text/plain")

    except Exception as e: 
        print(e)
        return abort(400)


@app.route("/start_schedule_upload", methods=["POST", "GET"])
def start_schedule_upload():
    try:
        # Create the background scheduler
        scheduler = BackgroundScheduler()
        # Create the job
        scheduler.add_job(func=upload, trigger="interval", seconds=120)
        # Start the scheduler
        scheduler.start()
        return Response("Schedule Upload Started (360 interval)", mimetype="text/plain")
    except Exception as e: 
        print(e)
        return abort(400)


@app.route("/attempts", methods=["POST", "GET"])
def display_attempts():
    with open("attempts2.csv", "r") as f:
        content = f.read()
    return Response(content, mimetype="text/plain")


@app.route("/download_attempts", methods=["POST", "GET"])
def download_attempts():
    with open("attempts2.csv", "r") as f:
        content = f.read()

    response = Response(content, content_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=attempts.csv"
    return response


@app.route("/scoreboard", methods=["POST", "GET"])
def display_scoreboard():
    with open("scoreboard2.csv", "r") as f:
        content = f.read()
    return Response(content, mimetype="text/plain")


@app.route("/download_scoreboard", methods=["POST", "GET"])
def download_scoreboard():
    with open("scoreboard2.csv", "r") as f:
        content = f.read()

    response = Response(content, content_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=scoreboard.csv"
    return response


# @app.route("/show", methods=["POST", "GET"])
# def results():
#     return render_template("result.html", var1=str(score), var2=str(len(attempts)))


@app.route("/quizstrt", methods=["POST", "GET"])
def strt():
    return render_template("quizstrt.html")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")


