# syno-filestat

Filter Synology file transfer logs and report most accessed files and statistics for user, by month.

```
$ python3.7 report.py -h
usage: report.py [-h] [-u USER] [-m MONTH] [-y YEAR] CSV [CSV ...]

Process Synology File Transfer Logs

positional arguments:
  CSV         CSV Export of the File Transfer Log

optional arguments:
  -h, --help  show this help message and exit
  -u USER     User to analyze
  -m MONTH    Month to analyze of current year [1-12]
  -y YEAR     Year to analyze of current year [e.g. 2019]
```

