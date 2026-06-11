from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "vibegram-secret"

UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

posts = [
    {
        "text": "Welcome to VibeGram",
        "user": "system",
        "likes": 0,
        "liked_by": [],
        "image": None
    }
]

@app.route("/")
def home():
    return render_template("register.html")

@app.route("/signup", methods=["POST"])
def signup():
    username = request.form.get("username")

    if not username:
        return redirect("/")

    session["username"] = username
    return redirect(f"/feed/{username}")

@app.route("/feed/<username>")
def feed(username):
    return render_template("feed.html", username=username, posts=posts)

@app.route("/post/<username>", methods=["GET", "POST"])
def post(username):

    if request.method == "GET":
        return render_template("post.html", username=username)

    text = request.form["text"]
    file = request.files.get("photo")

    image_url = None

    if file and file.filename != "":
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)
        image_url = "/uploads/" + filename

    posts.append({
        "text": text,
        "user": session.get("username"),
        "likes": 0,
        "liked_by": [],
        "image": image_url
    })

    return redirect(url_for("feed", username=username))

@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory("uploads", filename)

@app.route("/like/<username>/<int:index>")
def like(username, index):

    user = session.get("username")

    if not user:
        return redirect("/")

    if index < 0 or index >= len(posts):
        return redirect(f"/feed/{username}")

    post = posts[index]

    if user in post["liked_by"]:
        post["liked_by"].remove(user)
        post["likes"] -= 1
    else:
        post["liked_by"].append(user)
        post["likes"] += 1

    return redirect(f"/feed/{username}")

@app.route("/profile/<username>")
def profile(username):
    user_posts = [p for p in posts if p.get("user") == username]
    return render_template("profile.html", username=username, posts=user_posts)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
