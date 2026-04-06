import numpy as np
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHeaderView


from fixtrack.frontend.canvas import VideoCanvas
from fixtrack.frontend.player_head import PlayerHeadWidget
from fixtrack.frontend.track_controls import TrackEditLayoutBar
from fixtrack.frontend.track_controls import TopLevelControls
from fixtrack.frontend.tools import Tools
from fixtrack.frontend.graph import CandidateGraph


class VideoWidget(QtWidgets.QWidget):
    """
    Main GUI component for the FixTrack application.
    """
    mutated = QtCore.pyqtSignal(bool)

    def __init__(
        self, parent, fname_video=None, fname_video2=None, fname_track=None, 
        fname_track2=None, fname_candidates=None, range_slider=True, bgcolor="white"
    ):
        """
        Initializes the VideoWidget and lays out all subcomponents.
        """
        super().__init__(parent)
        self._parent = parent



        #left video setup
        self.canvas = VideoCanvas(
            self, fname_video=fname_video, fname_track=fname_track, fname_candidates=fname_candidates, is_left=True, bgcolor=bgcolor
        )
        self.canvas.native.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
        )
        self.canvas.create_native()
        self.canvas.native.setParent(self)

        self.canvas.visuals["tracks"].displayed_candidates.connect(self.populate_table)


        #right video setup
        self.canvas2 = VideoCanvas(
            self, fname_video=fname_video2, fname_track=fname_track2, bgcolor=bgcolor
        )
        self.canvas2.native.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
        )
        self.canvas2.create_native()
        self.canvas2.native.setParent(self)


        #left vid scroll area
        self.scroll_area = QtWidgets.QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        sp = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding
        )
        self.scroll_area.setSizePolicy(sp)
        self.scroll_area.setFocusPolicy(QtCore.Qt.NoFocus)

         #right vid scroll area
        self.scroll_area2 = QtWidgets.QScrollArea(self)
        self.scroll_area2.setWidgetResizable(True)
        self.scroll_area2.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.scroll_area2.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        sp = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding
        )
        self.scroll_area2.setSizePolicy(sp)
        self.scroll_area2.setFocusPolicy(QtCore.Qt.NoFocus)


        self.setup_track_edit_bar(
            self.canvas.tracks.num_tracks,
            self.scroll_area,
            True
            )
        self.setup_track_edit_bar(
            self.canvas2.tracks.num_tracks,
            self.scroll_area2,
            False
            )
        

        self.top_level_ctrls = TopLevelControls(
            self, 
            self.canvas, 
            self.track_edit_bar
            )
        self.top_level_ctrls2 = TopLevelControls(
            self,
            self.canvas2,
            self.track_edit_bar2
            )
        
        
        self.dual_track_controls = PlayerHeadWidget(
                self,
                self.canvas.video,
                range_slider=False,
                dual_video_reader=self.canvas2.video,
        )

        
        
        self.dual_track_controls.sig_frame_change.connect(self.canvas.on_frame_change)
        self.dual_track_controls.sig_frame_change.connect(self.canvas2.on_frame_change)
        self.dual_track_controls.sig_frame_change.emit(0, True)

        self.dual_track_controls.play_button.clicked.connect(self.sync_play_state)
        self.dual_track_controls.prevButton.clicked.connect(self.sync_prev_state)
        # self.dual_track_controls.forwardButton.clicked.connect(self.sync_forward_state)
        # self.dual_track_controls.backButton.clicked.connect(self.sync_back_state)
        # self.dual_track_controls.nextButton.clicked.connect(self.sync_next_state)



        #leftmost column: left vid tools
        tools_col = QtWidgets.QVBoxLayout()
        tools_col.addWidget(self.top_level_ctrls)
        tools_col.addWidget(self.scroll_area)

        
        #left video column
        left_vid_col = QtWidgets.QVBoxLayout()
        left_vid_col.addWidget(self.canvas.native)
        self.player_controls = PlayerHeadWidget(
            self, self.canvas.video, range_slider=range_slider
        )
        left_vid_col.addWidget(self.player_controls)    
        
        #right video column
        right_vid_col = QtWidgets.QVBoxLayout()
        right_vid_col.addWidget(self.canvas2.native)
        self.player_controls2 = PlayerHeadWidget(
            self, self.canvas2.video, range_slider=range_slider
        )
        right_vid_col.addWidget(self.player_controls2)

        #righmost column: right vid tools
        tools_col2 = QtWidgets.QVBoxLayout()
        tools_col2.addWidget(self.top_level_ctrls2)
        tools_col2.addWidget(self.scroll_area2)

        #store left and right vids
        video_container = QtWidgets.QHBoxLayout()
        video_container.addLayout(left_vid_col)
        video_container.addLayout(right_vid_col)


        #candidates data table
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Left ID", "Right ID", "Start Frame", "End Frame", "Action"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)


        self.graph = CandidateGraph(self)


        #store left and right vids + dual playbar
        center_col = QtWidgets.QVBoxLayout()
        center_col.addLayout(video_container)
        center_col.addWidget(self.dual_track_controls)
        self.main_tools = Tools(self)
        center_col.addWidget(self.main_tools)

        temp = QtWidgets.QHBoxLayout()
        temp.addWidget(self.table)
        temp.addWidget(self.graph)

        center_col.addLayout(temp)


        hl1 = QtWidgets.QHBoxLayout()
        hl1.addLayout(tools_col)
        hl1.addLayout(center_col)
        hl1.addLayout(tools_col2)
        self.setLayout(hl1)

        self.player_controls.sig_frame_change.connect(self.canvas.on_frame_change)
        self.player_controls.sig_frame_change.emit(0, True)

        self.player_controls2.sig_frame_change.connect(self.canvas2.on_frame_change)
        self.player_controls2.sig_frame_change.emit(0, True)

    def setup_track_edit_bar(self, tracks, scroll_area, left, select_last=False):
        """
        Initializes the track editing bar with track selectors.
        """
        if left:
            self.track_edit_bar = TrackEditLayoutBar(self, self.canvas)
            edit_bar = self.track_edit_bar
        else:
            self.track_edit_bar2 = TrackEditLayoutBar(self, self.canvas2)
            edit_bar = self.track_edit_bar2

        for i in range(tracks):
            last = i == (tracks - 1)
            select = (i == 0)
            if select_last:
                select = last
            edit_bar.add_track(index=i, select=select, last=last)

        scroll_area.setWidget(edit_bar)

    def idx_selected(self):
        """
        Returns the index of the currently selected track.
        """
        return self.track_edit_bar.idx_selected()


    def populate_table(self, rows):
        '''
        display candidates for selected track in data table
        turn on visibility for only candidate tracks
        '''

        #TODO: visibility for only candidate tracks
        #TODO: create buttons for each ID (sync videos to the "start" frame)

        self.table.setRowCount(0)

        #turn off all right tracks
        idxs = [i for i in range(self.canvas2.tracks.num_tracks)]
        self.canvas2.visuals["tracks"].set_all_track_visibilities(idxs, False)
        self.top_level_ctrls2.set_vis_toggle_state(False)

        for row_idx, row_data in enumerate(rows):
            self.table.insertRow(row_idx)


            item = QtWidgets.QTableWidgetItem(str(row_data["left_id"]))
            item.setTextAlignment(Qt.AlignCenter) 
            self.table.setItem(row_idx, 0, item)

            
            btn_plot = QtWidgets.QPushButton(str(row_data["right_id"]))
            btn_plot.clicked.connect(lambda _, l=row_data["left_id"], r = row_data["right_id"]: self.update_graph(l, r))
            self.table.setCellWidget(row_idx, 1, btn_plot)


            btn_start = QtWidgets.QPushButton(str(row_data["start"]))
            btn_start.clicked.connect(lambda _, frame_num=row_data["start"]: self.sync_frames(frame_num))
            self.table.setCellWidget(row_idx, 2, btn_start)
            
            btn_end = QtWidgets.QPushButton(str(row_data["end"]))
            btn_end.clicked.connect(lambda _, frame_num=row_data["end"]: self.sync_frames(frame_num))
            self.table.setCellWidget(row_idx, 3, btn_end)

            #only right candidates visible
            self.canvas2.visuals["tracks"].slot_set_track_vis(row_data["right_id"], True)

            #delete button
            btn_del = QtWidgets.QPushButton("Delete")
            btn_del.clicked.connect(lambda _, d=row_data: self.delete_candidate(d))

            self.table.setCellWidget(row_idx, 4, btn_del)



    def update_graph(self, left_id, right_id):
        '''
        update graph with data from tracks left_id and right_id
        '''
        try:
            y_left = self.canvas.tracks[left_id]["pos"][:, 1]
            y_right = self.canvas.tracks[right_id]["pos"][:, 1]
        except IndexError as e:
            print(f"Index Error: {e}")
            self.graph.clear()
            return

        max_len = max(len(y_left), len(y_right))
        time = np.arange(max_len)
        y_left_padded = np.pad(y_left, (0, max_len - len(y_left)))
        y_right_padded = np.pad(y_right, (0, max_len - len(y_right)))

        self.graph.update(time, y_left_padded - y_right_padded)


    def delete_candidate(self, data):
        '''
        delete candidate and refresh table
        '''
        self.canvas.candidates.delete_candidate(data)
        self.canvas.visuals["tracks"].refresh_candidate_table()

    def sync_frames(self, frame_num):
        self.player_controls.set_frame_num(frame_num)
        self.player_controls2.set_frame_num(frame_num)

    def sync_prev_state(self):
        self.player_controls.cb_first()
        self.player_controls2.cb_first()

    def sync_next_state(self):
        self.player_controls.cb_last()
        self.player_controls2.cb_last()

    def sync_forward_state(self):
        self.player_controls.cb_forward()
        self.player_controls2.cb_forward()

    def sync_back_state(self):
        self.player_controls.cb_back()
        self.player_controls2.cb_back()

    def sync_play_state(self):
        if self.dual_track_controls._playing:
            if not self.player_controls._playing:
                self.player_controls.cb_play()
            if not self.player_controls2._playing:
                self.player_controls2.cb_play()
        else:
            if self.player_controls._playing:
                self.player_controls.cb_stop()
            if self.player_controls2._playing:
                self.player_controls2.cb_stop()




    def keyPressEvent(self, event):
        #TODO: update key press events (2 vids, removed operations, etc)  


        """
        Handles keyboard shortcuts for quick GUI operations.

        Supported keys:
            Ctrl + Q       → Quit
            Ctrl + S       → Save tracks
            Ctrl + Shift + S → Save tracks with shift behavior
            Ctrl + B       → Break track
            Ctrl + L       → Link track
            Ctrl + N       → Add new track
            Ctrl + Z       → Undo
            Ctrl + Shift + Z → Redo
            Space          → Toggle play/pause
            Left Arrow     → Go to previous frame
            Right Arrow    → Go to next frame
            C              → Toggle camera overlay
            V              → Toggle visibility of main image layer
            [              → Set start of frame range
            ]              → Set end of frame range
        """
        key = event.key()
        if key == QtCore.Qt.Key_Escape:
            self.parent().fileQuit()

        c0 = event.modifiers() == QtCore.Qt.ControlModifier
        c1 = event.modifiers() == (QtCore.Qt.ShiftModifier | QtCore.Qt.ControlModifier)
        if key == QtCore.Qt.Key_Q and c0:
            self.parent().fileQuit()
        elif key == QtCore.Qt.Key_S and c0:
            self.top_level_ctrls.btn_save_tracks.animateClick()
        elif key == QtCore.Qt.Key_S and c1:
            self.top_level_ctrls.btn_save_tracks.animateShiftClick()
        elif key == QtCore.Qt.Key_B and c0:
            self.top_level_ctrls.btn_break.animateClick()
        elif key == QtCore.Qt.Key_L and c0:
            self.top_level_ctrls.btn_link.animateClick()
        elif key == QtCore.Qt.Key_N and c0:
            self.top_level_ctrls.btn_add_track.animateClick()
        elif key == QtCore.Qt.Key_Z and c0:
            self.top_level_ctrls.btn_undo.animateClick()
        elif key == QtCore.Qt.Key_Z and c1:
            self.top_level_ctrls.btn_redo.animateClick()
        elif key == QtCore.Qt.Key_Space:
            self.player_controls.toggle_play()
        elif key == QtCore.Qt.Key_Left:
            self.player_controls.decr()
        elif key == QtCore.Qt.Key_Right:
            self.player_controls.incr()
        elif key == QtCore.Qt.Key_C:
            self.canvas.toggle_cam()
        elif key == QtCore.Qt.Key_V:
            self.canvas.visuals["img"].visible ^= True
        elif key == QtCore.Qt.Key_BracketLeft:
            self.player_controls.range_slider.setFirstPosition(self.player_controls.frame_num)
            self.canvas.on_frame_change()
        elif key == QtCore.Qt.Key_BracketRight:
            self.player_controls.range_slider.setSecondPosition(self.player_controls.frame_num)
            self.canvas.on_frame_change()
