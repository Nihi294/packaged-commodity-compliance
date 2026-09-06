import pytesseract
from PIL import Image
import os
import cv2
import re
from collections import defaultdict

# ─────────────────────────────────────────────
# SETUP
# ─────────────────────────────────────────────

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

folder_path = os.path.dirname(os.path.abspath(__file__))

SUPPORTED = ('.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff', '.tif', '.jfif')

# ─────────────────────────────────────────────
# STEP 1: IMAGE CLEANING
# ─────────────────────────────────────────────

def clean_image(image_path):
    img = cv2.imread(image_path)
    img = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    return thresh

# ─────────────────────────────────────────────
# STEP 2: GROUP IMAGES BY PRODUCT NAME
# ─────────────────────────────────────────────

def group_images():
    products = defaultdict(list)

    for filename in os.listdir(folder_path):
        if not filename.lower().endswith(SUPPORTED):
            continue
        if filename.startswith('cleaned_'):
            continue

        # Split by last underscore to get product name
        # dettol_front.jpg → product = "dettol", part = "front"
        name_without_ext = os.path.splitext(filename)[0]

        if '_' in name_without_ext:
            product_name = '_'.join(name_without_ext.split('_')[:-1])
        else:
            # No underscore — treat whole name as product
            product_name = name_without_ext

        products[product_name].append(filename)

    return products

# ─────────────────────────────────────────────
# STEP 3: EXTRACT TEXT FROM ALL IMAGES OF ONE PRODUCT
# ─────────────────────────────────────────────

def extract_merged_text(filenames):
    merged_text = ""

    for filename in filenames:
        image_path = os.path.join(folder_path, filename)

        # Clean image
        cleaned = clean_image(image_path)

        # Save cleaned version
        clean_path = os.path.join(folder_path, 'cleaned_' + filename)
        cv2.imwrite(clean_path, cleaned)

        # Extract text
        text = pytesseract.image_to_string(Image.open(clean_path))

        print(f"    → Extracted from {filename}: {len(text.strip())} characters")

        merged_text += f"\n--- From {filename} ---\n" + text

    return merged_text

# ─────────────────────────────────────────────
# STEP 4: COMPLIANCE CHECKER
# ─────────────────────────────────────────────

def check_compliance(text):
    results = {}

    # 1. Manufacturer name and address
    manufacturer = re.search(
        r'(manufactured|mfg|packed|marketed|imported)\s*(by)?[\s:]+[A-Za-z]',
        text, re.IGNORECASE
    )
    results['Manufacturer / Packer Name & Address'] = {
        'status': 'PASS' if manufacturer else 'FAIL',
        'rule': 'Rule 6(1)(a)',
        'found': manufacturer.group() if manufacturer else 'Not found'
    }

    # 2. Product name
    first_line = text.strip().split('\n')[0]
    results['Product Name'] = {
        'status': 'PASS' if len(first_line) > 2 else 'FAIL',
        'rule': 'Rule 6(1)(b)',
        'found': first_line if len(first_line) > 2 else 'Not found'
    }

    # 3. Net quantity
    net_qty = re.search(
        r'(net\s*)?(weight|qty|quantity|content|vol|volume)?[\s:]*'
        r'(\d+\.?\d*)\s*(g|gm|gms|gram|kg|ml|l|litre|liter|pcs|pieces|units|tablets|tabs|nos)',
        text, re.IGNORECASE
    )
    results['Net Quantity'] = {
        'status': 'PASS' if net_qty else 'FAIL',
        'rule': 'Rule 6(1)(c)',
        'found': net_qty.group() if net_qty else 'Not found'
    }

    # 4. Mfg date
    mfg_date = re.search(
        r'(mfg|manufactured|mfd|dom|date of mfg|packing|packed)[\s.:]*'
        r'(\d{2}[\/\-]\d{4}|\d{2}[\/\-]\d{2}[\/\-]\d{4}|'
        r'(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*[\s\-\/]*\d{4})',
        text, re.IGNORECASE
    )
    results['Month & Year of Manufacture'] = {
        'status': 'PASS' if mfg_date else 'FAIL',
        'rule': 'Rule 6(1)(d)',
        'found': mfg_date.group() if mfg_date else 'Not found'
    }

    # 5. MRP
    mrp = re.search(
        r'(mrp|m\.r\.p|maximum retail price|retail price)[\s.:]*'
        r'(rs\.?|inr|₹)?\s*(\d+[\.,]?\d*)',
        text, re.IGNORECASE
    )
    results['MRP / Retail Sale Price'] = {
        'status': 'PASS' if mrp else 'FAIL',
        'rule': 'Rule 6(1)(e)',
        'found': mrp.group() if mrp else 'Not found'
    }

    # 6. Expiry date
    expiry = re.search(
        r'(exp|expiry|expiration|best before|use before|bb|use by)[\s.:]*'
        r'(\d{2}[\/\-]\d{4}|\d{2}[\/\-]\d{2}[\/\-]\d{4}|'
        r'(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*[\s\-\/]*\d{4})',
        text, re.IGNORECASE
    )
    results['Expiry / Best Before Date'] = {
        'status': 'PASS' if expiry else 'WARNING',
        'rule': 'Rule 6(1)(d)',
        'found': expiry.group() if expiry else 'Not found — may not apply to all products'
    }

    # 7. Consumer complaint contact
    phone = re.search(
        r'(\+91[\s\-]?)?(\d{10}|\d{3}[\s\-]\d{3}[\s\-]\d{4}|1800[\s\-]?\d+)',
        text
    )
    results['Consumer Complaint Contact'] = {
        'status': 'PASS' if phone else 'FAIL',
        'rule': 'Rule 6(2)',
        'found': phone.group() if phone else 'Not found'
    }

    # 8. FSSAI number
    fssai = re.search(
        r'(fssai|lic\.?\s*no\.?|license\s*no\.?)[\s:]*(\d{14})',
        text, re.IGNORECASE
    )
    results['FSSAI License Number'] = {
        'status': 'PASS' if fssai else 'WARNING',
        'rule': 'FSSAI Act',
        'found': fssai.group() if fssai else 'Not found — required only for food products'
    }

    return results

