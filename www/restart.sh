#/bin/sh

cd /var/www/jianhu/www/
kill -9 `cat /tmp/www_uwsgi_master.pid`
sleep 1
uwsgi socket.ini
