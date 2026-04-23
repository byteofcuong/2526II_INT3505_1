@echo off
echo ====================================================
echo TIEN HANH CHAY POSTMAN TEST TU DONG KEM BAO CAO HTML
echo ====================================================
echo.
echo Luu y: Ban can phai chay api_server/app.py hien thi tren cong 5000 truoc.
echo Yeu cau da xai: npm install -g newman newman-reporter-htmlextra
echo.
newman run collection.json -r cli,htmlextra
echo.
echo ====================================================
echo XONG! Hay vao muc newman/ de mo bao cao sinh tu dong.
pause