# ─────────────────────────────────────────────
# STEP 5: PRINT REPORT
# ─────────────────────────────────────────────

def print_report(product_name, filenames, text, compliance):
    print(f"\n{'='*55}")
    print(f"  PRODUCT : {product_name.upper()}")
    print(f"  IMAGES  : {', '.join(filenames)}")
    print(f"{'='*55}")

    if text.strip() == "":
        print("  ERROR: No text extracted from any image.")
        print("  Try clearer, flatter, better-lit photos.")
        return

    print(f"\n  COMPLIANCE REPORT")
    print(f"  {'─'*50}")

    pass_count = 0
    fail_count = 0
    warn_count = 0

    for field, result in compliance.items():
        status = result['status']
        icon = '✓' if status == 'PASS' else ('!' if status == 'WARNING' else '✗')
        print(f"\n  [{icon}] {field}")
        print(f"       Rule   : {result['rule']}")
        print(f"       Status : {status}")
        print(f"       Found  : {result['found']}")

        if status == 'PASS': pass_count += 1
        elif status == 'FAIL': fail_count += 1
        else: warn_count += 1

    total = pass_count + fail_count
    score = round((pass_count / total) * 100) if total > 0 else 0

    print(f"\n  {'─'*50}")
    print(f"  SUMMARY")
    print(f"  {'─'*50}")
    print(f"  PASSED   : {pass_count}")
    print(f"  FAILED   : {fail_count}")
    print(f"  WARNINGS : {warn_count}")
    print(f"  SCORE    : {score}%")

    if score == 100:
        print(f"  VERDICT  : FULLY COMPLIANT ✓")
    elif score >= 60:
        print(f"  VERDICT  : PARTIALLY COMPLIANT — fix failed fields")
    else:
        print(f"  VERDICT  : NON-COMPLIANT — major violations found")

    print(f"{'='*55}\n")

# ─────────────────────────────────────────────
# STEP 6: MAIN
# ─────────────────────────────────────────────

print("\n" + "="*55)
print("  PACKAGED COMMODITY COMPLIANCE CHECKER")
print("  Legal Metrology (Packaged Commodities) Rules 2011")
print("="*55)

products = group_images()

if not products:
    print("\n  No images found in folder.")
    print(f"  Folder: {folder_path}")
else:
    print(f"\n  Found {len(products)} product(s) to check:\n")
    for product_name, files in products.items():
        print(f"  Processing: {product_name} ({len(files)} image(s))")
        merged_text = extract_merged_text(files)
        compliance = check_compliance(merged_text)
        print_report(product_name, files, merged_text, compliance)