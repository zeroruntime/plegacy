import os
import tempfile
from datetime import datetime
from io import BytesIO

import pandas as pd
from PIL import Image
from django.http import HttpResponse


def create_thumbnail(image_path, size=(100, 100)):
    """Create a thumbnail of the image and return the path to the thumbnail"""
    try:
        with Image.open(image_path) as img:
            # Convert to RGB if necessary (for PNG with transparency)
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            
            # Create thumbnail
            img.thumbnail(size, Image.Resampling.LANCZOS)
            
            # Create temporary file with proper extension
            temp_dir = tempfile.gettempdir()
            base_name = os.path.splitext(os.path.basename(image_path))[0]
            thumbnail_path = os.path.join(temp_dir, f"thumb_{base_name}.jpg")
            
            img.save(thumbnail_path, 'JPEG', quality=85)
            return thumbnail_path
            
    except Exception as e:
        print(f"Error creating thumbnail for {image_path}: {e}")
        return None


def is_image_file(file_path):
    """Check if the file is an image"""
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
    return any(file_path.lower().endswith(ext) for ext in image_extensions)


def create_images_sheet(workbook, queryset, sheet_name, field_name):
    """Create a separate sheet with full-size images"""
    worksheet = workbook.add_worksheet(sheet_name)
    
    # Add headers
    header_format = workbook.add_format({
        'bold': True,
        'text_wrap': True,
        'valign': 'top',
        'fg_color': '#D7E4BC',
        'border': 1
    })
    
    worksheet.write(0, 0, 'Student Name', header_format)
    worksheet.write(0, 1, 'BECE Index', header_format)
    worksheet.write(0, 2, 'Image', header_format)
    
    # Set column widths
    worksheet.set_column(0, 0, 25)  # Name column
    worksheet.set_column(1, 1, 20)  # Index column  
    worksheet.set_column(2, 2, 30)  # Image column
    
    row = 1
    for admission in queryset:
        file_field = getattr(admission, field_name, None)
        
        if file_field and os.path.exists(file_field.path):
            # Write student info
            worksheet.write(row, 0, admission.full_name)
            worksheet.write(row, 1, admission.bece_index_number)
            
            # Insert full-size image (scaled down to fit)
            try:
                if is_image_file(file_field.path):
                    # Set row height for larger images
                    worksheet.set_row(row, 200)  # Adjust height as needed
                    
                    worksheet.insert_image(row, 2, file_field.path, {
                        'x_scale': 0.3,  # Adjust scale as needed
                        'y_scale': 0.3,
                        'object_position': 1  # Position relative to cell
                    })
                else:
                    worksheet.write(row, 2, f"File: {os.path.basename(file_field.path)}")
                    
            except Exception as e:
                worksheet.write(row, 2, f"Error loading image: {str(e)}")
                print(f"Error adding image for {admission.full_name}: {e}")
            
            row += 1


