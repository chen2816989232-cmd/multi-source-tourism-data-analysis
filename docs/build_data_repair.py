"""Audit dump row arities and build an additive scenic table repair."""
import re
from pathlib import Path

root = Path(__file__).resolve().parents[1]
dump = (root / 'db/lvxing2f63wq5x.sql').read_text(encoding='utf-8')
schemas = {}
for match in re.finditer(r'CREATE TABLE `([^`]+)` \((.*?)\n\)', dump, re.S):
    schemas[match[1]] = re.findall(r'^  `([^`]+)`', match[2], re.M)

def arities(values):
    quoted = escaped = False
    depth = fields = 0
    counts = []
    for char in values:
        if escaped:
            escaped = False
        elif quoted and char == '\\':
            escaped = True
        elif char == "'":
            quoted = not quoted
        elif not quoted:
            if char == '(':
                depth += 1
                if depth == 1:
                    fields = 1
            elif char == ',' and depth == 1:
                fields += 1
            elif char == ')':
                depth -= 1
                if depth == 0:
                    counts.append(fields)
    assert not quoted and depth == 0
    return counts

repairs = []
for match in re.finditer(r'^INSERT INTO `([^`]+)`(?: \(([^\n]*?)\))? VALUES (.*?);\n(?=(?:/\*!|INSERT INTO|UNLOCK))', dump, re.M | re.S):
    table, values = match[1], match[3].rstrip('\r')
    counts = arities(values)
    cols = re.findall(r'`([^`]+)`', match[2]) if match[2] else list(schemas[table])
    print(table, 'schema columns', len(cols), 'row columns', sorted(set(counts)), 'rows', len(counts))
    if table == 'T_Core_attractions':
        cols.insert(2, 'poiname')
    elif set(counts) != {len(cols)}:
        raise ValueError('Unexpected malformed table: ' + table)
    else:
        continue
    assert set(counts) == {len(cols)}, table
    repairs.append('INSERT IGNORE INTO `' + table + '` (' + ','.join('`'+c+'`' for c in cols) + ') VALUES ' + values + ';')

assert len(repairs) == 1
header = """-- Additive repair: existing primary keys are preserved; no DROP, DELETE or TRUNCATE.
SET NAMES utf8mb4;
SET @repair_sql = IF((SELECT COUNT(*) FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='T_Core_attractions' AND COLUMN_NAME='poiname')=0, 'ALTER TABLE `T_Core_attractions` ADD COLUMN `poiname` VARCHAR(255) DEFAULT NULL AFTER `addtime`', 'SELECT 1');
PREPARE repair_stmt FROM @repair_sql;
EXECUTE repair_stmt;
DEALLOCATE PREPARE repair_stmt;
"""
out = root / '.deploy-artifacts/repair-missing-tourism-data.sql'
out.write_text(header + '\n'.join(repairs) + '\n', encoding='utf-8')
print('Repair file:', out)
