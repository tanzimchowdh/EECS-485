import os
import logging
import json
import time
import click
import threading
import pathlib
import shutil
import mapreduce.utils


# Configure logging
logging.basicConfig(level=logging.DEBUG)


class Master:
    def __init__(self, port):
        logging.info("Starting master:%s", port)
        logging.info("Master:%s PWD %s", port, os.getcwd())
        pathlib.Path("tmp/").mkdir(exist_ok=True)
        for directory in pathlib.Path("tmp/").glob("job-*"):
            if (os.path.isdir(directory)):
                shutil.rmtree(directory)

        # This is a fake message to demonstrate pretty printing with logging
        message_dict = {
            "message_type": "register",
            "worker_host": "localhost",
            "worker_port": 6001,
            "worker_pid": 77811
        }
        logging.debug("Master:%s received\n%s",
            port,
            json.dumps(message_dict, indent=2),
        )

        # TODO: you should remove this. This is just so the program doesn't
        # exit immediately!
        logging.debug("IMPLEMENT ME!")
        time.sleep(120)


@click.command()
@click.argument("port", nargs=1, type=int)
def main(port):
    Master(port)


if __name__ == '__main__':
    main()
