#! /bin/bash
mongorestore -h localhost --authenticationDatabase admin -u root -p root -d bookstore --dir /code/script/data/bookstore
