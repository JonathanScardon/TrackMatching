import os
import copy
from collections import defaultdict, deque

import fixtrack.common.utils as utils


class Candidates():
    def undoable(func):
        def decorated_func(self, *args, **kwargs):
            self._undo_queue.append(copy.deepcopy(self.items))
            func(self, *args, **kwargs)

        return decorated_func
    
    def __init__(self, fname, undo_len=20):
        self.items = self.load(fname)
        self._undo_queue = deque(maxlen=undo_len)
        self._redo_queue = deque(maxlen=undo_len)

    def load(self, fname):

        fname = utils.expand_path(fname)
        assert os.path.exists(fname), f" '{fname} does not exist"

        #leftID : rightID : [list of intervals]
        candidates = defaultdict(lambda: defaultdict(list))

        with open(fname, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                leftID, rightID, start, end = map(int, line.split(","))
                
                candidates[leftID][rightID].append({
                    "start_frame": start,
                    "end_frame": end
                })

        return candidates
    
    @undoable
    def delete_candidate(self, data):
        self.items[data["left_id"]][data["right_id"]].remove({"start_frame": data["start"], "end_frame": data["end"]})

    def save(self, fname):
        fname = utils.expand_path(fname)

        with open(fname, 'w') as f:
            for leftID, right_dict in self.items.items():
                for rightID, intervals in right_dict.items():
                    for interval in intervals:
                        start = interval["start_frame"]
                        end = interval["end_frame"]

                        line = f"{leftID},{rightID},{start},{end}\n"
                        f.write(line)

    def undo(self):
        if len(self._undo_queue) == 0:
            return
        self._redo_queue.append(self.items.copy())
        self.items = self._undo_queue.pop()


    def redo(self):
        if len(self._redo_queue) == 0:
            return
        self._undo_queue.append(self.items.copy())
        self.items = self._redo_queue.pop()