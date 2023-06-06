@chcp 1251
cd sqlite-tools-win32-x86-3400100
echo UPDATE 'wallet' SET 'balance' = 'balance' + %2 WHERE 'squad' = %1; > "1.sql"
sqlite3 "D:\projects\vympel.music\database.db" ".read 1.sql"
cd ..