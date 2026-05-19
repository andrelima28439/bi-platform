from datetime import datetime, timedelta
import random
from sqlalchemy import func
from app.database import SessionLocal, init_db
from app.models import Product, Customer, Sale, SaleItem, SaleStatus, CustomerTier

random.seed(42)

init_db()
db = SessionLocal()

existing = db.query(Product).count()
if existing > 0:
    print("Database already has data, skipping seed")
    db.close()
    exit(0)

products_data = [
    {"name": "Notebook Pro", "sku": "NB-001", "category": "Eletrônicos", "unit_price": 4999.00, "cost_price": 3500.00, "stock_quantity": 50},
    {"name": "Mouse Wireless", "sku": "MS-002", "category": "Periféricos", "unit_price": 89.90, "cost_price": 45.00, "stock_quantity": 200},
    {"name": "Teclado Mecânico", "sku": "KB-003", "category": "Periféricos", "unit_price": 249.90, "cost_price": 120.00, "stock_quantity": 150},
    {"name": "Monitor 27\"", "sku": "MN-004", "category": "Eletrônicos", "unit_price": 1899.00, "cost_price": 1200.00, "stock_quantity": 30},
    {"name": "Webcam HD", "sku": "WC-005", "category": "Periféricos", "unit_price": 159.90, "cost_price": 80.00, "stock_quantity": 80},
    {"name": "Headset Gamer", "sku": "HS-006", "category": "Áudio", "unit_price": 299.90, "cost_price": 150.00, "stock_quantity": 100},
    {"name": "SSD 1TB", "sku": "SS-007", "category": "Armazenamento", "unit_price": 549.90, "cost_price": 320.00, "stock_quantity": 3},
    {"name": "Memória RAM 16GB", "sku": "RM-008", "category": "Componentes", "unit_price": 329.90, "cost_price": 180.00, "stock_quantity": 60},
    {"name": "Tablet 10\"", "sku": "TB-009", "category": "Eletrônicos", "unit_price": 2199.00, "cost_price": 1500.00, "stock_quantity": 25},
    {"name": "Impressora Multifuncional", "sku": "IP-010", "category": "Periféricos", "unit_price": 899.00, "cost_price": 550.00, "stock_quantity": 15},
    {"name": "Caixa de Som Bluetooth", "sku": "CS-011", "category": "Áudio", "unit_price": 199.90, "cost_price": 100.00, "stock_quantity": 2},
    {"name": "Hub USB-C", "sku": "HB-012", "category": "Periféricos", "unit_price": 129.90, "cost_price": 60.00, "stock_quantity": 90},
]
products = {}
for p in products_data:
    prod = Product(**p)
    db.add(prod)
    db.flush()
    products[prod.sku] = prod

customers_data = [
    {"name": "João Silva", "email": "joao@email.com", "phone": "(11) 99999-0001", "city": "São Paulo", "state": "SP", "tier": "gold"},
    {"name": "Maria Santos", "email": "maria@email.com", "phone": "(11) 99999-0002", "city": "São Paulo", "state": "SP", "tier": "platinum"},
    {"name": "Pedro Alves", "email": "pedro@email.com", "phone": "(21) 99999-0003", "city": "Rio de Janeiro", "state": "RJ", "tier": "silver"},
    {"name": "Ana Costa", "email": "ana@email.com", "phone": "(31) 99999-0004", "city": "Belo Horizonte", "state": "MG", "tier": "gold"},
    {"name": "Lucas Oliveira", "email": "lucas@email.com", "phone": "(41) 99999-0005", "city": "Curitiba", "state": "PR", "tier": "bronze"},
    {"name": "Carla Souza", "email": "carla@email.com", "phone": "(51) 99999-0006", "city": "Porto Alegre", "state": "RS", "tier": "silver"},
    {"name": "Roberto Lima", "email": "roberto@email.com", "phone": "(61) 99999-0007", "city": "Brasília", "state": "DF", "tier": "gold"},
    {"name": "Fernanda Rocha", "email": "fernanda@email.com", "phone": "(71) 99999-0008", "city": "Salvador", "state": "BA", "tier": "bronze"},
    {"name": "Thiago Martins", "email": "thiago@email.com", "phone": "(81) 99999-0009", "city": "Recife", "state": "PE", "tier": "silver"},
    {"name": "Juliana Pereira", "email": "juliana@email.com", "phone": "(91) 99999-0010", "city": "Belém", "state": "PA", "tier": "bronze"},
    {"name": "Gustavo Nascimento", "email": "gustavo@email.com", "phone": "(85) 99999-0011", "city": "Fortaleza", "state": "CE", "tier": "platinum"},
    {"name": "Patrícia Almeida", "email": "patricia@email.com", "phone": "(48) 99999-0012", "city": "Florianópolis", "state": "SC", "tier": "silver"},
]
customers = []
for c in customers_data:
    cust = Customer(
        name=c["name"], email=c["email"], phone=c["phone"],
        city=c["city"], state=c["state"], tier=c["tier"],
    )
    db.add(cust)
    db.flush()
    customers.append(cust)

