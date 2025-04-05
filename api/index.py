from flask import Flask, request, Response
import tls_client

app = Flask(__name__)

DISCORD_BASE_URL = 'https://discord.com'

# Khởi tạo session TLS mô phỏng trình duyệt Chrome
session = tls_client.Session(
    client_identifier="chrome_120",  # Giả lập Chrome 120
    random_tls_extension_order=True
)

@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def proxy(path):
    target_url = f'{DISCORD_BASE_URL}/{path}'

    # Loại bỏ header Host để tránh lỗi
    headers = {k: v for k, v in request.headers if k.lower() != 'host'}

    # Forward request
    try:
        response = session.request(
            method=request.method,
            url=target_url,
            headers=headers,
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=False,
        )

        # Gửi response về client
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        response_headers = [(k, v) for k, v in response.headers.items() if k.lower() not in excluded_headers]
        return Response(response.content, response.status_code, response_headers)

    except Exception as e:
        return {"error": str(e)}, 500

if __name__ == '__main__':
    app.run(port=5000)
