import uvicorn
import ssl

ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ssl_context.load_cert_chain(
    "/home/alexander/certs/cert.pem", keyfile="/home/alexander/certs/key.pem"
)

if __name__ == "__main__":
    uvicorn.run(
        app="main:app",
        host="localhost",
        port=8000,
        reload=True,
        proxy_headers=True,
        forwarded_allow_ips="*",
        ssl_certfile="/home/alexander/certs/cert.pem",
        ssl_keyfile="/home/alexander/certs/key.pem",
    )
