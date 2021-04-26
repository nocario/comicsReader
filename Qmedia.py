from PyQt5 import QtCore, QtWidgets, QtMultimedia
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton
import os
from pathlib import Path


class MyWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('')
        self.musique_position = 0
        self.label = QLabel('')

        self.musique_liste = list(Path(Path.cwd() / 'MusicMixer').rglob('*.mp3'))
        self.playlist = QtMultimedia.QMediaPlaylist()

        self.mplPlayer = QtMultimedia.QMediaPlayer()
        self.mplPlayer.setVolume(50)
        self.mplPlayer.mediaStatusChanged.connect(self.init_player)
        self.mplPlayer.stateChanged.connect(self.set_player_state)

        self.btnOpen = QtWidgets.QPushButton('start playlist')
        self.btnPlay = QtWidgets.QPushButton('play')
        self.btnPause = QtWidgets.QPushButton('pause')
        self.btnStop = QtWidgets.QPushButton('stop')
        self.btnMute = QtWidgets.QPushButton('Mute!')
        self.btnPrevious = QPushButton('previous')
        self.btnNext = QPushButton('next')

        self.btnOpen.setFixedHeight(100)
        self.btnPlay.setFixedHeight(100)
        self.btnPause.setFixedHeight(100)
        self.btnStop.setFixedHeight(100)
        self.btnPrevious.setFixedHeight(100)
        self.btnNext.setFixedHeight(100)

        self.btnOpen.clicked.connect(self.open_file)
        self.btnPlay.clicked.connect(self.mplPlayer.play)
        self.btnPause.clicked.connect(self.mplPlayer.pause)
        self.btnStop.clicked.connect(self.mplPlayer.stop)
        self.btnMute.toggled.connect(self.mplPlayer.setMuted)
        self.btnPrevious.clicked.connect(self.previous)
        self.btnPrevious.setEnabled(False)
        self.btnNext.clicked.connect(self.next)
        self.btnNext.setEnabled(False)

        self.btnPlay.setEnabled(False)
        self.btnPause.setEnabled(False)
        self.btnStop.setEnabled(False)
        self.btnMute.setCheckable(True)

        lblVolume = QtWidgets.QLabel('Volume')
        sldVolume = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        sldVolume.setTickPosition(QtWidgets.QSlider.TicksAbove)
        sldVolume.setRange(0, 100)
        sldVolume.setTickInterval(10)
        sldVolume.setValue(50)
        lblVolume.setBuddy(sldVolume)
        sldVolume.valueChanged.connect(self.mplPlayer.setVolume)

        hbox1 = QtWidgets.QHBoxLayout()
        hbox2 = QtWidgets.QHBoxLayout()
        hbox3 = QtWidgets.QHBoxLayout()

        hbox1.addWidget(self.btnPlay)
        hbox1.addWidget(self.btnPause)
        hbox1.addWidget(self.btnStop)
        hbox2.addWidget(lblVolume)
        hbox2.addWidget(sldVolume)
        hbox2.addWidget(self.btnMute)
        hbox3.addWidget(self.btnPrevious)
        hbox3.addWidget(self.btnNext)

        vbox = QtWidgets.QVBoxLayout()

        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)
        vbox.addLayout(hbox3)

        vbox.addWidget(self.btnOpen)
        vbox.addWidget(self.label)
        self.setLayout(vbox)

    def open_file(self):
        if len(self.musique_liste) > 0:
            self.btnOpen.setEnabled(False)
            self.mplPlayer.setPlaylist(self.playlist)
            for musique in self.musique_liste:
                self.playlist.addMedia(QtMultimedia.QMediaContent(QtCore.QUrl("MusicMixer/"+musique.name)))
            self.mplPlayer.playlist().setCurrentIndex(self.musique_position)
            self.label.setText(self.musique_liste[self.musique_position].name)
            self.mplPlayer.play()

    def init_player(self, state):
        if state == QtMultimedia.QMediaPlayer.LoadedMedia:
            self.mplPlayer.stop()
            self.btnPlay.setEnabled(True)
            self.btnPause.setEnabled(False)
        elif state == QtMultimedia.QMediaPlayer.EndOfMedia:
            self.musique_position += 1
            if self.musique_position == len(self.musique_liste):
                self.musique_position = 0
            self.label.setText(self.musique_liste[self.musique_position].name)
            self.mplPlayer.playlist().setCurrentIndex(self.musique_position)
        elif state == QtMultimedia.QMediaPlayer.NoMedia or state == QtMultimedia.QMediaPlayer.InvalidMedia:
            self.btnPlay.setEnabled(False)
            self.btnPause.setEnabled(False)
            self.btnStop.setEnabled(False)

    def set_player_state(self, state):
        if state == QtMultimedia.QMediaPlayer.StoppedState:
            self.btnPlay.setEnabled(True)
            self.btnPause.setEnabled(False)
            self.btnStop.setEnabled(False)
        elif state == QtMultimedia.QMediaPlayer.PlayingState:
            self.btnPlay.setEnabled(False)
            self.btnPause.setEnabled(True)
            self.btnStop.setEnabled(True)
            self.btnPrevious.setEnabled(True)
            self.btnNext.setEnabled(True)
        elif state == QtMultimedia.QMediaPlayer.PausedState:
            self.btnPlay.setEnabled(True)
            self.btnPause.setEnabled(False)
            self.btnStop.setEnabled(True)

    def next(self):
        self.musique_position += 1
        if self.musique_position == len(self.musique_liste):
            self.musique_position = 0
        self.label.setText(self.musique_liste[self.musique_position].name)
        self.mplPlayer.playlist().setCurrentIndex(self.musique_position)

    def previous(self):
        self.musique_position -= 1
        if self.musique_position == -1:
            self.musique_position = len(self.musique_liste) - 1
        self.label.setText(self.musique_liste[self.musique_position].name)
        self.mplPlayer.playlist().setCurrentIndex(self.musique_position)
