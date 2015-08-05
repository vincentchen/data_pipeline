# -*- coding: utf-8 -*-
"""
This script will create a JSON version of the Google Spreadsheet schema reference.

Google Spreadsheet:
https://docs.google.com/spreadsheets/d/1ZIE8UdMadTgBpcELOnGLNJIhOLXBsij0_f5BiwlAQss/edit#gid=8

Usage:
    1. download sheets as csvs from the Google Spreadsheet into the same directory as this script
        - ref_cols.csv          Sheet 1 ("DW Schema Reference")
        - ref_tables.csv        Sheet 2 ("DW Tables")
    2. download BAM's listings of table owners into the same directory as this script
        - ref_owners.csv        Original Version
        - ref_owners_new.csv    Updated Version
    3. run the script and the output will be in schema_ref.json
"""
import csv
import json


if __name__ == '__main__':

    owners_file = open('ref_owners.csv', 'rb')
    owners_new_file = open('ref_owners_new.csv', 'rb')
    tables_file = open('ref_tables.csv', 'rb')
    cols_file = open('ref_cols.csv', 'rb')

    owners_rows, owners_new_rows, tables_rows, cols_rows = [], [], [], []

    reader = csv.reader(owners_file)
    for row in reader:
        owners_rows.append(row)
    reader = csv.reader(owners_new_file)
    for row in reader:
        owners_new_rows.append(row)
    reader = csv.reader(tables_file)
    for row in reader:
        tables_rows.append(row)
    reader = csv.reader(cols_file)
    for row in reader:
        cols_rows.append(row)

    tables_rows = tables_rows[1:]

    output = {
        'doc_source': 'https://docs.google.com/spreadsheets/d/1ZIE8UdMadTgBpcELOnGLNJIhOLXBsij0_f5BiwlAQss/edit#gid=11',
        'doc_owner': 'bam@yelp.com',
        'docs': []
    }

    for row in tables_rows:

        schema, name, category, description, _, _, notes, _ = row
        table_output = {
            'namespace': schema + '_v1',
            'source': name,
            'doc': description,
            'note': notes,
            'category': category,
            'fields': []
        }

        owner_row = filter(lambda row: row[3] == name, owners_rows)
        owner_new_row = filter(lambda row: row[3] == name, owners_new_rows)

        try:
            _, source_path, _, _, _, owner = owner_row.pop()
            owner = owner.split(',')[0]

            table_output['owner_email'] = owner
            table_output['file_display'] = source_path
            table_output['file_url'] = 'https://opengrok.yelpcorp.com/xref/yelp-main/' + source_path

        except IndexError:

            if len(owner_new_row) > 0:

                _, source_path, _, _, _, owner = owner_new_row.pop()
                owner = owner.split(',')[0]

                table_output['owner_email'] = owner
                table_output['file_display'] = source_path
                table_output['file_url'] = 'https://opengrok.yelpcorp.com/xref/yelp-main/' + source_path

            else:

                table_output['owner_email'] = ''
                table_output['file_display'] = ''
                table_output['file_url'] = ''

        col_rows = filter(lambda row: row[0] == schema and row[1] == name, cols_rows)

        for row in col_rows:

            _, _, col_name, pos, _, nullable, write_once, data_type, _, _, _, _, description, _, notes = row

            if nullable == 'NO':
                data_type += ' not null'
            if write_once == 'YES':
                data_type += ' write once'

            if notes.strip() == '0':
                notes = ''

            col_output = {
                'name': col_name,
                'doc': description,
                'note': notes,
            }
            table_output['fields'].append(col_output)

        output['docs'].append(table_output)

    out_file = open('schema_ref.json', 'wb')
    out_file.write(json.dumps(output))
    out_file.close()

