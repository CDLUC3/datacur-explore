import argparse
from app.interface.app import create_app
import sys
import os


# determine a robust project root (where `app` package lives)
_here = Path(__file__).resolve().parent
if (_here / 'app').is_dir():
    _project_root = _here
elif (_here.parent / 'app').is_dir():
    _project_root = _here.parent
else:
    # fallback to previous behavior (closest parent)
    _project_root = _here.parent

sys.path.insert(0, str(_project_root))


def main():
    parser = argparse.ArgumentParser(description="Run the Gradio app with specified options.")
    parser.add_argument('--listen', type=str, default="127.0.0.1",
                        help="If set, the app will listen on the the IP address.")
    parser.add_argument('--port', type=int, default=7860, help="The port to run the app on.")
    parser.add_argument('--share', action='store_true', help="If set, the app will create a public link.")
    parser.add_argument('--user', type=str, help="Username for authentication.")
    parser.add_argument('--password', type=str, help="Password for authentication.")
    parser.add_argument('--debug', action='store_true', help="If set, the app will run in debug mode.")
    parser.add_argument('--ssl_keyfile', type=str, help="Path to the SSL key file.")
    parser.add_argument('--ssl_certfile', type=str, help="Path to the SSL certificate file.")

    args = parser.parse_args()

    # Create the Gradio app
    iface = create_app()

    auth = None
    if args.user and args.password:
        auth = (args.user, args.password)

    iface.launch(debug=args.debug, share=args.share, auth=auth, server_name=args.listen, server_port=args.port,
                 ssl_keyfile=args.ssl_keyfile, ssl_certfile=args.ssl_certfile)

if __name__ == "__main__":
    main()
