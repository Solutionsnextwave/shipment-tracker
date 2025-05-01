
CREATE TABLE IF NOT EXISTS po_details (
    id INT AUTO_INCREMENT PRIMARY KEY,
    po_number VARCHAR(20),
    revised_po VARCHAR(20),
    location VARCHAR(100),
    pin_code VARCHAR(10),
    product_1l INT,
    product_900ml INT,
    product_500ml INT,
    product_450ml INT,
    po_date DATE,
    asn VARCHAR(100),
    grn VARCHAR(100),
    payment_status VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS appointment_status (
    id INT AUTO_INCREMENT PRIMARY KEY,
    confirm_date DATE,
    delivery_location VARCHAR(100),
    vendor_name VARCHAR(100),
    brand VARCHAR(50),
    category VARCHAR(50),
    sku_count INT,
    total_po_qty INT,
    po_number VARCHAR(20),
    FOREIGN KEY (po_number) REFERENCES po_details(po_number)
);
