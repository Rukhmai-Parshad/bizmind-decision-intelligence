from django.db import transaction
from sales.models import SalesRecord
from sales.csv import process_sales_csv
from decisions.engine import generate_decisions


def process_sales_dataset(dataset):
    if dataset.type != 'sales' or dataset.is_processed:
        return
    
    if SalesRecord.objects.filter(dataset=dataset).exists():
        return


    try:
        with transaction.atomic():
            df = process_sales_csv(dataset.file.path)

            SalesRecord.objects.bulk_create([
                SalesRecord(
                    dataset=dataset,
                    date=row['date'],
                    product=row['product'],
                    region=row['region'],
                    units_sold=row['units_sold'],
                    unit_price=row['unit_price'],
                    revenue=row['revenue'],
                )
                for _, row in df.iterrows()
            ])

            dataset.is_processed = True
            dataset.error_message = None
            dataset.save(update_fields=['is_processed', 'error_message'])

        generate_decisions(dataset)

    except Exception as e:
        dataset.error_message = str(e)
        dataset.save(update_fields=['error_message'])
        raise
