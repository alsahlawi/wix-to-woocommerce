import pandas as pd
from bs4 import BeautifulSoup

BASE_IMAGE_URL = "https://static.wixstatic.com/media/"

def clean_html(html):
    """Remove HTML tags from description"""
    if pd.isna(html):
        return ''
    return BeautifulSoup(html, 'html.parser').get_text()

def process_images(image_str):
    """Convert Wix image names to full URLs"""
    if pd.isna(image_str):
        return '', ''
    urls = [f"{BASE_IMAGE_URL}{img.strip()}" for img in image_str.split(';')]
    return urls[0], ','.join(urls[1:]) if len(urls) > 1 else ''

def process_wix_to_woocommerce(input_file, output_file):
    # Read Wix CSV
    df = pd.read_csv(input_file)
    
    # Group products by handleId
    grouped = df.groupby('handleId')
    
    wc_products = []
    
    for handle_id, group in grouped:
        main_product = group[group['fieldType'] == 'Product'].iloc[0]
        variants = group[group['fieldType'] == 'Variant']
        
        # Process images
        main_image, additional_images = process_images(main_product['productImageUrl'])
        
        # Common product data
        product_data = {
            'Type': 'variable' if len(variants) > 0 else 'simple',
            'SKU': main_product['sku'],
            'Name': main_product['name'],
            'Published': 1 if main_product['visible'] else 0,
            'Is featured?': 0,
            'Visibility in catalog': 'visible' if main_product['visible'] else 'hidden',
            'Short description': clean_html(main_product['description']),
            'Description': '',
            'Regular price': main_product['price'],
            'Categories': main_product['collection'],
            'Images': main_image,
            'Additional images': additional_images,
            'Attribute 1 name': '',
            'Attribute 1 value(s)': '',
            'Attribute 1 visible': 1,
            'Attribute 1 global': 1,
        }
        
        # Handle variants and attributes
        attributes = []
        for i in range(1, 7):
            opt_name = main_product.get(f'productOptionName{i}', '')
            if pd.notna(opt_name) and opt_name != '':
                attr_values = []
                for variant in variants.itertuples():
                    variant_value = getattr(variant, f'productOptionName{i}', '')
                    if pd.notna(variant_value):
                        attr_values.append(variant_value)
                
                if attr_values:
                    attributes.append({
                        'name': opt_name,
                        'values': list(set(attr_values)),
                        'visible': True
                    })
        
        # Add attributes to product data
        for idx, attr in enumerate(attributes[:2], start=1):
            product_data[f'Attribute {idx} name'] = attr['name']
            product_data[f'Attribute {idx} value(s)'] = '|'.join(attr['values'])
        
        wc_products.append(product_data)
        
        # Add variants if exists
        if len(variants) > 0:
            for variant in variants.itertuples():
                variant_data = {
                    'Type': 'variation',
                    'Parent': main_product['sku'],
                    'SKU': getattr(variant, 'sku', ''),
                    'Regular price': variant.price if pd.notna(variant.price) else main_product['price'],
                    'Stock': variant.inventory if pd.notna(variant.inventory) else main_product['inventory'],
                    'Attribute 1 value(s)': getattr(variant, 'productOptionName1', ''),
                    'Attribute 2 value(s)': getattr(variant, 'productOptionName2', '')
                }
                wc_products.append({**product_data, **variant_data})
    
    # Convert to DataFrame and reorder columns
    wc_df = pd.DataFrame(wc_products)
    
    # Select and order WooCommerce columns
    columns = [
        'Type', 'SKU', 'Name', 'Published', 'Is featured?', 'Visibility in catalog',
        'Short description', 'Description', 'Regular price', 'Categories', 'Images',
        'Additional images', 'Attribute 1 name', 'Attribute 1 value(s)', 
        'Attribute 1 visible', 'Attribute 1 global', 'Attribute 2 name',
        'Attribute 2 value(s)', 'Attribute 2 visible', 'Attribute 2 global',
        'Parent', 'Stock'
    ]
    
    wc_df = wc_df.reindex(columns=columns)
    
    # Save to CSV
    wc_df.to_csv(output_file, index=False)

# Usage
process_wix_to_woocommerce('catalog_products.csv', 'woocommerce_products.csv')
