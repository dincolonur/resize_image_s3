import base64
import io
from PIL import Image
from flask import Flask, request, jsonify

app = Flask(__name__)

images = [
    {"id": 0, "img_name": "test", "size": [100,100]}
]


def _find_next_id():
    return max(image["id"] for image in images) + 1


@app.route("/im_size", methods=['POST'])
def process_image():
    payload = request.form.to_dict(flat=False)
    im_b64 = payload['image'][0]
    img_name = payload['img_name'][0]
    im_binary = base64.b64decode(im_b64)
    buf = io.BytesIO(im_binary)
    img = Image.open(buf)
    image = {"img_name": img_name, "size": [img.width, img.height]}
    image['id'] = _find_next_id()
    images.append(image)

    return jsonify({'msg': 'success', 'img_name': img_name, 'size': [img.width, img.height]})


@app.get("/images")
def get_images():
    return jsonify(images)


@app.route("/images/<id>", methods=['GET'])
def get_image(id):
    if 0 <= int(id) < len(images):
        return jsonify(images[int(id)])
    return {}


if __name__ == "__main__":
    app.run(debug=True)
