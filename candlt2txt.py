#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import re

dlt_id = 0x1fffffff
do_binfile = 0

sn = [0x41, 0x00, 0x01, 0x82]
snLen = len(sn)
idx = 0
skipBytes = 0
toSkip = 5

if len(sys.argv) > 1  :
	textdata = ''
	bindata = b''
	dlt_id_txt = format(dlt_id, 'x')
	dreg = '( [0-9A-Fa-f]{2}){8}'
	in_fname = sys.argv[1:2][0]
	fname, _ = in_fname.rsplit('.')
	out_fname = fname + '_log.txt'
	out_fname_bin = fname + '_data.bin'

	with open(in_fname, 'r') as f:
		for li in f:
			if dlt_id_txt in li.lower():
				match = re.search(dreg, li)
				if match :
					for b in match.group(0).split(' '):
						if b :
							c = int(b, 16)
							if do_binfile :
								bindata += bytes.fromhex(b)

							if skipBytes == 0 :
								if c != sn[idx] :
									idx = 0
								else :
									idx += 1
									if idx == snLen :
										skipBytes = toSkip
										line = ''
										idx = 0
							elif skipBytes > 1 :
								skipBytes -= 1
							elif skipBytes == 1 :
								if c != 0 :
									line += chr(c)
								else :
									print(line)
									skipBytes = 0
									textdata += line + '\n'

	size = len(textdata)
	if size > 0 :
		print('\nConvert '+in_fname+' to '+out_fname+' '+str(size)+' bytes')

		f = open(out_fname, 'w', encoding='utf-8')
		f.write(textdata)
		f.close()
	else:
		print('\nNo data to convert')

	size = len(bindata)
	if do_binfile and size > 0 :
		print()
		print('\nSave binary file'+out_fname_bin+' '+str(size)+' bytes')

		f = open(out_fname_bin, 'wb')
		f.write(bindata)
		f.close()
else:
	print('No filename is given, trying receive over can0 interface\n')
	import can

	with can.Bus(channel='can0', interface='socketcan') as bus :
		line = ''
		skipBytes = 0
		while 1 :
			msg = bus.recv()
			if msg.arbitration_id == dlt_id :
				for c in msg.data :
					if skipBytes == 0 :
						if c != sn[idx] :
							idx = 0
						else :
							idx += 1
							if idx == snLen :
								skipBytes = toSkip
								line = ''
								idx = 0
					elif skipBytes > 1 :
						skipBytes -= 1
					else :
						if c != 0 :
							line += chr(c)
						else :
							print(line)
							skipBytes = 0
							line = ''