payment_methods = ["credit_card", "boleto", "pix", "debit_card"]
now = datetime.utcnow()

invoice_num = 1
for days_ago in range(90, -1, -1):
    sale_date = now - timedelta(days=days_ago)
    num_sales = random.randint(3, 12)
    for _ in range(num_sales):
        customer = random.choice(customers)
        pmt = random.choice(payment_methods)
        num_items = random.randint(1, 5)
        items = random.sample(list(products.values()), min(num_items, len(products)))
        total = 0
        sale_items = []
        for prod in items:
            qty = random.randint(1, 3)
            unit_price = prod.unit_price * random.uniform(0.9, 1.1)
            total_price = round(unit_price * qty, 2)
            total += total_price
            sale_items.append({
                "product_id": prod.id,
                "quantity": qty,
                "unit_price": round(unit_price, 2),
                "total_price": total_price,
            })

        discount = round(total * random.choice([0, 0, 0, 0.05, 0.1, 0.15]), 2)
        tax = round(total * 0.08, 2)
        final = round(total - discount + tax, 2)
        status = random.choices(
            ["completed", "completed", "completed", "completed", "cancelled", "refunded"],
            weights=[40, 40, 10, 5, 3, 2]
        )[0]

        sale = Sale(
            invoice_number=f"INV-{invoice_num:05d}",
            customer_id=customer.id,
            sale_date=sale_date,
            total_amount=round(total, 2),
            discount=discount,
            tax=tax,
            final_amount=final,
            payment_method=pmt,
            status=status,
        )
        db.add(sale)
        db.flush()
        invoice_num += 1

        for si in sale_items:
            db.add(SaleItem(sale_id=sale.id, **si))

for c in customers:
    sales_data = db.query(
        Sale.customer_id,
        func.count(Sale.id).label("total_purchases"),
        func.sum(Sale.final_amount).label("total_spent"),
        func.min(Sale.sale_date).label("first_purchase"),
        func.max(Sale.sale_date).label("last_purchase"),
    ).filter(
        Sale.customer_id == c.id,
        Sale.status == "completed",
    ).group_by(Sale.customer_id).first()

    if sales_data:
        c.total_purchases = int(sales_data.total_purchases)
        c.total_spent = round(float(sales_data.total_spent or 0), 2)
        c.first_purchase_date = sales_data.first_purchase
        c.last_purchase_date = sales_data.last_purchase
        c.is_active = True

        total = c.total_spent
        if total >= 10000:
            c.tier = CustomerTier.PLATINUM.value
        elif total >= 5000:
            c.tier = CustomerTier.GOLD.value
        elif total >= 2000:
            c.tier = CustomerTier.SILVER.value
        else:
            c.tier = CustomerTier.BRONZE.value

db.commit()
db.close()
print(f"Seed complete! Created {len(products)} products, {len(customers)} customers, {invoice_num - 1} sales")
