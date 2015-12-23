from ckan.lib.base import response
from ckan.controllers.package import PackageController
from ckanext.scheming.logic import (scheming_dataset_schema_list,
                                    scheming_dataset_schema_show)
from openpyxl import Workbook
from openpyxl.cell import get_column_letter
from cStringIO import StringIO


class SchemaToXlController(PackageController):
    """
    Controller for sending schema in Excel file
    """

    def dump(self):
        schema_list = sorted(scheming_dataset_schema_list({}, {}))
        workbook = Workbook()
        sheet = None
        headers = [
            'field_name',
            'multivalued',
            'fluent',
            'label_en',
            'label_fr']
        for schema_name in schema_list:
            schema = []
            schema_dict = scheming_dataset_schema_show({}, {
                'type': schema_name,
                'expanded': True
            })
            for field in schema_dict['dataset_fields']:
                schema.append({
                    'field_name': field.get('field_name'),
                    'label_en': field.get('label')['en'],
                    'label_fr': field.get('label')['fr'],
                    'multivalued': field.get('schema_multivalued'),
                    'fluent': field.get('schema_field_type') in [
                        'code',
                        'fluent']
                })
            if sheet:
                sheet = workbook.create_sheet(title=schema_name)
            else:
                sheet = workbook.active
                sheet.title = schema_name

            for i in range(1, len(headers)+1):
                cd = sheet.column_dimensions[get_column_letter(i)]
                sheet.cell(row=1, column=i, value=headers[i-1])
                cd.width = max(cd.width, len(headers[i-1]))
            row = 2
            for field in schema:
                column = 1
                for header in headers:
                    if isinstance(field[header], bool):
                        value = 'true' if field[header] else 'false'
                    else:
                        value = field[header]
                    cd = sheet.column_dimensions[get_column_letter(column)]
                    sheet.cell(row=row, column=column, value=value)
                    cd.width = max(cd.width, len(value))
                    column += 1
                row += 1
            cell = sheet['B2']
            sheet.freeze_panes = cell

        blob = StringIO()
        workbook.save(blob)
        response.headers['Content-Type'] = \
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response.headers['Content-Disposition'] = (
            'inline; filename="ProductSchemas.xlsx"')
        return blob.getvalue()
