import requests

def test_post_app():
    url = "https://obixconfigdoctor.onrender.com/app"
    r = requests.post(url, data={
        "size": "5", "weight": "450", "battery": "4S", "style": "Freestyle",
        "prop_size": "5", "blades": "2", "pitch": "3"
    }, timeout=10)
    assert r.status_code == 200
