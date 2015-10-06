#!/bin/bash

cd venv/lib/python2.7/site-packages/

unlink glib
unlink gobject
unlink gst-0.10
unlink gstoption.so
unlink gtk-2.0
unlink pygst.pth
unlink pygst.py
unlink pygtk.pth
unlink pygtk.py
unlink gi

ln -s /usr/lib/python2.7/site-packages/glib
ln -s /usr/lib/python2.7/site-packages/gobject
ln -s /usr/lib/python2.7/site-packages/gst-0.10
ln -s /usr/lib/python2.7/site-packages/gstoption.so
ln -s /usr/lib/python2.7/site-packages/gtk-2.0
ln -s /usr/lib/python2.7/site-packages/pygst.pth
ln -s /usr/lib/python2.7/site-packages/pygst.py
ln -s /usr/lib/python2.7/site-packages/pygtk.pth
ln -s /usr/lib/python2.7/site-packages/pygtk.py
ln -s /usr/lib/python2.7/site-packages/gi