#!/bin/sh
systemctl daemon-reload
systemctl enable sofia_read
systemctl enable sofia_write
