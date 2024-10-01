#!/bin/bash

# this is an example gradio control script with some values omitted

cd /datacur/datacur-explore/gradio_gpt_gemini || exit

# Configurations
export GOOGLE_APPLICATION_CREDENTIALS="path/to/your/credentials.json"
PID_FILE="tmp/gradio_app.pid"
SSL_KEYFILE="path/to/your/privkey.pem"
SSL_CERTFILE="path/to/your/fullchain.pem"
APP_COMMAND="python -u app.py --listen=domain --ssl_keyfile=$SSL_KEYFILE --ssl_certfile=$SSL_CERTFILE"
# APP_COMMAND="python -u app.py --listen=0.0.0.0"
mkdir -p tmp
mkdir -p log

start() {
    if [ -f "$PID_FILE" ] && kill -0 $(cat "$PID_FILE") > /dev/null 2>&1; then
        echo "Gradio app is already running with PID $(cat $PID_FILE)"
        exit 1
    fi

    echo "Starting Gradio app..."
    nohup $APP_COMMAND > log/gradio_app.log 2>&1 &
    echo $! > "$PID_FILE"
    echo "Gradio app started with PID $(cat $PID_FILE)"
}

stop() {
    if [ -f "$PID_FILE" ] && kill -0 $(cat "$PID_FILE") > /dev/null 2>&1; then
        echo "Stopping Gradio app with PID $(cat $PID_FILE)..."
        kill $(cat "$PID_FILE") && rm -f "$PID_FILE"
        echo "Gradio app stopped."
    else
        echo "Gradio app is not running."
    fi
}

status() {
    if [ -f "$PID_FILE" ] && kill -0 $(cat "$PID_FILE") > /dev/null 2>&1; then
        echo "Gradio app is running with PID $(cat $PID_FILE)"
    else
        echo "Gradio app is not running."
    fi
}

restart() {
    echo "Restarting Gradio app..."
    stop
    start
}

case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    status)
        status
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        exit 1
        ;;
esac
