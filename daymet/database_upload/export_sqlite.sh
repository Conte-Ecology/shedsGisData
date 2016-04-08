#!/bin/bash
sqlite3 DaymetByNENYHRDCatchments <<!
.mode csv
.output stdout
select * from climateRecord;
!
