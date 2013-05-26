# -*- coding: utf-8 -*-

from PyQt4 import QtGui,QtCore

TTS_ADDRESS = 'http://vaas.acapela-group.com/Services/Synthesizer'
ACCOUNT_LOGIN = ''
ACCOUNT_APP = ''
ACCOUNT_PASSWORD = ''
TTS_VOICE = 'klaus22k'

import re, subprocess, urllib
from anki.utils import stripHTML
from urllib import quote_plus
import awesometts.config as config
import awesometts.util as util
from subprocess import Popen, PIPE, STDOUT

# Prepend http proxy if one is being used.  Scans the environment for
# a variable named "http_proxy" for all operating systems
# proxy code contributted by Scott Otterson
proxies = urllib.getproxies()

if len(proxies)>0 and "http" in proxies:
  proxStr = re.sub("http:", "http_proxy:", proxies['http'])
	TTS_ADDRESS = proxStr + "/" + TTS_ADDRESS

def prepareAcapela(text, language):
	return {
            'cl_env': 'PYTHON_2.X',
            'cl_login': ACCOUNT_LOGIN,
            'cl_vers': '1-30',
            'req_voice': TTS_VOICE,
            'cl_app': ACCOUNT_APP,
            'prot_vers': '2',
            'cl_pwd': ACCOUNT_PASSWORD,
            'req_asw_type': 'STREAM',
			'req_spd':'160',
			'req_text': text,
			'req_snd_type': 'MP3'
	}	
	
def playAcapela(text, language):
	text = re.sub("\[sound:.*?\]", "", stripHTML(text.replace("\n", "")).encode('utf-8'))
	address = TTS_ADDRESS+'?' + urllib.urlencode(prepareAcapela(text, language))

	if subprocess.mswindows:
		param = ['mplayer.exe', '-ao', 'win32', '-slave', '-user-agent', "'Mozilla/5.0'", address]
		if config.subprocessing:
			subprocess.Popen(param, startupinfo=util.si, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
		else:
			subprocess.Popen(param, startupinfo=util.si, stdin=PIPE, stdout=PIPE, stderr=STDOUT).communicate()
	else:
		param = ['mplayer', '-slave', '-user-agent', "'Mozilla/5.0'", address]
		if config.subprocessing:
			subprocess.Popen(param, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
		else:
			subprocess.Popen(param, stdin=PIPE, stdout=PIPE, stderr=STDOUT).communicate()

def playfromtagAcapela(fromtag):
	for item in fromtag:
		match = re.match("(.*?):(.*)", item, re.M|re.I)
		playAcapela(match.group(2), match.group(1))

def playfromHTMLtagAcapela(fromtag):
	for item in fromtag:
		text = ''.join(item.findAll(text=True))
		voice = item['voice']
		playAcapela(text, voice)

def recordAcapela(form, text):
	return _recordAcapela(text, TTS_VOICE)

def _recordAcapela(text, language):
	text = re.sub("\[sound:.*?\]", "", stripHTML(text.replace("\n", "")).encode('utf-8'))
	address = TTS_ADDRESS+'?' + urllib.urlencode(prepareAcapela(text, language))
	
	file = util.generateFileName(text, 'acap', 'utf-8')
	if subprocess.mswindows:
		subprocess.Popen(['mplayer.exe', '-ao', 'win32', '-slave', '-user-agent', "'Mozilla/5.0'", address, '-dumpstream', '-dumpfile', file], startupinfo=util.si, stdin=PIPE, stdout=PIPE, stderr=STDOUT).wait()
		if not config.quote_mp3:
			return file.decode('utf-8')
	else:
		subprocess.Popen(['mplayer', '-slave', '-user-agent', "'Mozilla/5.0'", address, '-dumpstream', '-dumpfile', file], stdin=PIPE, stdout=PIPE, stderr=STDOUT).wait()
	return file.decode('utf-8')

def filegenerator_layout(form):
	verticalLayout = QtGui.QVBoxLayout()
	return verticalLayout

def filegenerator_run(form):
	return _recordAcapela(unicode(form.texttoTTS.toPlainText()), TTS_VOICE)

def filegenerator_preview(form):
	return playAcapela(unicode(form.texttoTTS.toPlainText()), TTS_VOICE)

TTS_service = {'acap' : {
'name': 'Acapela-Vaas',
'play' : playAcapela,
'playfromtag' : playfromtagAcapela,
'playfromHTMLtag' : playfromHTMLtagAcapela,
'record' : recordAcapela,
'filegenerator_layout': filegenerator_layout,
'filegenerator_preview': filegenerator_preview,
'filegenerator_run': filegenerator_run}}
