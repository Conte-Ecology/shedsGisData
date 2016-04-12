#!/bin/bash
#usage: ./export_sqlite.sh <db_filepath> 
#example: ./export_sqlite.sh /conte/data/daymet/NHDHRDV2_01

DB=$1

sqlite3 $DB <<!
.mode csv
.output stdout
select * from climateRecord;
!
