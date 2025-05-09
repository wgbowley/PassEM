# PassEM -  Password Encrypted Manager

```
  `7MM"""Mq.                        `7MM"""YMM  `7MMM.     ,MMF'
    MM   `MM.                         MM    `7    MMMb    dPMM 
    MM   ,M9 ,6"Yb.  ,pP"Ybd ,pP"Ybd  MM   d      M YM   ,M MM 
    MMmmdM9 8    MM  8I   `" 8I   `"  MMmmMM      M  Mb  M' MM 
    MM       ,pm9MM  `YMMMa. `YMMMa.  MM   Y  ,   M  YM.P'  MM 
    MM      8M   MM  L.   I8 L.   I8  MM     ,M   M  `YM'   MM 
  .JMML.    `Moo9^Yo.M9mmmP' M9mmmP'.JMMmmmmMMM .JML. `'  .JMML
```

I made this for my Unit 3 & 4 Software Development SAT in 2024. It uses Python and is very simplistic, as only 10% of the grade came from the programming aspect.

PassEM runs in the browser using Flask. When the application starts, it logs the access URL (e.g. http://localhost:5000) to application.log. On the first launch, you must initialize the database by setting a master password. Once initialized, you'll be taken to the Vault page, where you can securely store passwords. When you're done, exiting the vault clears all decrypted data from memory. To view your stored passwords later, simply log in again using your master password.

Use the following command to install the required libraries:
```py
pip install -r requirements.txt
```
After that, the program should work.

# Possible Improvements
- The user interface isn't great, as I did all the front-end programming the day my SAT was due.
- The security of the application is questionable.