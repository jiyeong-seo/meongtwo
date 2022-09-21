import os, random, string

from pymongo import MongoClient
import jwt
import datetime
import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import certifi
from bson.objectid import ObjectId

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = "./static/profile_pics"

SECRET_KEY = 'SPARTA'

# 페이저 포스트 노출 갯수
page_view_config = 5

ca = certifi.where()

client = MongoClient('mongodb+srv://test:sparta@cluster0.38yzx.mongodb.net/?retryWrites=true&w=majority', tlsCAFile=ca)
db = client.meongsyullaeng


@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"username": payload["id"]})

        # 페이저 용 카운트
        post_count = int((db.posts.count_documents({}) / page_view_config) + 1)
        return render_template('index.html', user_info=user_info, post_count=post_count)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)


@app.route('/user/<username>')
def user(username):
    # 각 사용자의 프로필과 글을 모아볼 수 있는 공간
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        status = (username == payload["id"])  # 내 프로필이면 True, 다른 사람 프로필 페이지면 False

        user_info = db.users.find_one({"username": username}, {"_id": False})

        # 페이저 프로필용 카운트
        post_count = int((db.posts.count_documents({"username": username}) / page_view_config) + 1)
        return render_template('user.html', user_info=user_info, status=status, post_count=post_count)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route('/sign_in', methods=['POST'])
