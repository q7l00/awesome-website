
# METHOD 1
## 1. **using app directly!**


1. find dist dir
2. cd dist
3. copy all files to ./autoCorrect2.app/Contents/Resources/
4. ./autoCorrect2.app/Contents/MacOS/autoCorrect2
5. 
   
```
Which line of data would you like to input?
3
What is the answer key?
Please type in UPPERCASE letters without space or comma.
"DBDBDDDBBBBCCACDBBDB"
```
#### ---------- !!!  in mac need add comma!! for ABCD

6. open ./autoCorrect2.app/Contents/Resources/aws.xlsx


----

# METHOD 2
## 2. manual install and run python

1. pip3 install -r requirements.txt
2. or pip install -r requirements.txt (for python2)
3. copy all xlsx to this folder
4. python autoCorrect.py

```
Which line of data would you like to input?
3
What is the answer key?
Please type in UPPERCASE letters without space or comma.
"DBDBDDDBBBBCCACDBBDB"
```



---

BTW **how to make mac app**: 

1. pip install py2app
2. cd app 
3. py2applet --make-setup autoCorrect2.py 
4. python setup.py py2app --emulate-shell-environment
5. cd dist
6. done! (refer method 1)


