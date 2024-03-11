import json
import datetime


class BaseCheckpoint(object):
    """
    The base class of checkpoint
    """
    def __init__(self, logger, url, start_date=None):
        self.logger = logger
        self.url = url
        self.start_date = start_date
        self.contents = {}
        self._reset_check_point()


    def _reset_check_point(self):
        """
        The method to reset the checkpoint
        """
        raise NotImplementedError("Derived class shall implement the function")


    def _get_content(self):
        """
        The method to get the content of the checkpoint.
        """
        return self.contents


    def read(self, content=None):
        """
        The method to read the checkpoint.
        """
        if content:
            ckpt = json.loads(content)
            self.contents = ckpt
        else:
            self._reset_check_point()


    def write(self):
        """
        The method to write checkpoint file.
        """
        return json.dump(self.contents)


    def delete(self):
        return self._reset_check_point()



class MyInputCheckpoint(BaseCheckpoint):
    def _reset_check_point(self):
        self.contents[self.url] = {}
        self.contents[self.url]["data"] = {}
        self.contents[self.url]["start_date"] = self.start_date


class MyInput2Checkpoint(BaseCheckpoint):
    def _reset_check_point(self):
        self.contents["last_process_time"] = None
        self.contents["data"] = []
        self.contents["start_date"] = self.start_date
