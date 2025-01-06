import base64
import os
import urllib.parse

import requests
from Crypto.Cipher import AES
from Crypto.Hash import MD5
from Crypto.Util.Padding import unpad
from lxml import etree

YUDOU_HOME = "https://www.yudou66.com/"


def decrypt(ciphertext, password):
    encrypt_data = base64.b64decode(ciphertext)

    salt = encrypt_data[8:16]
    ciphertext = encrypt_data[16:]

    derived = b""
    while len(derived) < 48:
        hasher = MD5.new()
        hasher.update(derived[-16:] + password.encode("utf-8") + salt)
        derived += hasher.digest()

    key = derived[0:32]
    iv = derived[32:48]

    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = unpad(cipher.decrypt(ciphertext), 16)
    return decrypted.decode("utf-8")


def main():

    home_html = requests.get(YUDOU_HOME)

    home_etree = etree.HTML(home_html.text)
    hrefs = home_etree.xpath('//*[@id="main"]//a/@href')

    print(f"read url from {hrefs[0]}")

    today_html = requests.get(hrefs[0])

    today_etree = etree.HTML(today_html.text)
    scripts = today_etree.xpath("//script")

    encryption = ""
    for script in scripts:
        if script.text and "encryption" in script.text:
            find = False
            for line in script.text.split("\n"):
                if find and encryption == "":
                    encryption = line.split('"')[1]
                    break
                if "encryption" in line:
                    find = True
            break

    if encryption == "":
        print("get encryption failed")
        os._exit(1)

    print("get encryption success")

    parse_data(encryption)


def parse_data(encry_data):
    urls = []
    decry_data = ""

    for pwd in range(1000, 10000):
        try:
            decry_data = decrypt(encry_data, str(pwd))
            break
        except Exception:
            continue

    if decry_data == "":
        print("parse encry password failed")
        os._exit(1)
    print("parse encry password success")

    decrypted_decoded = urllib.parse.unquote(decry_data)
    test = etree.HTML(decrypted_decoded)
    brs = test.xpath("//br")
    for br in brs:
        if br.tail and br.tail.startswith("http"):
            urls.append(br.tail)
    if len(urls) == 0:
        print("cannot parse sub url")
        os._exit(1)
    print("parse sub url success")

    download_sub_url(urls)


def download_sub_url(urls):
    for url in urls:
        print(f"get data from {url}")
        r = requests.get(url)
        file = "../output/"
        if url.endswith("txt"):
            file += "v2ray.txt"
        elif url.endswith("yaml"):
            file += "clash.yaml"
        if file:
            print(f"write file {file}")
            with open(file, "w", encoding="utf-8") as f:
                f.write(r.text)


if __name__ == "__main__":
    main()
