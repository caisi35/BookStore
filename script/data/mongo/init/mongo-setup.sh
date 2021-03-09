#!/bin/sh
mongorestore -h localhost --authenticationDatabase admin -u root -p root -d bookstore --dir $WORKSPACE/bookstore