def export_to_excel(queryset):
    """Export admission records to detailed Excel file with thumbnails and images"""
    temp_thumbnails = []

    # Convert queryset to pandas DataFrame
    data = []
    for idx, admission in enumerate(queryset, start=1):  # start=1 for 1-based indexing
        data.append({
            'No': idx,
            'Full Name': admission.full_name,
            'Date of Birth': admission.date_of_birth,
            'Gender': admission.get_gender_display(),
            'Nationality': admission.nationality,
            'Previous School': admission.previous_school,
            'Class Completed': admission.class_completed,
            'BECE Index Number': admission.bece_index_number,
            'BECE Year': admission.bece_year,
            'Aggregate Score': admission.aggregate_score,
            'Program Applied': admission.program_applied_for,
            'Accommodation Status': admission.get_accommodation_status_display(),
            
            # Section B: Parent/Guardian Information
            'Parent/Guardian Name': admission.parent_name,
            'Relationship to Applicant': admission.parent_relationship,
            'Parent Occupation': admission.parent_occupation,
            'Parent Phone': admission.parent_contact,
            'Parent Address': admission.parent_address,
            'Parent Email': admission.parent_email,
            
            # Section C: Alumni Sponsorship Details
            'Alumni Name': admission.alumni_name,
            'Alumni Year Group': admission.alumni_year_group,
            'Alumni Class Stream': admission.alumni_class_stream,
            'Alumni House': admission.alumni_house,
            'Alumni Phone': admission.alumni_phone,
            'Alumni Email': admission.alumni_email,
            'Alumni Occupation': admission.alumni_occupation,
            'Alumni Organization': admission.alumni_organization,
            'Alumni Relationship': admission.alumni_relationship,
            'Recommendation Reason': admission.reason_for_recommendation,
            
            # Attachment columns
            'Birth Certificate': 'Attached' if admission.birth_certificate else 'Not Attached',
            'Passport Photo': 'Attached' if admission.passport_photo else 'Not Attached',
            'BECE Results': 'Attached' if admission.bece_results else 'Not Attached',
            
            # Metadata
            'Submitted At': admission.date_submitted.strftime("%Y-%m-%d %H:%M"),
        })
 
    
    df = pd.DataFrame(data)

    # Add current date to filename
    today = datetime.now()
    
    
    # Create HTTP response with Excel file
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="protocol_admissions_{today.strftime("%Y%m%d")}.xlsx"'
    
    with pd.ExcelWriter(response, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Protocol Admissions', index=False)
        
        # Get the xlsxwriter workbook and worksheet objects
        workbook = writer.book
        worksheet = writer.sheets['Protocol Admissions']
        
        # Add formatting
        header_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'fg_color': '#D7E4BC',
            'border': 1
        })
        
        # Write the column headers with the defined format
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
        
        # Auto-adjust columns' width
        for column in df:
            column_length = max(df[column].astype(str).map(len).max(), len(column))
            col_idx = df.columns.get_loc(column)
            worksheet.set_column(col_idx, col_idx, column_length + 2)
        
        # Add images as thumbnails in the main sheet
        row_num = 1  # Start from row 1 (after headers)
        
        # Find the column positions for all three attachment columns
        birth_cert_col = df.columns.get_loc('Birth Certificate')
        passport_col = df.columns.get_loc('Passport Photo')
        bece_col = df.columns.get_loc('BECE Results')
        
        # Set row height for image thumbnails (in pixels, roughly)
        worksheet.set_default_row(80)  # Increase row height for thumbnails
        
        # Set column widths for attachment columns to accommodate thumbnails
        worksheet.set_column(birth_cert_col, birth_cert_col, 15)
        worksheet.set_column(passport_col, passport_col, 15)
        worksheet.set_column(bece_col, bece_col, 15)
        
        for admission in queryset:
            # Add birth certificate thumbnail
            if admission.birth_certificate and os.path.exists(admission.birth_certificate.path):
                try:
                    if is_image_file(admission.birth_certificate.path):
                        thumbnail_path = create_thumbnail(admission.birth_certificate.path, (60, 75))
                        if thumbnail_path:
                            worksheet.insert_image(row_num, birth_cert_col, thumbnail_path,
                                                 {'x_scale': 1.0, 'y_scale': 1.0, 'object_position': 1})
                            temp_thumbnails.append(thumbnail_path) 
                except Exception as e:
                    print(f"Error adding birth certificate for {admission.full_name}: {e}")
            
            # Add passport photo thumbnail
            if admission.passport_photo and os.path.exists(admission.passport_photo.path):
                try:
                    # Create thumbnail
                    thumbnail_path = create_thumbnail(admission.passport_photo.path, (60, 75))
                    if thumbnail_path:
                        worksheet.insert_image(row_num, passport_col, thumbnail_path, 
                                             {'x_scale': 1.0, 'y_scale': 1.0, 'object_position': 1})
                        # Clean up temporary thumbnail
                        temp_thumbnails.append(thumbnail_path) 
                except Exception as e:
                    print(f"Error adding passport photo for {admission.full_name}: {e}")
            
            # Add BECE results thumbnail
            if admission.bece_results and os.path.exists(admission.bece_results.path):
                try:
                    if is_image_file(admission.bece_results.path):
                        thumbnail_path = create_thumbnail(admission.bece_results.path, (60, 75))
                        if thumbnail_path:
                            worksheet.insert_image(row_num, bece_col, thumbnail_path,
                                                 {'x_scale': 1.0, 'y_scale': 1.0, 'object_position': 1})
                            temp_thumbnails.append(thumbnail_path) 
                except Exception as e:
                    print(f"Error adding BECE results for {admission.full_name}: {e}")
            
            row_num += 1
        
        # Create separate sheets for full-size images
        create_images_sheet(workbook, queryset, 'Passport Photos', 'passport_photo')
        create_images_sheet(workbook, queryset, 'Birth Certificates', 'birth_certificate')
        create_images_sheet(workbook, queryset, 'BECE Results', 'bece_results')

    for thumb in temp_thumbnails:
        if os.path.exists(thumb):
            os.remove(thumb)

    return response


def export_summary_to_excel(queryset):
    """Export a summary of admission records to Excel"""
    # Prepare simplified data
    data = []
    for idx, admission in enumerate(queryset, start=1):
        data.append({
            'No': idx,
            'Applicant Name': admission.full_name,
            'Index No.': admission.bece_index_number,
            'Grade': admission.aggregate_score,
            'Old Boy Name': admission.alumni_name,
            'Old Boy Year Group': admission.alumni_year_group,
        })

    # Convert to DataFrame
    df = pd.DataFrame(data)

    # Add current date to filename
    today = datetime.now()

    # Create HTTP response with Excel file
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="admission_summary_{today.strftime("%Y%m%d")}.xlsx"'

    with pd.ExcelWriter(response, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Summary', index=False)

        # Formatting
        workbook = writer.book
        worksheet = writer.sheets['Summary']

        header_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'fg_color': '#D7E4BC',
            'border': 1
        })

        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)

        for column in df:
            column_length = max(df[column].astype(str).map(len).max(), len(column))
            col_idx = df.columns.get_loc(column)
            worksheet.set_column(col_idx, col_idx, column_length + 2)

    return response
