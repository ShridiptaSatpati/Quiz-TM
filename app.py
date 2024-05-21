from flask import Flask, render_template, request, Response
from utils import create_question_object, create_score_object, get_field
from answers import my_list
import json
import pandas as pd
import dropbox
import functools
from flask import request, abort

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
global score_list
score_list = []

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


@app.route("/check_result", methods=["POST", "GET"])
def check_result():
    rec = []
    ckemail = request.form.get("ckemail").strip()
    exist = False

    df = pd.read_csv('scoreboard.csv')
    outlist = df.values.tolist()


    for idx in range(len(outlist)):
        idx_email = outlist[idx][0]
        if idx_email == ckemail:
            rec = outlist[idx]
            exist = True

    print("-" * 100)
    print(rec)
    rec.append(exist)
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
                    score += option[-1]

        flname = request.form.get("flname").strip()
        flemail = request.form.get("email").strip()
        exist = False

        df = pd.read_csv('scoreboard.csv')
        outlist = df.values.tolist()

        for idx in range(len(outlist)):
            idx_email = outlist[idx][0]
            if idx_email == flemail:
                exist = True

        for idx in range(len(outlist)):
            idx_name = outlist[idx][1]
            if idx_name == flname:
                exist = True


        if not exist:
            with open("attempts.csv", "a") as file:
                save_attempts = attempts
                print("-" * 100)
                print(flname, flemail)
                percent_score = score / (4*20) * 100.0
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
                for idx in score_list:
                    file.write(",".join(map(str, idx)))
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
        f1 = open("attempts.csv", 'rb')
        print(dbx.files_upload(f1.read(), "/attempts.csv", mode=dropbox.files.WriteMode("overwrite")))

        f2 = open("scoreboard.csv", 'rb')
        print(dbx.files_upload(f2.read(), "/scoreboard.csv", mode=dropbox.files.WriteMode("overwrite")))
        return Response("Done Uploading", mimetype="text/plain")

    except Exception as e: 
        print(e)
        return abort(400)



@app.route("/attempts.csv", methods=["POST", "GET"])
def display_attempts():
    with open("attempts.csv", "r") as f:
        content = f.read()
    return Response(content, mimetype="text/plain")


@app.route("/download_attempts.csv", methods=["POST", "GET"])
def download_attempts():
    with open("attempts.csv", "r") as f:
        content = f.read()

    response = Response(content, content_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=attempts.csv"
    return response


@app.route("/scoreboard.csv", methods=["POST", "GET"])
def display_scoreboard():
    with open("scoreboard.csv", "r") as f:
        content = f.read()
    return Response(content, mimetype="text/plain")


@app.route("/download_scoreboard.csv", methods=["POST", "GET"])
def download_scoreboard():
    with open("scoreboard.csv", "r") as f:
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


# if __name__ == "__main__":
#     app.run(debug=True, host="0.0.0.0")


