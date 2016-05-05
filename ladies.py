from instagram.client import InstagramAPI
from flask import Flask, render_template, request
from clarifai.client import ClarifaiApi

INSTAGRAM_TOKEN = "415073090.539d1f7.14bc529d42ed40ad89af79b671462f98"

def get_instagram_recent_media():
    api = InstagramAPI(access_token=INSTAGRAM_TOKEN)
    user = api.user("self")
    recent_media, next_page = api.user_recent_media(used_id=user.id, count=20)
    return recent_media
    
#for media in get_instagram_recent_media():
 #   print media.caption
 
app = Flask(__name__)

@app.route("/")
def hello():
    recent_media = get_instagram_recent_media()
    context = {
            "media": recent_media
    }
    return render_template("image.html", **context)

@app.route("/tags/")
def tags():
    url = request.args.get('url')
    tags = image_tags_recognition(url)
    return ", ".join(tags)


CLARIFY_ID = "hF5aLr77Qdx7Pz6Y_7oAme5ntQO15_esUT4DL4bo"
CLARIFY_SECRET = "pWO29ycwWDPv-QWwG-gJRYStVeluBN2LNmsGnYbV"

def image_tags_recognition(url):
    clarifai_api = ClarifaiApi(app_id=CLARIFY_ID, app_secret=CLARIFY_SECRET)
    response = clarifai_api.tag_image_urls(url)
    if response['status_code'] == 'OK':
        return response['results'][0]['result']['tag']['classes']

app.jinja_env.globals.update(
    tags_recognition=image_tags_recognition
)

if __name__ == "__main__":
   app.run(port=8080, host="0.0.0.0", debug=True)