def sign_in():
    # 로그인
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']

    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    result = db.users.find_one({'username': username_receive, 'password': pw_hash})

    if result is not None:
        payload = {
            'id': username_receive,
            'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


@app.route('/sign_up/save', methods=['POST'])
def sign_up():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    doc = {
        "username": username_receive,
        "password": password_hash,
        "profile_name": username_receive,
        "profile_pic": "",
        "profile_pic_real": "profile_pics/profile_placeholder.png",
        "profile_info": ""
    }
    db.users.insert_one(doc)
    return jsonify({'result': 'success'})


@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    username_receive = request.form['username_give']
    exists = bool(db.users.find_one({"username": username_receive}))
    # print(value_receive, type_receive, exists)
    return jsonify({'result': 'success', 'exists': exists})


@app.route('/update_profile', methods=['POST'])
def save_img():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        username = payload["id"]
        name_receive = request.form["name_give"]
        about_receive = request.form["about_give"]
        new_doc = {
            "profile_name": name_receive,
            "profile_info": about_receive
        }
        if 'file_give' in request.files:
            file = request.files["file_give"]

            # 이미지 업로드 경로 설정
            path = "./static/profile_pics/"

            # 이미지 업로드 경로가 존재 하지 않을 경우 생성
            if not os.path.exists(path):
                os.mkdir(path)

            # filename = secure_filename(file.filename) -secure_filename()은 한글을 지원하지 않는다
            # 자바스크립트로 username 유효성 검사 중 이므로 한글은 올 수 없다 (유효성 처리 필요 X)
            receive_filename = file.filename
            extension = receive_filename.split(".")[-1]

            # 이미지 파일이 아닐 경우 리턴 한다
            extension_temp = extension.upper()
            if extension_temp != "JPG" and extension_temp != "PNG" and extension_temp != "GIF" and extension_temp != "BMP":
                return redirect(url_for("home"))

            # 업로드 파일 이름을 고유한 ID인 username으로 변경해 DB(문자열 경로)와 서버(파일)에 저장 (프론트에서 사용)
            file_path = f"profile_pics/{username}.{extension}"
            file.save("./static/" + file_path)
            new_doc["profile_pic"] = receive_filename
            new_doc["profile_pic_real"] = file_path

        # DB 등록
        db.users.update_one({'username': payload['id']}, {'$set': new_doc})
        return jsonify({"result": "success", 'msg': '프로필을 업데이트했습니다.'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route('/posting', methods=['POST'])
def posting():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        # 포스팅하기
        user_info = db.users.find_one({"username": payload["id"]})
        comment_receive = request.form["comment_give"]
        date_receive = request.form["date_give"]
        doc = {
            "username": user_info["username"],
            "profile_name": user_info["profile_name"],
            "profile_pic_real": user_info["profile_pic_real"],
            "comment": comment_receive,
            "date": date_receive
        }
        if 'img_file_give' in request.files:
            file = request.files["img_file_give"]

            # filename = secure_filename(file.filename) -secure_filename()은 한글을 지원하지 않는다
            receive_filename = file.filename

            # 이미지 업로드 경로가 존재 하지 않을 경우 생성
            path = "./static/post_images/"
            if not os.path.exists(path):
                os.mkdir(path)

            # 프론트에서 유효성 검사를 하지 않으므로 중복 제어와 보안을 위해 파일 명을 랜덤한 값으로 바꿔 줄 필요가 있다
            # secure_filename은 한글을 지원하지 않으므로 직접 변경한다
            # 파일 이름에 랜덤 문자열 삽입
            # 랜덤 문자열 갯수
            length_of_string = 8
            random_string = ''.join(
                random.choice(string.ascii_letters + string.digits) for _ in range(length_of_string))
            index_temp = receive_filename.rfind(".")
            filename = receive_filename[:index_temp] + random_string + receive_filename[index_temp:]

            # 이미지 파일이 아닐 경우 리턴 한다 (파일 명에 .이 여러개 올 경우 인덱스 마지막 문자열 가져옴 [-1])
            extension = receive_filename.split(".")[-1]
            extension_temp = extension.upper()
            if extension_temp != "JPG" and extension_temp != "PNG" and extension_temp != "GIF" and extension_temp != "BMP":
                return redirect(url_for("home"))

            file_path = f"post_images/{filename}"
            file.save("./static/" + file_path)
            doc["postfile_pic"] = filename
            doc["postfile_pic_real"] = file_path
        db.posts.insert_one(doc)
        return jsonify({"result": "success", 'msg': '포스팅 성공'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route('/posting/comment', methods=['POST'])
def comment_posting():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        # 댓글 달기
        user_info = db.users.find_one({"username": payload["id"]})
        comment_receive = request.form["comment_give"]
        date_receive = request.form["date_give"]
        postid_receive = request.form["id_give"]

        doc = {
            "username": user_info["username"],
            "profile_name": user_info["profile_name"],
            "profile_pic_real": user_info["profile_pic_real"],
            "comment": comment_receive,
            "post_id": postid_receive,
            "date": date_receive
        }

        db.comments.insert_one(doc)
        return jsonify({"result": "success", 'msg': '포스팅 성공'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route("/get_posts", methods=['GET'])
def get_posts():
    token_receive = request.cookies.get('mytoken')

    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        my_username = payload["id"]
        username_receive = request.args.get("username_give")

        # 페이저 기능
        # sort(기준 필드,디폴트 값은 정렬(ascending) -1은 역정렬(descending)), list(가져올 갯 수), skip(건너뛸 갯 수 offset)
        page_receive = request.args.get("page")

        if page_receive is not None and page_receive != "":
            page = int(request.args.get("page"))
        else:
            page = 1

        if username_receive == "":
            posts = list(db.posts.find({}).sort("date", -1).limit(page_view_config).skip((page - 1) * page_view_config))
            comments = list(db.comments.find({}, {'_id': False}))

        else:
            posts = list(db.posts.find({"username": username_receive}).sort("date", -1).limit(page_view_config).skip(
                (page - 1) * page_view_config))
            comments = list(db.comments.find({}, {'_id': False}))

        for post in posts:

            post["_id"] = str(post["_id"])
            post["count_heart"] = db.likes.count_documents({"post_id": post["_id"], "type": "heart"})
            post["heart_by_me"] = bool(
                db.likes.find_one({"post_id": post["_id"], "type": "heart", "username": my_username}))

        return jsonify({"result": "success", "msg": "포스팅을 가져왔습니다.", "posts": posts, "my_username": payload["id"], "comments": comments})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route('/update_like', methods=['POST'])
def update_like():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        # 좋아요 수 변경
        user_info = db.users.find_one({"username": payload["id"]})
        post_id_receive = request.form["post_id_give"]
        type_receive = request.form["type_give"]
        action_receive = request.form["action_give"]
        doc = {
            "post_id": post_id_receive,
            "username": user_info["username"],
            "type": type_receive
        }
        if action_receive == "like":
            db.likes.insert_one(doc)
        else:
            db.likes.delete_one(doc)
        count = db.likes.count_documents({"post_id": post_id_receive, "type": type_receive})
        return jsonify({"result": "success", 'msg': 'updated', "count": count})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route('/del_post', methods=['POST'])
def delete_post():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        post_id_receive = request.form["post_id_give"]
        post_db_receive = db.posts.find_one({'_id': ObjectId(post_id_receive)})

        # 포스팅한 유저와 현재 삭제 하려는 유저가 같다면 포스트+코멘트 삭제 하고 데이터 넘겨 주기
        if payload["id"] == post_db_receive['username']:
            db.comments.delete_many({"post_id": post_id_receive})
            db.posts.delete_one({'_id': ObjectId(post_id_receive)})
            return jsonify({"result": "success", 'msg': '성공'})
        else:
            return jsonify({"result": "fail", 'msg': '실패'})

    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route('/del_comment', methods=['POST'])
def delete_comment():

    return redirect(url_for("home"))


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
