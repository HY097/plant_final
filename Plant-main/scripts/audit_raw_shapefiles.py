"""Audit the original shapefiles.zip without third-party GIS dependencies.

Usage: python scripts/audit_raw_shapefiles.py source_data/shapefiles.zip
Counts record headers, not detailed geometry validity. Does NOT regenerate parquet.
"""
import csv
import hashlib
import io
import json
import struct
import sys
import zipfile
from collections import Counter
from pathlib import Path


def audit(path: Path):
    h=hashlib.sha256(path.read_bytes()).hexdigest()
    with zipfile.ZipFile(path) as arc:
        items=set(arc.namelist())
        shp=sorted(p for p in items if p.endswith('.shp'))
        entries=[]
        for p in shp:
            stem=p[:-4]
            if not all(stem+ext in items for ext in ('.shp','.shx','.dbf')):
                raise ValueError(f'Incomplete Shapefile: {stem}')
            dbf=arc.read(stem+'.dbf')[:32]
            if len(dbf)<32:raise ValueError(f'Bad DBF header: {stem}')
            n=struct.unpack('<I',dbf[4:8])[0]
            name=Path(stem).name
            kind='polygon' if name.startswith('poly_') else 'point' if name.startswith('pnt_') else 'unknown'
            entries.append({'file':stem,'kind':kind,'dbf_records':n})
        kind_count=Counter()
        for e in entries:kind_count[e['kind']]+=e['dbf_records']
        return {'source':str(path),'sha256':h,'shapefile_count':len(entries),
                'records_by_kind':dict(kind_count),'records_total':sum(x['dbf_records'] for x in entries),
                'note':'DBF header counts, not successful geometry/attribute reconciliation.'}


def main():
    path=Path(sys.argv[1]) if len(sys.argv)>1 else Path('source_data/shapefiles.zip')
    if not path.is_file():
        raise SystemExit(f'Raw source zip missing: {path}. Download from the original source or use the full archive.')
    print(json.dumps(audit(path),ensure_ascii=False,indent=2))

if __name__=='__main__':main()
