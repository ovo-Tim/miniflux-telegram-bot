import subprocess
import os
import select
import time
import atexit

process = None
TIME_OUT = 60*60
@atexit.register
def cleanup():
    if process and process.poll() is None:
        process.terminate()
        process.wait()
        print("Process terminated on exit")

while True:
    st = time.time()
    process = subprocess.Popen(["python3", "./main.py"],
                               cwd=os.getcwd(),
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               text=True)

    while process.poll() is None:
        time.sleep(1)
        readable, _, _ = select.select([process.stdout], [], [], 0.1)
        if process.stdout in readable:
            line = process.stdout.readline()
            if line:
                print("Output:", line.strip())

        readable, _, _ = select.select([process.stderr], [], [], 0.1)
        if process.stderr in readable:
            line = process.stderr.readline()
            if line:
                print("Error:", line.strip())

        if time.time() - st > TIME_OUT:
            process.terminate()
            process.wait()
            print("Process terminated due to timeout")

    print("Process terminated with exit code:", process.returncode, "Restarting...")
    time.sleep(120)