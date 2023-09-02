from flask import Flask, request, jsonify, send_file
from cloth_segmentation import cloth_segmentation
from sdwebui import img2img
import time
import os

# result_path = img2img(positive_prompt, negative_prompt, image_path, masked_image_path)

app = Flask(__name__)

@app.route('/', methods=['POST'])
def main():
    # get image from request
    image = request.files['image']

    # save image to in-images folder with timestamp
    timestr = time.strftime("%Y%m%d-%H%M%S")
    image_path = f"./in-images/{timestr}.jpg"
    image.save(image_path)
    masked_image_path = cloth_segmentation(image_path)

    positive_prompt = "woman nude, nude bare naked, breasts, detailed nipples"
    negative_prompt = "ugly, deformed, deformityc, disfigured, malformed, ugliness, blurry, disfigured, mutation, mutated, extra limbs, bad anatomy, long body, cropped head, cropped face, two women, anatomical nonsense, malformed hands, long neck, missing limb, floating limbs, disconnected limbs, anime"

    result_path = img2img(positive_prompt, negative_prompt, image_path, masked_image_path)

    return send_file(result_path, mimetype='image/gif')
    
    
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))