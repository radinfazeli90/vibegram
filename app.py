from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "vibegram-secret"

# 📁 uploads folder (Render safe)
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

# ---------------- HOME ----------------
@app.route("/")
def home():
    return render_template("register.html")

# ---------------- SIGN UP ----------------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")

        if not username:
            return redirect(url_for("home"))

        session["username"] = username
        return redirect(url_for("feed", username=username))

    return render_template("signup.html")

# ---------------- FEED ----------------
@app.route("/feed/<username>")
def feed(username):
    return render_template("feed.html", username=username, posts=posts)

# ---------------- POST ----------------
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

# ---------------- UPLOADS ----------------
@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory("uploads", filename)

# ---------------- LIKE ----------------
@app.route("/like/<username>/<int:index>")
def like(username, index):

    user = session.get("username")

    if not user:
        return redirect(url_for("home"))

    if index < 0 or index >= len(posts):
        return redirect(url_for("feed", username=username))

    post = posts[index]

    if user in post["liked_by"]:
        post["liked_by"].remove(user)
        post["likes"] -= 1
    else:
        post["liked_by"].append(user)
        post["likes"] += 1

    return redirect(url_for("feed", username=username))

# ---------------- PROFILE ----------------
@app.route("/profile/<username>")
def profile(username):
    user_posts = [p for p in posts if p.get("user") == username]
    return render_template("profile.html", username=username, posts=user_posts)

# ---------------- RUN (Render FIX) ----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
